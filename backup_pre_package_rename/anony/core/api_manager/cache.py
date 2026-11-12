# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - API Reliability Architecture
# Maintained by Aspirant (https://t.me/aspirant_u)

import time
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Intelligent caching manager supporting:
    - High performance in-memory TTL cache with automatic expiration.
    - Optional Redis integration when REDIS_URL is provided in configuration.
    - Graceful fallback: If Redis is unavailable or disconnected, the system seamlessly
      operates using the built-in memory cache without breaking any music services.
    """

    def __init__(self, default_ttl: int = 3600, redis_url: Optional[str] = None):
        self.default_ttl = default_ttl
        self.redis_url = redis_url
        self._memory_cache: dict[str, tuple[Any, float]] = {}
        self._hits = 0
        self._misses = 0
        self._redis = None
        self._has_redis = False

    async def initialize(self):
        """Initializes optional Redis client if configured."""
        if self.redis_url:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=3.0,
                    socket_timeout=3.0,
                )
                await self._redis.ping()
                self._has_redis = True
                logger.info("[CacheManager] Connected to Redis cache backend.")
            except Exception as ex:
                self._has_redis = False
                logger.warning(f"[CacheManager] Redis connection unavailable ({ex}). Operating in memory-only mode.")

    async def get(self, key: str) -> Optional[Any]:
        """Retrieves an item from Redis or in-memory cache."""
        now = time.time()

        # 1. Try Redis if enabled
        if self._has_redis and self._redis:
            try:
                val = await self._redis.get(key)
                if val is not None:
                    self._hits += 1
                    try:
                        return json.loads(val)
                    except Exception:
                        return val
            except Exception as ex:
                logger.debug(f"[CacheManager] Redis get error: {ex}. Falling back to memory.")

        # 2. In-memory cache fallback
        if key in self._memory_cache:
            value, expires_at = self._memory_cache[key]
            if expires_at > now:
                self._hits += 1
                return value
            else:
                del self._memory_cache[key]

        self._misses += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Stores an item in cache with TTL."""
        expiry = ttl or self.default_ttl
        now = time.time()

        # 1. Try Redis if enabled
        if self._has_redis and self._redis:
            try:
                serialized = json.dumps(value) if not isinstance(value, str) else value
                await self._redis.set(key, serialized, ex=expiry)
            except Exception as ex:
                logger.debug(f"[CacheManager] Redis set error: {ex}. Storing in memory.")

        # 2. Always store in memory for fast local access and resilience
        self._memory_cache[key] = (value, now + expiry)
        self._prune_memory_if_needed()
        return True

    async def delete(self, key: str) -> bool:
        """Deletes a key from cache."""
        self._memory_cache.pop(key, None)
        if self._has_redis and self._redis:
            try:
                await self._redis.delete(key)
            except Exception:
                pass
        return True

    async def clear(self):
        """Clears memory cache."""
        self._memory_cache.clear()

    def _prune_memory_if_needed(self, max_items: int = 5000):
        """Removes expired entries and limits memory cache footprint."""
        now = time.time()
        if len(self._memory_cache) > max_items:
            # Remove expired
            expired = [k for k, (_, exp) in self._memory_cache.items() if exp <= now]
            for k in expired:
                del self._memory_cache[k]
            # If still over limit, trim oldest items
            if len(self._memory_cache) > max_items:
                keys_to_remove = list(self._memory_cache.keys())[: max_items // 4]
                for k in keys_to_remove:
                    del self._memory_cache[k]

    def get_stats(self) -> dict:
        """Returns cache telemetry."""
        total = self._hits + self._misses
        hit_ratio = round((self._hits / total * 100), 1) if total > 0 else 0.0
        return {
            "backend": "Redis + Memory" if self._has_redis else "In-Memory Only",
            "memory_items": len(self._memory_cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_ratio_percent": hit_ratio,
        }
