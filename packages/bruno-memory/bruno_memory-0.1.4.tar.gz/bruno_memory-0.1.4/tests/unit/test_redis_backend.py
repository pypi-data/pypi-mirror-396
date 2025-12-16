"""
Tests for Redis backend implementation.

Tests require a running Redis instance. Configure connection via environment:
- REDIS_HOST (default: localhost)
- REDIS_PORT (default: 6379)
- REDIS_DB (default: 15)  # Use high DB number for testing
- REDIS_PASSWORD (default: None)
"""

import asyncio
import os
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from bruno_core.models import (
    MemoryEntry,
    MemoryMetadata,
    MemoryQuery,
    MemoryType,
    Message,
    MessageRole,
)

from bruno_memory.backends.redis import RedisMemoryBackend
from bruno_memory.base import RedisConfig
from bruno_memory.exceptions import NotFoundError, StorageError

# Redis connection config from environment
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "database": int(os.getenv("REDIS_DB", "15")),  # Use DB 15 for testing
    "password": os.getenv("REDIS_PASSWORD", None),
}


@pytest.fixture
async def redis_backend():
    """Create and initialize Redis backend for testing."""
    config = RedisConfig(**REDIS_CONFIG)
    backend = RedisMemoryBackend(config)

    try:
        await backend.initialize()

        # Clear test database before tests
        await backend._client.flushdb()

        yield backend
    finally:
        # Clean up test data
        if backend._client:
            await backend._client.flushdb()
        await backend.close()


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    return Message(
        role=MessageRole.USER,
        content="Test message content",
        message_type="text",
        timestamp=datetime.now(),
        metadata={"test": "data"},
    )


@pytest.fixture
def sample_memory_entry():
    """Create a sample memory entry for testing."""
    return MemoryEntry(
        content="Test memory content",
        memory_type=MemoryType.FACT,
        user_id="test_user",
        conversation_id=uuid4(),
        metadata=MemoryMetadata(
            importance=0.8,
            confidence=0.9,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_accessed=datetime.now(),
        ),
    )


