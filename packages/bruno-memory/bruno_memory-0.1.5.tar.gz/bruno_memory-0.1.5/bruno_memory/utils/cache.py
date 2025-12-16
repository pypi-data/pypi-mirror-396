"""
Cache implementations for bruno-memory.

Provides multi-level caching with LRU eviction, Redis integration,
and automatic TTL management.
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from bruno_memory.exceptions import CacheError

logger = logging.getLogger(__name__)


class CacheInterface(ABC):
    """Abstract interface for cache implementations."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries."""
        pass

    @abstractmethod
    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache."""
        pass

    @abstractmethod
    async def set_many(self, items: dict[str, Any], ttl: int | None = None) -> None:
        """Set multiple values in cache."""
        pass

    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        pass


class InMemoryCache(CacheInterface):
    """
    In-memory LRU cache with TTL support.

    Features:
    - LRU eviction policy
    - TTL-based expiration
    - Thread-safe operations
    - Automatic cleanup of expired entries
    """

    def __init__(
        self, max_size: int = 1000, default_ttl: int | None = 3600, cleanup_interval: int = 60
    ):
        """
        Initialize in-memory cache.

        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds (None = no expiration)
            cleanup_interval: Interval for cleanup task in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, tuple[Any, float | None]] = OrderedDict()
        self._lock = asyncio.Lock()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._expirations = 0

        # Start cleanup task
        self._cleanup_task: asyncio.Task | None = None
        self._cleanup_interval = cleanup_interval
        self._running = False

    async def start(self) -> None:
        """Start background cleanup task."""
        if not self._running:
            self._running = True
            self._cleanup_task = asyncio.create_task(self._cleanup_expired())
            logger.info("InMemoryCache cleanup task started")

    async def stop(self) -> None:
        """Stop background cleanup task."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("InMemoryCache cleanup task stopped")

    async def _cleanup_expired(self) -> None:
        """Background task to remove expired entries."""
        while self._running:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._remove_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    async def _remove_expired(self) -> None:
        """Remove all expired entries."""
        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, (_, expiry) in self._cache.items()
                if expiry is not None and expiry < current_time
            ]

            for key in expired_keys:
                del self._cache[key]
                self._expirations += 1

            if expired_keys:
                logger.debug(f"Removed {len(expired_keys)} expired entries")

    def _is_expired(self, expiry: float | None) -> bool:
        """Check if entry is expired."""
        if expiry is None:
            return False
        return expiry < time.time()

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        async with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, expiry = self._cache[key]

            # Check expiration
            if self._is_expired(expiry):
                del self._cache[key]
                self._expirations += 1
                self._misses += 1
                return None

            # Move to end (mark as recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with optional TTL."""
        async with self._lock:
            # Calculate expiry time
            if ttl is None:
                ttl = self.default_ttl

            expiry = None if ttl is None else time.time() + ttl

            # Update or add entry
            if key in self._cache:
                del self._cache[key]

            self._cache[key] = (value, expiry)
            self._cache.move_to_end(key)

            # Evict oldest if over capacity
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._evictions += 1

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        async with self._lock:
            if key not in self._cache:
                return False

            _, expiry = self._cache[key]
            if self._is_expired(expiry):
                del self._cache[key]
                self._expirations += 1
                return False

            return True

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache."""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result

    async def set_many(self, items: dict[str, Any], ttl: int | None = None) -> None:
        """Set multiple values in cache."""
        for key, value in items.items():
            await self.set(key, value, ttl)

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0

            return {
                "type": "in_memory",
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2),
                "evictions": self._evictions,
                "expirations": self._expirations,
            }


class RedisCache(CacheInterface):
    """
    Redis-based cache implementation.

    Features:
    - Distributed caching
    - Automatic TTL management
    - Connection pooling
    - Batch operations
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        prefix: str = "bruno:cache:",
        default_ttl: int | None = 3600,
        max_connections: int = 10,
    ):
        """
        Initialize Redis cache.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            prefix: Key prefix for namespacing
            default_ttl: Default TTL in seconds
            max_connections: Maximum connections in pool
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis package is required for RedisCache")

        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.prefix = prefix
        self.default_ttl = default_ttl
        self.max_connections = max_connections

        self._client: aioredis.Redis | None = None
        self._connected = False

        # Statistics (approximate, stored in Redis)
        self._stats_key = f"{prefix}stats"

    async def connect(self) -> None:
        """Connect to Redis."""
        if self._connected:
            return

        try:
            self._client = await aioredis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                password=self.password,
                max_connections=self.max_connections,
                decode_responses=False,
            )

            # Test connection
            await self._client.ping()
            self._connected = True
            logger.info(f"Connected to Redis at {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise CacheError(f"Redis connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._connected = False
            logger.info("Disconnected from Redis")

    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        return f"{self.prefix}{key}"

    async def _increment_stat(self, stat: str) -> None:
        """Increment statistics counter."""
        try:
            await self._client.hincrby(self._stats_key, stat, 1)
        except Exception:
            pass  # Don't fail on stats

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if not self._connected:
            await self.connect()

        try:
            redis_key = self._make_key(key)
            value = await self._client.get(redis_key)

            if value is None:
                await self._increment_stat("misses")
                return None

            await self._increment_stat("hits")
            return json.loads(value)

        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with optional TTL."""
        if not self._connected:
            await self.connect()

        try:
            redis_key = self._make_key(key)
            serialized = json.dumps(value)

            if ttl is None:
                ttl = self.default_ttl

            if ttl:
                await self._client.setex(redis_key, ttl, serialized)
            else:
                await self._client.set(redis_key, serialized)

        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            raise CacheError(f"Failed to set cache key: {e}")

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._connected:
            await self.connect()

        try:
            redis_key = self._make_key(key)
            result = await self._client.delete(redis_key)
            return result > 0

        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._connected:
            await self.connect()

        try:
            redis_key = self._make_key(key)
            return await self._client.exists(redis_key) > 0

        except Exception as e:
            logger.error(f"Error checking key {key}: {e}")
            return False

    async def clear(self) -> None:
        """Clear all cache entries with prefix."""
        if not self._connected:
            await self.connect()

        try:
            # Scan for all keys with prefix
            cursor = 0
            pattern = f"{self.prefix}*"

            while True:
                cursor, keys = await self._client.scan(cursor, match=pattern, count=100)

                if keys:
                    await self._client.delete(*keys)

                if cursor == 0:
                    break

            logger.info("Redis cache cleared")

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            raise CacheError(f"Failed to clear cache: {e}")

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache."""
        if not self._connected:
            await self.connect()

        try:
            redis_keys = [self._make_key(k) for k in keys]
            values = await self._client.mget(redis_keys)

            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = json.loads(value)
                    await self._increment_stat("hits")
                else:
                    await self._increment_stat("misses")

            return result

        except Exception as e:
            logger.error(f"Error getting multiple keys: {e}")
            return {}

    async def set_many(self, items: dict[str, Any], ttl: int | None = None) -> None:
        """Set multiple values in cache."""
        if not self._connected:
            await self.connect()

        try:
            pipe = self._client.pipeline()

            for key, value in items.items():
                redis_key = self._make_key(key)
                serialized = json.dumps(value)

                if ttl is None:
                    ttl = self.default_ttl

                if ttl:
                    pipe.setex(redis_key, ttl, serialized)
                else:
                    pipe.set(redis_key, serialized)

            await pipe.execute()

        except Exception as e:
            logger.error(f"Error setting multiple keys: {e}")
            raise CacheError(f"Failed to set multiple keys: {e}")

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        if not self._connected:
            await self.connect()

        try:
            stats = await self._client.hgetall(self._stats_key)
            hits = int(stats.get(b"hits", 0))
            misses = int(stats.get(b"misses", 0))
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0.0

            # Get approximate size
            cursor = 0
            pattern = f"{self.prefix}*"
            size = 0

            while True:
                cursor, keys = await self._client.scan(cursor, match=pattern, count=100)
                size += len(keys)

                if cursor == 0:
                    break

            return {
                "type": "redis",
                "size": size,
                "hits": hits,
                "misses": misses,
                "hit_rate": round(hit_rate, 2),
                "connected": self._connected,
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"type": "redis", "error": str(e)}


class MultiLevelCache(CacheInterface):
    """
    Multi-level cache with L1 (in-memory) and L2 (Redis) tiers.

    Features:
    - Automatic promotion to L1 on access
    - Write-through to both levels
    - Fallback to L2 on L1 miss
    - Combined statistics
    """

    def __init__(
        self,
        l1_cache: InMemoryCache,
        l2_cache: RedisCache | None = None,
        promote_on_hit: bool = True,
    ):
        """
        Initialize multi-level cache.

        Args:
            l1_cache: L1 (in-memory) cache
            l2_cache: L2 (Redis) cache (optional)
            promote_on_hit: Promote L2 hits to L1
        """
        self.l1 = l1_cache
        self.l2 = l2_cache
        self.promote_on_hit = promote_on_hit

        logger.info(f"MultiLevelCache initialized (L2: {l2_cache is not None})")

    async def start(self) -> None:
        """Start cache layers."""
        await self.l1.start()
        if self.l2:
            await self.l2.connect()

    async def stop(self) -> None:
        """Stop cache layers."""
        await self.l1.stop()
        if self.l2:
            await self.l2.disconnect()

    async def get(self, key: str) -> Any | None:
        """Get value from cache (L1 -> L2)."""
        # Try L1 first
        value = await self.l1.get(key)
        if value is not None:
            return value

        # Try L2 if available
        if self.l2:
            value = await self.l2.get(key)
            if value is not None and self.promote_on_hit:
                # Promote to L1
                await self.l1.set(key, value)
            return value

        return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in both cache levels."""
        await self.l1.set(key, value, ttl)
        if self.l2:
            await self.l2.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """Delete key from both cache levels."""
        l1_result = await self.l1.delete(key)
        l2_result = await self.l2.delete(key) if self.l2 else False
        return l1_result or l2_result

    async def exists(self, key: str) -> bool:
        """Check if key exists in any cache level."""
        if await self.l1.exists(key):
            return True
        if self.l2 and await self.l2.exists(key):
            return True
        return False

    async def clear(self) -> None:
        """Clear all cache levels."""
        await self.l1.clear()
        if self.l2:
            await self.l2.clear()

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache."""
        # Try L1 first
        result = await self.l1.get_many(keys)

        # Find missing keys
        if self.l2:
            missing_keys = [k for k in keys if k not in result]
            if missing_keys:
                l2_results = await self.l2.get_many(missing_keys)
                result.update(l2_results)

                # Promote to L1
                if self.promote_on_hit and l2_results:
                    await self.l1.set_many(l2_results)

        return result

    async def set_many(self, items: dict[str, Any], ttl: int | None = None) -> None:
        """Set multiple values in both cache levels."""
        await self.l1.set_many(items, ttl)
        if self.l2:
            await self.l2.set_many(items, ttl)

    async def get_stats(self) -> dict[str, Any]:
        """Get combined cache statistics."""
        l1_stats = await self.l1.get_stats()

        stats = {
            "type": "multi_level",
            "l1": l1_stats,
        }

        if self.l2:
            l2_stats = await self.l2.get_stats()
            stats["l2"] = l2_stats

        return stats
