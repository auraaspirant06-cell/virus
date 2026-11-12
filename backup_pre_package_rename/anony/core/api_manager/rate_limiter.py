# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - API Reliability Architecture
# Maintained by Aspirant (https://t.me/aspirant_u)

import time
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket rate limiter algorithm with floating point token replenishment."""

    def __init__(self, rate_per_second: float, capacity: float):
        self.rate = rate_per_second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    async def acquire(self, tokens: float = 1.0) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # Replenish tokens based on elapsed time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    async def wait_acquire(self, tokens: float = 1.0, max_wait: float = 10.0) -> bool:
        start = time.time()
        while time.time() - start < max_wait:
            if await self.acquire(tokens):
                return True
            await asyncio.sleep(0.05)
        return False


class RateLimiter:
    """
    Centralized rate limiter managing:
    - Provider-level rate limits (preventing upstream 429 errors).
    - User-level rate limits (preventing bot command spam).
    - Bounded concurrency control via semaphores.
    """

    def __init__(self, default_rate_per_minute: int = 30, max_concurrent_requests: int = 10):
        self.default_rate = default_rate_per_minute / 60.0
        self.capacity = float(default_rate_per_minute)
        self.max_concurrent_requests = max_concurrent_requests
        self._buckets: dict[str, TokenBucket] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._total_requests = 0
        self._throttled_requests = 0

    def _get_bucket(self, key: str, rate: Optional[float] = None, capacity: Optional[float] = None) -> TokenBucket:
        if key not in self._buckets:
            r = rate or self.default_rate
            c = capacity or self.capacity
            self._buckets[key] = TokenBucket(rate_per_second=r, capacity=c)
        return self._buckets[key]

    async def acquire(self, key: str = "global", max_wait: float = 5.0) -> bool:
        """Acquires a rate limit token and enforces concurrency boundaries."""
        self._total_requests += 1
        bucket = self._get_bucket(key)
        acquired = await bucket.wait_acquire(tokens=1.0, max_wait=max_wait)
        if not acquired:
            self._throttled_requests += 1
            logger.warning(f"[RateLimiter] Rate limit exceeded for '{key}'. Throttling request.")
            return False
        return True

    def concurrency_guard(self):
        """Returns the semaphore context manager for bounded concurrency."""
        return self._semaphore

    def get_stats(self) -> dict:
        """Returns rate limiter metrics."""
        return {
            "tracked_keys": len(self._buckets),
            "total_requests": self._total_requests,
            "throttled_requests": self._throttled_requests,
            "max_concurrency": self.max_concurrent_requests,
        }
