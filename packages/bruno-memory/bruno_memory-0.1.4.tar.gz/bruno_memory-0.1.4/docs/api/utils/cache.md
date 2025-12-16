# Cache Utilities

Multi-level caching system for high-performance memory access.

## Overview

bruno-memory provides three cache implementations:

1. **InMemoryCache**: LRU cache with TTL support
2. **RedisCache**: Distributed caching with Redis
3. **MultiLevelCache**: L1 (memory) + L2 (Redis) tiered caching

## InMemoryCache

::: bruno_memory.utils.cache.InMemoryCache
    options:
      show_root_heading: true
      show_source: true
      members:
        - __init__
        - get
        - set
        - delete
        - exists
        - clear
        - get_many
        - set_many
        - stats

## RedisCache

::: bruno_memory.utils.cache.RedisCache
    options:
      show_root_heading: true
      show_source: true
      members:
        - __init__
        - connect
        - disconnect
        - get
        - set
        - delete
        - exists
        - clear
        - get_many
        - set_many
        - stats

## MultiLevelCache

::: bruno_memory.utils.cache.MultiLevelCache
    options:
      show_root_heading: true
      show_source: true
      members:
        - __init__
        - get
        - set
        - delete
        - exists
        - clear
        - get_many
        - set_many
        - stats

## Examples

### In-Memory Caching

```python
from bruno_memory.utils import InMemoryCache

# Create cache with max 1000 items
cache = InMemoryCache(max_size=1000)

# Set with TTL
await cache.set("key1", "value1", ttl=300)  # 5 minutes

# Get value
value = await cache.get("key1")

# Batch operations
await cache.set_many({
    "key2": "value2",
    "key3": "value3"
}, ttl=600)

values = await cache.get_many(["key1", "key2", "key3"])

# Statistics
stats = cache.stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

### Redis Caching

```python
from bruno_memory.utils import RedisCache

# Create Redis cache
cache = RedisCache(
    host="localhost",
    port=6379,
    prefix="myapp:"
)

await cache.connect()

# Use same API as InMemoryCache
await cache.set("session:123", user_data, ttl=3600)
data = await cache.get("session:123")

await cache.disconnect()
```

### Multi-Level Caching

```python
from bruno_memory.utils import (
    MultiLevelCache,
    InMemoryCache,
    RedisCache
)

# Create tiered cache
cache = MultiLevelCache(
    l1_cache=InMemoryCache(max_size=100),  # Fast L1
    l2_cache=RedisCache(host="localhost")   # Distributed L2
)

await cache.l2_cache.connect()

# Checks L1 first, then L2, promotes to L1 on L2 hit
value = await cache.get("key")

# Writes to both levels
await cache.set("key", "value", ttl=300)

# Combined statistics
stats = cache.stats()
print(f"L1 hits: {stats['l1_hits']}")
print(f"L2 hits: {stats['l2_hits']}")

await cache.l2_cache.disconnect()
```

### Integration with Backend

```python
from bruno_memory import create_backend
from bruno_memory.utils import InMemoryCache

# Create backend with caching
backend = create_backend("sqlite", database_path="memory.db")
cache = InMemoryCache(max_size=500)

await backend.connect()

async def get_cached_messages(conv_id: str):
    """Get messages with caching."""
    cache_key = f"messages:{conv_id}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    # Fallback to backend
    messages = await backend.retrieve_messages(
        conversation_id=conv_id,
        limit=50
    )
    
    # Cache for 5 minutes
    await cache.set(cache_key, messages, ttl=300)
    return messages
```

## Performance Tips

### LRU Eviction

The in-memory cache uses LRU (Least Recently Used) eviction:

```python
cache = InMemoryCache(max_size=100)

# When cache is full, least recently accessed items are evicted
for i in range(150):
    await cache.set(f"key{i}", f"value{i}")

# Only last 100 items remain
```

### TTL Management

Expired items are cleaned up automatically:

```python
cache = InMemoryCache(
    max_size=1000,
    cleanup_interval=60  # Check every 60 seconds
)

# Set short TTL for temporary data
await cache.set("temp", data, ttl=10)
```

### Batch Operations

Use batch operations for better performance:

```python
# Slower: individual sets
for key, value in data.items():
    await cache.set(key, value)

# Faster: batch set
await cache.set_many(data, ttl=300)
```

### Connection Pooling (Redis)

Redis cache uses connection pooling:

```python
cache = RedisCache(
    host="localhost",
    pool_size=10,  # Max 10 connections
    max_overflow=5  # Allow 5 extra if needed
)
```

## See Also

- [Backend Selection](../guide/backends.md) - Choosing the right backend
- [Performance Tuning](../guide/performance.md) - Optimization strategies
- [Backup & Analytics](api/backup.md) - Backup and analytics utilities