@pytest.mark.asyncio
class TestRedisBackend:
    """Test suite for Redis backend."""

    async def test_initialization(self, redis_backend):
        """Test backend initialization."""
        assert redis_backend._initialized
        assert redis_backend._client is not None
        assert redis_backend._pool is not None

    async def test_health_check(self, redis_backend):
        """Test health check."""
        health = await redis_backend.health_check()
        assert health is True

    async def test_store_and_retrieve_message(self, redis_backend, sample_message):
        """Test storing and retrieving messages."""
        conversation_id = uuid4()

        # Store message
        message_id = await redis_backend.store_message(sample_message, conversation_id)
        assert isinstance(message_id, UUID)

        # Retrieve messages
        messages = await redis_backend.retrieve_messages(conversation_id)
        assert len(messages) == 1
        assert messages[0].content == sample_message.content
        assert messages[0].role == sample_message.role

    async def test_retrieve_messages_with_filters(self, redis_backend, sample_message):
        """Test retrieving messages with time filters."""
        conversation_id = uuid4()

        # Store messages at different times
        now = datetime.now()
        msg1 = Message(**sample_message.model_dump())
        msg1.timestamp = now - timedelta(hours=2)
        msg2 = Message(**sample_message.model_dump())
        msg2.timestamp = now - timedelta(hours=1)
        msg3 = Message(**sample_message.model_dump())
        msg3.timestamp = now

        await redis_backend.store_message(msg1, conversation_id)
        await redis_backend.store_message(msg2, conversation_id)
        await redis_backend.store_message(msg3, conversation_id)

        # Test before filter
        messages = await redis_backend.retrieve_messages(
            conversation_id,
            before=now - timedelta(minutes=30),
        )
        assert len(messages) == 2

        # Test after filter
        messages = await redis_backend.retrieve_messages(
            conversation_id,
            after=now - timedelta(hours=1, minutes=30),
        )
        assert len(messages) == 2

        # Test limit
        messages = await redis_backend.retrieve_messages(
            conversation_id,
            limit=2,
        )
        assert len(messages) == 2

    async def test_search_messages(self, redis_backend):
        """Test searching messages."""
        conversation_id = uuid4()

        # Store messages with different content
        msg1 = Message(
            role=MessageRole.USER,
            content="Python programming is great",
            timestamp=datetime.now(),
        )
        msg2 = Message(
            role=MessageRole.USER,
            content="JavaScript programming is fun",
            timestamp=datetime.now(),
        )
        msg3 = Message(
            role=MessageRole.USER,
            content="Database design patterns",
            timestamp=datetime.now(),
        )

        await redis_backend.store_message(msg1, conversation_id)
        await redis_backend.store_message(msg2, conversation_id)
        await redis_backend.store_message(msg3, conversation_id)

        # Search for "programming"
        results = await redis_backend.search_messages("programming", conversation_id)
        assert len(results) == 2

        # Search for "database"
        results = await redis_backend.search_messages("database", conversation_id)
        assert len(results) == 1
        assert "Database" in results[0].content

    async def test_store_and_retrieve_memory(self, redis_backend, sample_memory_entry):
        """Test storing and retrieving memories."""
        memory_id = await redis_backend.store_memory(sample_memory_entry)
        assert isinstance(memory_id, UUID)

        memories = await redis_backend.retrieve_memories(sample_memory_entry.user_id)
        assert len(memories) == 1
        assert memories[0].content == sample_memory_entry.content
        assert memories[0].memory_type == sample_memory_entry.memory_type

    async def test_retrieve_memories_with_filters(self, redis_backend):
        """Test retrieving memories with filters."""
        user_id = "test_user"

        # Store different memory types
        fact_memory = MemoryEntry(
            content="Python was created by Guido van Rossum",
            memory_type=MemoryType.FACT,
            user_id=user_id,
            metadata=MemoryMetadata(importance=0.9),
        )

        preference_memory = MemoryEntry(
            content="User prefers dark mode",
            memory_type=MemoryType.PREFERENCE,
            user_id=user_id,
            metadata=MemoryMetadata(importance=0.7),
        )

        await redis_backend.store_memory(fact_memory)
        await redis_backend.store_memory(preference_memory)

        # Filter by memory type
        facts = await redis_backend.retrieve_memories(user_id, memory_type=MemoryType.FACT)
        assert len(facts) == 1
        assert facts[0].memory_type == MemoryType.FACT

        # Filter by limit
        limited = await redis_backend.retrieve_memories(user_id, limit=1)
        assert len(limited) == 1
        assert limited[0].metadata.importance == 0.9  # Should return highest importance

    async def test_search_memories(self, redis_backend):
        """Test searching memories."""
        user_id = "test_user"

        # Store memories with different content
        mem1 = MemoryEntry(
            content="Python is a programming language",
            memory_type=MemoryType.FACT,
            user_id=user_id,
            metadata=MemoryMetadata(importance=0.8),
        )

        mem2 = MemoryEntry(
            content="User loves Python development",
            memory_type=MemoryType.PREFERENCE,
            user_id=user_id,
            metadata=MemoryMetadata(importance=0.9),
        )

        await redis_backend.store_memory(mem1)
        await redis_backend.store_memory(mem2)

        # Search for "Python"
        query = MemoryQuery(
            user_id=user_id,
            query_text="Python",
            limit=10,
        )
        results = await redis_backend.search_memories(query)
        assert len(results) == 2

        # Search with memory type filter
        query = MemoryQuery(
            user_id=user_id,
            query_text="Python",
            memory_types=[MemoryType.FACT],
            limit=10,
        )
        results = await redis_backend.search_memories(query)
        assert len(results) == 1
        assert results[0].memory_type == MemoryType.FACT

    async def test_delete_memory(self, redis_backend, sample_memory_entry):
        """Test deleting memory entries."""
        memory_id = await redis_backend.store_memory(sample_memory_entry)

        # Verify it exists
        memories = await redis_backend.retrieve_memories(sample_memory_entry.user_id)
        assert len(memories) == 1

        # Delete it
        await redis_backend.delete_memory(memory_id)

        # Verify it's gone
        memories = await redis_backend.retrieve_memories(sample_memory_entry.user_id)
        assert len(memories) == 0

    async def test_session_management(self, redis_backend):
        """Test session creation and management."""
        user_id = "test_user"
        conversation_id = uuid4()

        # Create session
        session = await redis_backend.create_session(
            user_id,
            conversation_id,
            initial_state={"step": "started"},
        )
        assert session.session_id is not None
        assert session.user_id == user_id
        assert session.is_active

        # Retrieve session
        retrieved = await redis_backend.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
        assert retrieved.state["step"] == "started"

        # Update session state
        await redis_backend.update_session_state(
            session.session_id,
            {"step": "completed"},
        )
        updated = await redis_backend.get_session(session.session_id)
        assert updated.state["step"] == "completed"

        # End session
        await redis_backend.end_session(session.session_id)
        ended = await redis_backend.get_session(session.session_id)
        assert not ended.is_active
        assert ended.ended_at is not None

    async def test_conversation_context(self, redis_backend, sample_message):
        """Test conversation context retrieval."""
        conversation_id = uuid4()

        # Store some messages
        await redis_backend.store_message(sample_message, conversation_id)
        await redis_backend.store_message(sample_message, conversation_id)

        # Get context
        context = await redis_backend.get_context(conversation_id)
        assert context.conversation_id == conversation_id
        assert len(context.messages) == 2

    async def test_clear_history(self, redis_backend, sample_message):
        """Test clearing message history."""
        conversation_id = uuid4()

        # Store messages
        await redis_backend.store_message(sample_message, conversation_id)
        await redis_backend.store_message(sample_message, conversation_id)
        await redis_backend.store_message(sample_message, conversation_id)

        # Clear all history
        deleted = await redis_backend.clear_history(conversation_id)
        assert deleted == 3

        # Verify empty
        messages = await redis_backend.retrieve_messages(conversation_id)
        assert len(messages) == 0

    async def test_clear_history_with_before(self, redis_backend):
        """Test clearing history with before timestamp."""
        conversation_id = uuid4()
        now = datetime.now()

        # Store messages at different times
        msg1 = Message(
            role=MessageRole.USER,
            content="Old message",
            timestamp=now - timedelta(hours=2),
        )
        msg2 = Message(
            role=MessageRole.USER,
            content="Recent message",
            timestamp=now,
        )

        await redis_backend.store_message(msg1, conversation_id)
        await redis_backend.store_message(msg2, conversation_id)

        # Clear only old messages
        deleted = await redis_backend.clear_history(
            conversation_id,
            before=now - timedelta(hours=1),
        )
        assert deleted == 1

        # Verify recent message still exists
        messages = await redis_backend.retrieve_messages(conversation_id)
        assert len(messages) == 1
        assert messages[0].content == "Recent message"

    async def test_get_statistics(self, redis_backend, sample_message, sample_memory_entry):
        """Test statistics retrieval."""
        conversation_id = uuid4()

        # Add some data
        await redis_backend.store_message(sample_message, conversation_id)
        await redis_backend.store_memory(sample_memory_entry)
        await redis_backend.create_session("test_user", conversation_id)

        # Get statistics
        stats = await redis_backend.get_statistics()
        assert stats["total_messages"] >= 1
        assert stats["total_memories"] >= 1
        assert stats["active_sessions"] >= 1
        assert "redis_version" in stats
        assert "used_memory" in stats
        assert "total_keys" in stats

    async def test_ttl_expiration(self, redis_backend):
        """Test TTL-based expiration."""
        # Create backend with short TTL
        config = RedisConfig(**REDIS_CONFIG, ttl_default=2)
        backend = RedisMemoryBackend(config)
        await backend.initialize()

        try:
            conversation_id = uuid4()
            message = Message(
                role=MessageRole.USER,
                content="This will expire",
                timestamp=datetime.now(),
            )

            # Store message
            await backend.store_message(message, conversation_id)

            # Verify it exists
            messages = await backend.retrieve_messages(conversation_id)
            assert len(messages) == 1

            # Wait for expiration
            await asyncio.sleep(3)

            # Verify it's gone
            messages = await backend.retrieve_messages(conversation_id)
            assert len(messages) == 0

        finally:
            await backend.close()

    async def test_concurrent_operations(self, redis_backend):
        """Test concurrent operations."""
        conversation_id = uuid4()

        async def store_message(idx):
            message = Message(
                role=MessageRole.USER,
                content=f"Message {idx}",
                timestamp=datetime.now(),
            )
            return await redis_backend.store_message(message, conversation_id)

        # Store messages concurrently
        message_ids = await asyncio.gather(*[store_message(i) for i in range(10)])

        assert len(message_ids) == 10
        assert len(set(message_ids)) == 10  # All unique

        # Verify all stored
        messages = await redis_backend.retrieve_messages(conversation_id)
        assert len(messages) == 10


@pytest.mark.asyncio
async def test_factory_integration():
    """Test Redis backend factory registration."""
    from bruno_memory.factory import MemoryBackendFactory

    factory = MemoryBackendFactory()
    config = RedisConfig(**REDIS_CONFIG)
    backend = factory.create_backend("redis", config)

    assert isinstance(backend, RedisMemoryBackend)
    await backend.close()


# Skip tests if Redis is not available
def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line("markers", "redis: mark test as requiring Redis")


def pytest_collection_modifyitems(config, items):
    """Skip Redis tests if connection fails."""
    try:
        import redis

        # Try to connect
        client = redis.Redis(**REDIS_CONFIG, socket_connect_timeout=2)
        client.ping()
        client.close()
    except Exception:
        skip_redis = pytest.mark.skip(reason="Redis not available")
        for item in items:
            if "redis" in str(item.fspath).lower():
                item.add_marker(skip_redis)
