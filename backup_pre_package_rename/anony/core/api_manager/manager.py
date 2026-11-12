# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - API Reliability Architecture
# Maintained by Aspirant (https://t.me/aspirant_u)

import time
import random
import asyncio
import logging
from typing import Optional, List as TList

from config import Config
from anony.helpers._dataclass import Track
from .circuit_breaker import CircuitBreaker, CircuitState
from .cache import CacheManager
from .rate_limiter import RateLimiter
from .providers import BaseMusicProvider, PyYTSearchProvider, DirectYTHtmlProvider

logger = logging.getLogger(__name__)


class APIManager:
    """
    Centralized API Reliability Manager for VIRUS MUSIC BOT.
    Coordinates:
    - Provider fallback chains
    - Intelligent caching (memory + optional Redis)
    - Circuit breaking per provider
    - Exponential backoff retries with random jitter
    - Rate limiting & bounded concurrency
    - Health monitoring & telemetry dashboard
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.timeout = getattr(self.config, "API_TIMEOUT", 15)
        self.max_retries = getattr(self.config, "API_MAX_RETRIES", 3)
        self.retry_backoff = getattr(self.config, "API_RETRY_BACKOFF", 1.5)
        self.cache_ttl = getattr(self.config, "API_CACHE_TTL", 3600)
        self.rate_limit_per_min = getattr(self.config, "RATE_LIMIT_PER_MINUTE", 30)
        self.fail_threshold = getattr(self.config, "CIRCUIT_BREAKER_FAIL_THRESHOLD", 5)
        self.reset_timeout = getattr(self.config, "CIRCUIT_BREAKER_RESET_TIMEOUT", 60)

        # Core Components
        self.cache = CacheManager(
            default_ttl=self.cache_ttl,
            redis_url=getattr(self.config, "REDIS_URL", None)
        )
        self.rate_limiter = RateLimiter(
            default_rate_per_minute=self.rate_limit_per_min,
            max_concurrent_requests=10
        )

        # Registered Providers & Circuit Breakers
        self.providers: list[BaseMusicProvider] = []
        self.circuit_breakers: dict[str, CircuitBreaker] = {}

        # Default providers registered in priority order
        self.register_provider(PyYTSearchProvider(priority=1))
        self.register_provider(DirectYTHtmlProvider(priority=2))

    def register_provider(self, provider: BaseMusicProvider):
        """Registers a provider and initializes its dedicated circuit breaker."""
        self.providers.append(provider)
        self.providers.sort(key=lambda p: p.priority)
        self.circuit_breakers[provider.name] = CircuitBreaker(
            name=provider.name,
            failure_threshold=self.fail_threshold,
            recovery_timeout=float(self.reset_timeout),
        )
        logger.info(f"[APIManager] Registered provider: {provider.name} (Priority {provider.priority})")

    async def initialize(self):
        """Initializes async cache connections."""
        await self.cache.initialize()

    async def execute_with_retry(self, func, *args, **kwargs):
        """
        Executes an async callable with exponential backoff and random jitter.
        Applies timeout management and catches network / transient errors.
        """
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                # Enforce timeout guard
                return await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout)
            except asyncio.TimeoutError as ex:
                last_error = ex
                logger.warning(f"[APIManager] Attempt {attempt}/{self.max_retries} timed out after {self.timeout}s.")
            except Exception as ex:
                last_error = ex
                logger.warning(f"[APIManager] Attempt {attempt}/{self.max_retries} failed: {ex}")

            if attempt < self.max_retries:
                # Exponential backoff with random jitter: (base * backoff^attempt) + random(0, 0.5)
                delay = (self.retry_backoff ** attempt) + random.uniform(0.1, 0.5)
                logger.debug(f"[APIManager] Waiting {delay:.2f}s before retry {attempt + 1}...")
                await asyncio.sleep(delay)

        raise last_error

    async def search(self, query: str, video: bool = False, limit: int = 1) -> TList[Track]:
        """
        High-reliability music search pipeline:
        1. Checks cache for existing metadata.
        2. Acquires rate limit token and enters bounded concurrency.
        3. Tries providers in priority order, respecting circuit breaker states.
        4. Applies exponential backoff on transient errors.
        5. Caches successful result and updates circuit metrics.
        """
        clean_query = query.strip()
        cache_key = f"search:{'v:' if video else 'a:'}:{clean_query.lower()}:{limit}"

        # 1. Cache Check
        cached = await self.cache.get(cache_key)
        if cached:
            try:
                tracks = [Track(**item) for item in cached]
                logger.debug(f"[APIManager] Cache HIT for query: '{clean_query}'")
                return tracks
            except Exception:
                pass

        # 2. Rate Limiter & Concurrency Check
        acquired = await self.rate_limiter.acquire(key="search", max_wait=3.0)
        if not acquired:
            logger.warning(f"[APIManager] Concurrency/rate limit delayed query: '{clean_query}'")

        # 3. Provider Fallback Pipeline
        async with self.rate_limiter.concurrency_guard():
            for provider in self.providers:
                cb = self.circuit_breakers.get(provider.name)
                if cb and not cb.can_execute():
                    logger.warning(f"[APIManager] Skipping provider {provider.name} (Circuit State: {cb.state.value})")
                    continue

                start_time = time.time()
                try:
                    # Execute provider with smart retry
                    tracks = await self.execute_with_retry(provider.search, clean_query, video, limit)
                    latency = (time.time() - start_time) * 1000

                    if tracks:
                        if cb:
                            cb.record_success()
                        provider.record_metrics(success=True, latency_ms=latency)

                        # 4. Cache successful result
                        serialized = [t.__dict__ for t in tracks]
                        await self.cache.set(cache_key, serialized, ttl=self.cache_ttl)
                        logger.info(f"[APIManager] Search succeeded via {provider.name} in {latency:.1f}ms")
                        return tracks
                    else:
                        # Empty results are treated as soft misses
                        if cb:
                            cb.record_success()
                        provider.record_metrics(success=True, latency_ms=latency)
                except Exception as ex:
                    latency = (time.time() - start_time) * 1000
                    if cb:
                        cb.record_failure()
                    provider.record_metrics(success=False, latency_ms=latency)
                    logger.error(f"[APIManager] Provider {provider.name} failed: {ex}. Falling back to next provider...")

        logger.warning(f"[APIManager] All search providers failed or returned empty for query: '{clean_query}'")
        return []

    async def get_health_dashboard(self) -> dict:
        """Returns structured observability telemetry for bot status."""
        provider_stats = [p.get_stats() for p in self.providers]
        circuit_stats = [cb.get_status() for cb in self.circuit_breakers.values()]
        cache_stats = self.cache.get_stats()
        limiter_stats = self.rate_limiter.get_stats()

        return {
            "status": "OPERATIONAL",
            "providers": provider_stats,
            "circuits": circuit_stats,
            "cache": cache_stats,
            "rate_limiter": limiter_stats,
            "config": {
                "timeout": self.timeout,
                "max_retries": self.max_retries,
                "cache_ttl": self.cache_ttl,
                "fail_threshold": self.fail_threshold,
            }
        }
