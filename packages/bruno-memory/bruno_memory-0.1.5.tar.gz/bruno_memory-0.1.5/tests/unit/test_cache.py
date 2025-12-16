"""Tests for cache implementations."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bruno_memory.utils.cache import (
    InMemoryCache,
    MultiLevelCache,
    RedisCache,
)


class TestInMemoryCache:
    """Tests for InMemoryCache."""

    @pytest.fixture
    async def cache(self):
        """Create cache instance."""
        cache = InMemoryCache(max_size=10, default_ttl=None)
        await cache.start()
        yield cache
        await cache.stop()

    @pytest.mark.asyncio
    async def test_basic_get_set(self, cache):
        """Test basic get/set operations."""
        await cache.set("key1", "value1")
        value = await cache.get("key1")
        assert value == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache):
        """Test getting non-existent key returns None."""
        value = await cache.get("nonexistent")
        assert value is None

    @pytest.mark.asyncio
    async def test_set_with_ttl(self, cache):
        """Test TTL expiration."""
        await cache.set("expiring", "value", ttl=1)

        # Should exist immediately
        value = await cache.get("expiring")
        assert value == "value"

        # Wait for expiration
        await asyncio.sleep(1.1)
        value = await cache.get("expiring")
        assert value is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache):
        """Test LRU eviction when max_size exceeded."""
        # Fill cache to capacity
        for i in range(10):
            await cache.set(f"key{i}", f"value{i}")

        # Add one more - should evict oldest
        await cache.set("key10", "value10")

        # First key should be evicted
        assert await cache.get("key0") is None

        # Others should exist
        assert await cache.get("key1") is not None
        assert await cache.get("key10") is not None

    @pytest.mark.asyncio
    async def test_lru_access_order(self, cache):
        """Test LRU maintains access order."""
        # Fill cache
        for i in range(10):
            await cache.set(f"key{i}", f"value{i}")

        # Access key0 to make it recently used
        await cache.get("key0")

        # Add new key - should evict key1 (now oldest)
        await cache.set("key10", "value10")

        assert await cache.get("key0") is not None  # Still exists
        assert await cache.get("key1") is None  # Evicted

    @pytest.mark.asyncio
    async def test_delete(self, cache):
        """Test delete operation."""
        await cache.set("key1", "value1")

        result = await cache.delete("key1")
        assert result is True
        assert await cache.get("key1") is None

        # Delete non-existent
        result = await cache.delete("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists(self, cache):
        """Test exists operation."""
        await cache.set("key1", "value1")

        assert await cache.exists("key1") is True
        assert await cache.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_clear(self, cache):
        """Test clear operation."""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")

        await cache.clear()

        assert await cache.get("key1") is None
        assert await cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_get_many(self, cache):
        """Test batch get operation."""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")

        result = await cache.get_many(["key1", "key2", "nonexistent"])

        assert result == {"key1": "value1", "key2": "value2"}

    @pytest.mark.asyncio
    async def test_set_many(self, cache):
        """Test batch set operation."""
        items = {"key1": "value1", "key2": "value2", "key3": "value3"}
        await cache.set_many(items)

        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_statistics(self, cache):
        """Test cache statistics."""
        # Generate some hits and misses
        await cache.set("key1", "value1")
        await cache.get("key1")  # Hit
        await cache.get("nonexistent")  # Miss
        await cache.get("key1")  # Hit

        stats = await cache.get_stats()

        assert stats["type"] == "in_memory"
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] > 0
        assert stats["size"] == 1

    @pytest.mark.asyncio
    async def test_expired_cleanup(self):
        """Test automatic cleanup of expired entries."""
        cache = InMemoryCache(max_size=10, default_ttl=1, cleanup_interval=1)
        await cache.start()

        try:
            # Add entries that will expire
            await cache.set("exp1", "value1", ttl=1)
            await cache.set("exp2", "value2", ttl=1)

            # Wait for expiration and cleanup
            await asyncio.sleep(2)

            stats = await cache.get_stats()
            assert stats["expirations"] >= 2

        finally:
            await cache.stop()

    @pytest.mark.asyncio
    async def test_update_existing_key(self, cache):
        """Test updating existing key."""
        await cache.set("key1", "value1")
        await cache.set("key1", "value2")

        value = await cache.get("key1")
        assert value == "value2"

    @pytest.mark.asyncio
    async def test_complex_values(self, cache):
        """Test caching complex data types."""
        complex_value = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "number": 42,
            "boolean": True,
        }

        await cache.set("complex", complex_value)
        value = await cache.get("complex")

        assert value == complex_value


class TestRedisCache:
    """Tests for RedisCache."""

    @pytest.fixture
    async def mock_redis(self):
        """Mock Redis client."""
        with patch("bruno_memory.utils.cache.aioredis") as mock:
            redis_instance = AsyncMock()
            redis_instance.ping = AsyncMock()
            redis_instance.get = AsyncMock(return_value=None)
            redis_instance.set = AsyncMock()
            redis_instance.setex = AsyncMock()
            redis_instance.delete = AsyncMock(return_value=1)
            redis_instance.exists = AsyncMock(return_value=1)
            redis_instance.mget = AsyncMock(return_value=[])
            redis_instance.pipeline = MagicMock()
            redis_instance.scan = AsyncMock(return_value=(0, []))
            redis_instance.hgetall = AsyncMock(return_value={})
            redis_instance.hincrby = AsyncMock()
            redis_instance.close = AsyncMock()

            mock.from_url = AsyncMock(return_value=redis_instance)

            yield redis_instance

    @pytest.mark.asyncio
    async def test_redis_available(self):
        """Test Redis availability check."""
        from bruno_memory.utils.cache import REDIS_AVAILABLE

        # Just verify the import check works
        assert isinstance(REDIS_AVAILABLE, bool)

    @pytest.mark.asyncio
    async def test_connect(self, mock_redis):
        """Test Redis connection."""
        cache = RedisCache()
        await cache.connect()

        assert cache._connected is True
        mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_set(self, mock_redis):
        """Test basic get/set operations."""
        import json

        cache = RedisCache()
        await cache.connect()

        # Test set
        await cache.set("key1", "value1")
        mock_redis.setex.assert_called_once()

        # Test get
        mock_redis.get.return_value = json.dumps("value1")
        value = await cache.get("key1")
        assert value == "value1"

    @pytest.mark.asyncio
    async def test_get_miss(self, mock_redis):
        """Test cache miss."""
        cache = RedisCache()
        await cache.connect()

        mock_redis.get.return_value = None
        value = await cache.get("nonexistent")

        assert value is None

    @pytest.mark.asyncio
    async def test_delete(self, mock_redis):
        """Test delete operation."""
        cache = RedisCache()
        await cache.connect()

        result = await cache.delete("key1")
        assert result is True
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_exists(self, mock_redis):
        """Test exists operation."""
        cache = RedisCache()
        await cache.connect()

        mock_redis.exists.return_value = 1
        assert await cache.exists("key1") is True

        mock_redis.exists.return_value = 0
        assert await cache.exists("key2") is False

    @pytest.mark.asyncio
    async def test_clear(self, mock_redis):
        """Test clear operation."""
        cache = RedisCache(prefix="test:")
        await cache.connect()

        mock_redis.scan.return_value = (0, [b"test:key1", b"test:key2"])

        await cache.clear()

        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_many(self, mock_redis):
        """Test batch get operation."""
        import json

        cache = RedisCache()
        await cache.connect()

        mock_redis.mget.return_value = [json.dumps("value1"), json.dumps("value2"), None]

        result = await cache.get_many(["key1", "key2", "key3"])

        assert result == {"key1": "value1", "key2": "value2"}

    @pytest.mark.asyncio
    async def test_set_many(self, mock_redis):
        """Test batch set operation."""
        cache = RedisCache()
        await cache.connect()

        pipe = AsyncMock()
        mock_redis.pipeline.return_value = pipe
        pipe.execute = AsyncMock()

        items = {"key1": "value1", "key2": "value2"}
        await cache.set_many(items)

        pipe.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_prefix_namespacing(self, mock_redis):
        """Test key prefixing."""
        cache = RedisCache(prefix="myapp:")
        await cache.connect()

        await cache.set("key1", "value1")

        # Verify the key was prefixed
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "myapp:key1"


class TestMultiLevelCache:
    """Tests for MultiLevelCache."""

    @pytest.fixture
    async def l1_cache(self):
        """Create L1 cache."""
        cache = InMemoryCache(max_size=5, default_ttl=None)
        await cache.start()
        yield cache
        await cache.stop()

    @pytest.fixture
    async def l2_cache(self):
        """Create mocked L2 cache."""
        cache = AsyncMock(spec=RedisCache)
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        cache.delete = AsyncMock(return_value=False)
        cache.exists = AsyncMock(return_value=False)
        cache.clear = AsyncMock()
        cache.get_many = AsyncMock(return_value={})
        cache.set_many = AsyncMock()
        cache.get_stats = AsyncMock(return_value={"type": "redis"})
        cache.connect = AsyncMock()
        cache.disconnect = AsyncMock()
        return cache

    @pytest.fixture
    async def multi_cache(self, l1_cache, l2_cache):
        """Create multi-level cache."""
        cache = MultiLevelCache(l1_cache, l2_cache)
        await cache.start()
        yield cache
        await cache.stop()

    @pytest.mark.asyncio
    async def test_l1_hit(self, multi_cache, l1_cache, l2_cache):
        """Test L1 cache hit."""
        await multi_cache.set("key1", "value1")

        value = await multi_cache.get("key1")

        assert value == "value1"
        # L2 get should not be called (L1 hit)
        l2_cache.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_l2_hit_promotion(self, multi_cache, l1_cache, l2_cache):
        """Test L2 hit promotes to L1."""
        # Setup L2 to return value
        l2_cache.get.return_value = "value_from_l2"

        # Get should check L1, miss, then L2, then promote
        value = await multi_cache.get("key1")

        assert value == "value_from_l2"
        l2_cache.get.assert_called_once_with("key1")

        # Verify promotion to L1
        l1_value = await l1_cache.get("key1")
        assert l1_value == "value_from_l2"

    @pytest.mark.asyncio
    async def test_write_through(self, multi_cache, l1_cache, l2_cache):
        """Test writes go to both levels."""
        await multi_cache.set("key1", "value1")

        # Both caches should have been written
        assert await l1_cache.get("key1") == "value1"
        l2_cache.set.assert_called_once_with("key1", "value1", None)

    @pytest.mark.asyncio
    async def test_delete_both_levels(self, multi_cache, l1_cache, l2_cache):
        """Test delete removes from both levels."""
        await multi_cache.set("key1", "value1")
        await multi_cache.delete("key1")

        assert await l1_cache.get("key1") is None
        l2_cache.delete.assert_called_once_with("key1")

    @pytest.mark.asyncio
    async def test_exists_checks_both(self, multi_cache, l1_cache, l2_cache):
        """Test exists checks both levels."""
        await l1_cache.set("key1", "value1")

        result = await multi_cache.exists("key1")
        assert result is True

        # L2 should not be checked if found in L1
        l2_cache.exists.assert_not_called()

    @pytest.mark.asyncio
    async def test_clear_both_levels(self, multi_cache, l1_cache, l2_cache):
        """Test clear affects both levels."""
        await multi_cache.set("key1", "value1")
        await multi_cache.clear()

        assert await l1_cache.get("key1") is None
        l2_cache.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_many_fallback(self, multi_cache, l1_cache, l2_cache):
        """Test get_many with L1/L2 fallback."""
        # Put some in L1
        await l1_cache.set("key1", "value1")

        # Setup L2 to have others
        l2_cache.get_many.return_value = {"key2": "value2", "key3": "value3"}

        result = await multi_cache.get_many(["key1", "key2", "key3"])

        assert result == {"key1": "value1", "key2": "value2", "key3": "value3"}

    @pytest.mark.asyncio
    async def test_combined_stats(self, multi_cache, l1_cache, l2_cache):
        """Test statistics from both levels."""
        stats = await multi_cache.get_stats()

        assert stats["type"] == "multi_level"
        assert "l1" in stats
        assert "l2" in stats
        assert stats["l1"]["type"] == "in_memory"
        assert stats["l2"]["type"] == "redis"

    @pytest.mark.asyncio
    async def test_no_l2_cache(self, l1_cache):
        """Test multi-level cache with only L1."""
        cache = MultiLevelCache(l1_cache, None)
        await cache.start()

        try:
            await cache.set("key1", "value1")
            value = await cache.get("key1")

            assert value == "value1"

            stats = await cache.get_stats()
            assert "l2" not in stats

        finally:
            await cache.stop()


class TestCachePerformance:
    """Performance tests for cache implementations."""

    @pytest.mark.asyncio
    async def test_high_volume_operations(self):
        """Test cache with high volume of operations."""
        cache = InMemoryCache(max_size=1000, default_ttl=None)
        await cache.start()

        try:
            # Write many entries
            start = time.time()
            for i in range(1000):
                await cache.set(f"key{i}", f"value{i}")
            write_time = time.time() - start

            # Read many entries
            start = time.time()
            for i in range(1000):
                await cache.get(f"key{i}")
            read_time = time.time() - start

            # Should be fast
            assert write_time < 1.0  # 1000 writes in < 1 second
            assert read_time < 1.0  # 1000 reads in < 1 second

            stats = await cache.get_stats()
            assert stats["hits"] == 1000
            assert stats["hit_rate"] == 100.0

        finally:
            await cache.stop()

    @pytest.mark.asyncio
    async def test_batch_operations_performance(self):
        """Test performance of batch operations."""
        cache = InMemoryCache(max_size=1000, default_ttl=None)
        await cache.start()

        try:
            # Batch write
            items = {f"key{i}": f"value{i}" for i in range(100)}

            start = time.time()
            await cache.set_many(items)
            batch_write_time = time.time() - start

            # Batch read
            keys = list(items.keys())
            start = time.time()
            result = await cache.get_many(keys)
            batch_read_time = time.time() - start

            assert len(result) == 100
            assert batch_write_time < 0.5
            assert batch_read_time < 0.5

        finally:
            await cache.stop()

    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """Test concurrent access to cache."""
        cache = InMemoryCache(max_size=100, default_ttl=None)
        await cache.start()

        try:

            async def worker(worker_id: int):
                for i in range(10):
                    await cache.set(f"worker{worker_id}_key{i}", f"value{i}")
                    await cache.get(f"worker{worker_id}_key{i}")

            # Run multiple workers concurrently
            tasks = [worker(i) for i in range(10)]
            await asyncio.gather(*tasks)

            stats = await cache.get_stats()
            assert stats["hits"] == 100  # 10 workers × 10 reads

        finally:
            await cache.stop()
