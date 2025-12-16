"""
Tests for PostgreSQL backend implementation.

Tests require a running PostgreSQL instance. Configure connection via environment:
- POSTGRES_HOST (default: localhost)
- POSTGRES_PORT (default: 5432)
- POSTGRES_USER (default: postgres)
- POSTGRES_PASSWORD (default: postgres)
- POSTGRES_DB (default: bruno_memory_test)
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

from bruno_memory.backends.postgresql import PostgreSQLMemoryBackend
from bruno_memory.base import PostgreSQLConfig
from bruno_memory.exceptions import StorageError

# PostgreSQL connection config from environment
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "username": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "database": os.getenv("POSTGRES_DB", "bruno_memory_test"),
}


@pytest.fixture
async def pg_backend():
    """Create and initialize PostgreSQL backend for testing."""
    config = PostgreSQLConfig(**POSTGRES_CONFIG)
    backend = PostgreSQLMemoryBackend(config)

    try:
        await backend.initialize()
        yield backend
    finally:
        # Clean up test data
        if backend._pool:
            async with backend._pool.acquire() as conn:
                await conn.execute("TRUNCATE TABLE messages CASCADE")
                await conn.execute("TRUNCATE TABLE memory_entries CASCADE")
                await conn.execute("TRUNCATE TABLE session_contexts CASCADE")
                await conn.execute("TRUNCATE TABLE conversation_contexts CASCADE")
                await conn.execute("TRUNCATE TABLE user_contexts CASCADE")
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
class TestPostgreSQLBackend:
    """Test suite for PostgreSQL backend."""

    async def test_initialization(self, pg_backend):
        """Test backend initialization."""
        assert pg_backend._initialized
        assert pg_backend._pool is not None
        assert pg_backend._pool.get_size() > 0

    async def test_store_and_retrieve_message(self, pg_backend, sample_message):
        """Test storing and retrieving messages."""
        conversation_id = uuid4()

        # Create conversation context first
        async with pg_backend._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO conversation_contexts (conversation_id, user_id, message_count)
                VALUES ($1, $2, 0)
                """,
                conversation_id,
                "test_user",
            )

        # Store message
        message_id = await pg_backend.store_message(sample_message, conversation_id)
        assert isinstance(message_id, UUID)

        # Retrieve messages
        messages = await pg_backend.retrieve_messages(conversation_id)
        assert len(messages) == 1
        assert messages[0].content == sample_message.content
        assert messages[0].role == sample_message.role

    async def test_retrieve_messages_with_filters(self, pg_backend, sample_message):
        """Test retrieving messages with time filters."""
        conversation_id = uuid4()

        # Create conversation context
        async with pg_backend._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO conversation_contexts (conversation_id, user_id, message_count)
                VALUES ($1, $2, 0)
                """,
                conversation_id,
                "test_user",
            )

        # Store messages at different times
        now = datetime.now()
        msg1 = Message(**sample_message.model_dump())
        msg1.timestamp = now - timedelta(hours=2)
        msg2 = Message(**sample_message.model_dump())
        msg2.timestamp = now - timedelta(hours=1)
        msg3 = Message(**sample_message.model_dump())
        msg3.timestamp = now

        await pg_backend.store_message(msg1, conversation_id)
        await pg_backend.store_message(msg2, conversation_id)
        await pg_backend.store_message(msg3, conversation_id)

        # Test before filter
        messages = await pg_backend.retrieve_messages(
            conversation_id,
            before=now - timedelta(minutes=30),
        )
        assert len(messages) == 2

        # Test after filter
        messages = await pg_backend.retrieve_messages(
            conversation_id,
            after=now - timedelta(hours=1, minutes=30),
        )
        assert len(messages) == 2

        # Test limit
        messages = await pg_backend.retrieve_messages(
            conversation_id,
            limit=2,
        )
        assert len(messages) == 2

    async def test_search_messages(self, pg_backend):
        """Test full-text search on messages."""
        conversation_id = uuid4()

        # Create conversation context
        async with pg_backend._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO conversation_contexts (conversation_id, user_id, message_count)
                VALUES ($1, $2, 0)
                """,
                conversation_id,
                "test_user",
            )

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

        await pg_backend.store_message(msg1, conversation_id)
        await pg_backend.store_message(msg2, conversation_id)
        await pg_backend.store_message(msg3, conversation_id)

        # Search for "programming"
        results = await pg_backend.search_messages("programming", conversation_id)
        assert len(results) == 2

        # Search for "database"
        results = await pg_backend.search_messages("database", conversation_id)
        assert len(results) == 1
        assert "Database" in results[0].content

    async def test_store_and_retrieve_memory(self, pg_backend, sample_memory_entry):
        """Test storing and retrieving memories."""
        memory_id = await pg_backend.store_memory(sample_memory_entry)
        assert isinstance(memory_id, UUID)

        memories = await pg_backend.retrieve_memories(sample_memory_entry.user_id)
        assert len(memories) == 1
        assert memories[0].content == sample_memory_entry.content
        assert memories[0].memory_type == sample_memory_entry.memory_type
        assert memories[0].metadata.importance == sample_memory_entry.metadata.importance

    async def test_retrieve_memories_with_filters(self, pg_backend):
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

        await pg_backend.store_memory(fact_memory)
        await pg_backend.store_memory(preference_memory)

        # Filter by memory type
        facts = await pg_backend.retrieve_memories(user_id, memory_type=MemoryType.FACT)
        assert len(facts) == 1
        assert facts[0].memory_type == MemoryType.FACT

        # Filter by limit
        limited = await pg_backend.retrieve_memories(user_id, limit=1)
        assert len(limited) == 1
        assert limited[0].metadata.importance == 0.9  # Should return highest importance

    async def test_search_memories(self, pg_backend):
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

        mem3 = MemoryEntry(
            content="JavaScript is also popular",
            memory_type=MemoryType.FACT,
            user_id=user_id,
            metadata=MemoryMetadata(importance=0.7),
        )

        await pg_backend.store_memory(mem1)
        await pg_backend.store_memory(mem2)
        await pg_backend.store_memory(mem3)

        # Search for "Python"
        query = MemoryQuery(
            user_id=user_id,
            query_text="Python",
            limit=10,
        )
        results = await pg_backend.search_memories(query)
        assert len(results) == 2

        # Search with memory type filter
        query = MemoryQuery(
            user_id=user_id,
            query_text="Python",
            memory_types=[MemoryType.FACT],
            limit=10,
        )
        results = await pg_backend.search_memories(query)
        assert len(results) == 1
        assert results[0].memory_type == MemoryType.FACT

    async def test_session_management(self, pg_backend):
        """Test session creation and management."""
        user_id = "test_user"
        conversation_id = uuid4()

        # Create session
        session = await pg_backend.create_session(
            user_id,
            conversation_id,
            initial_state={"step": "started"},
        )
        assert session.session_id is not None
        assert session.user_id == user_id
        assert session.is_active

        # Retrieve session
        retrieved = await pg_backend.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
        assert retrieved.state["step"] == "started"

        # Update session state
        await pg_backend.update_session_state(
            session.session_id,
            {"step": "completed"},
        )
        updated = await pg_backend.get_session(session.session_id)
        assert updated.state["step"] == "completed"

        # End session
        await pg_backend.end_session(session.session_id)
        ended = await pg_backend.get_session(session.session_id)
        assert not ended.is_active
        assert ended.ended_at is not None

    async def test_conversation_context(self, pg_backend, sample_message):
        """Test conversation context retrieval."""
        conversation_id = uuid4()
        user_id = "test_user"

        # Create conversation context
        async with pg_backend._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO conversation_contexts 
                (conversation_id, user_id, title, message_count)
                VALUES ($1, $2, $3, 0)
                """,
                conversation_id,
                user_id,
                "Test Conversation",
            )

        # Store some messages
        await pg_backend.store_message(sample_message, conversation_id)
        await pg_backend.store_message(sample_message, conversation_id)

        # Get context
        context = await pg_backend.get_context(conversation_id)
        assert context.conversation_id == conversation_id
        assert context.user_id == user_id
        assert len(context.messages) == 2

    async def test_clear_history(self, pg_backend, sample_message):
        """Test clearing message history."""
        conversation_id = uuid4()

        # Create conversation context
        async with pg_backend._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO conversation_contexts (conversation_id, user_id, message_count)
                VALUES ($1, $2, 0)
                """,
                conversation_id,
                "test_user",
            )

        # Store messages
        await pg_backend.store_message(sample_message, conversation_id)
        await pg_backend.store_message(sample_message, conversation_id)
        await pg_backend.store_message(sample_message, conversation_id)

        # Clear all history
        deleted = await pg_backend.clear_history(conversation_id)
        assert deleted == 3

        # Verify empty
        messages = await pg_backend.retrieve_messages(conversation_id)
        assert len(messages) == 0

    async def test_get_statistics(self, pg_backend, sample_message, sample_memory_entry):
        """Test statistics retrieval."""
        conversation_id = uuid4()

        # Create conversation context
        async with pg_backend._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO conversation_contexts (conversation_id, user_id, message_count)
                VALUES ($1, $2, 0)
                """,
                conversation_id,
                "test_user",
            )

        # Add some data
        await pg_backend.store_message(sample_message, conversation_id)
        await pg_backend.store_memory(sample_memory_entry)
        await pg_backend.create_session("test_user", conversation_id)

        # Get statistics
        stats = await pg_backend.get_statistics()
        assert stats["total_messages"] >= 1
        assert stats["total_memories"] >= 1
        assert stats["active_sessions"] >= 1
        assert "pool_size" in stats
        assert "pool_free" in stats

    async def test_connection_pooling(self, pg_backend):
        """Test connection pool behavior."""
        # Get pool stats
        stats = await pg_backend.get_statistics()
        initial_size = stats["pool_size"]

        # Create multiple concurrent operations
        async def concurrent_operation():
            conversation_id = uuid4()
            async with pg_backend._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO conversation_contexts (conversation_id, user_id, message_count)
                    VALUES ($1, $2, 0)
                    """,
                    conversation_id,
                    f"user_{uuid4().hex[:8]}",
                )

        # Run concurrent operations
        await asyncio.gather(*[concurrent_operation() for _ in range(10)])

        # Verify pool handled concurrency
        stats = await pg_backend.get_statistics()
        assert stats["pool_size"] >= initial_size

    async def test_memory_expiration(self, pg_backend):
        """Test memory expiration handling."""
        user_id = "test_user"

        # Store memory with expiration
        expired_memory = MemoryEntry(
            content="Expired memory",
            memory_type=MemoryType.FACT,
            user_id=user_id,
            metadata=MemoryMetadata(
                importance=0.8,
                expires_at=datetime.now() - timedelta(hours=1),  # Already expired
            ),
        )

        active_memory = MemoryEntry(
            content="Active memory",
            memory_type=MemoryType.FACT,
            user_id=user_id,
            metadata=MemoryMetadata(
                importance=0.9,
                expires_at=datetime.now() + timedelta(hours=1),  # Still valid
            ),
        )

        await pg_backend.store_memory(expired_memory)
        await pg_backend.store_memory(active_memory)

        # Retrieve should only return non-expired
        memories = await pg_backend.retrieve_memories(user_id)
        assert len(memories) == 1
        assert memories[0].content == "Active memory"


@pytest.mark.asyncio
async def test_factory_integration():
    """Test PostgreSQL backend factory registration."""
    from bruno_memory.factory import MemoryBackendFactory

    config = PostgreSQLConfig(**POSTGRES_CONFIG)
    backend = MemoryBackendFactory.create_backend("postgresql", config)

    assert isinstance(backend, PostgreSQLMemoryBackend)
    await backend.close()


# Skip tests if PostgreSQL is not available
def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line("markers", "postgres: mark test as requiring PostgreSQL")


def pytest_collection_modifyitems(config, items):
    """Skip PostgreSQL tests if connection fails."""
    try:
        import asyncpg

        # Try to connect
        loop = asyncio.new_event_loop()

        async def test_connection():
            conn = await asyncpg.connect(**POSTGRES_CONFIG, timeout=2)
            await conn.close()

        loop.run_until_complete(test_connection())
        loop.close()
    except Exception:
        skip_postgres = pytest.mark.skip(reason="PostgreSQL not available")
        for item in items:
            if "postgresql" in str(item.fspath).lower():
                item.add_marker(skip_postgres)
