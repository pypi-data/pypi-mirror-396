"""
Tests for Qdrant backend implementation.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import UUID

import pytest
from bruno_core.models import MemoryEntry, MemoryType, Message

from bruno_memory.backends.vector import QdrantBackend
from bruno_memory.base.config import QdrantConfig
from bruno_memory.exceptions import ConnectionError, MemoryError, QueryError


@pytest.fixture
def qdrant_config():
    """Create Qdrant configuration for testing."""
    return QdrantConfig(
        host="localhost",
        port=6333,
        collection_name="test_memories",
        vector_size=1536,
        distance_metric="cosine",
    )


@pytest.fixture
async def qdrant_backend(qdrant_config):
    """Create and initialize Qdrant backend for testing."""
    backend = QdrantBackend(qdrant_config)

    # Mock Qdrant client
    mock_client = AsyncMock()
    backend._client = mock_client
    backend._is_connected = True

    yield backend

    await backend.close()


@pytest.mark.asyncio
async def test_initialization(qdrant_config):
    """Test Qdrant initialization."""
    backend = QdrantBackend(qdrant_config)

    with patch("bruno_memory.backends.vector.qdrant_backend.AsyncQdrantClient") as mock_qdrant:
        mock_client = AsyncMock()
        mock_qdrant.return_value = mock_client

        # Mock get_collection to simulate existing collection
        mock_client.get_collection = AsyncMock()

        await backend.initialize()

        assert backend._is_connected
        assert backend._client is not None


@pytest.mark.asyncio
async def test_initialization_creates_collection(qdrant_config):
    """Test collection creation during initialization."""
    backend = QdrantBackend(qdrant_config)

    with patch("bruno_memory.backends.vector.qdrant_backend.AsyncQdrantClient") as mock_qdrant:
        mock_client = AsyncMock()
        mock_qdrant.return_value = mock_client

        # Mock get_collection to raise exception (collection doesn't exist)
        mock_client.get_collection = AsyncMock(side_effect=Exception("Not found"))
        mock_client.create_collection = AsyncMock()

        await backend.initialize()

        mock_client.create_collection.assert_called_once()


@pytest.mark.asyncio
async def test_store_message(qdrant_backend):
    """Test message storage."""
    message = Message(role="user", content="Test message", timestamp=datetime.now(timezone.utc))
    embedding = [0.1] * 1536  # Mock embedding vector

    qdrant_backend._client.upsert = AsyncMock()

    message_id = await qdrant_backend.store_message("session_1", message, embedding=embedding)

    assert message_id is not None
    # Verify it's a valid UUID
    UUID(message_id)

    qdrant_backend._client.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_store_message_without_embedding(qdrant_backend):
    """Test that storing message without embedding raises error."""
    message = Message(role="user", content="Test message", timestamp=datetime.now(timezone.utc))

    with pytest.raises(ValueError, match="Embedding vector is required"):
        await qdrant_backend.store_message("session_1", message)


@pytest.mark.asyncio
async def test_store_message_wrong_embedding_size(qdrant_backend):
    """Test that wrong embedding size raises error."""
    message = Message(role="user", content="Test message", timestamp=datetime.now(timezone.utc))
    embedding = [0.1] * 512  # Wrong size

    with pytest.raises(ValueError, match="Embedding size"):
        await qdrant_backend.store_message("session_1", message, embedding=embedding)


@pytest.mark.asyncio
async def test_retrieve_messages(qdrant_backend):
    """Test message retrieval."""
    # Mock scroll response
    mock_points = [
        MagicMock(
            payload={
                "role": "user",
                "content": "Message 1",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": "session_1",
                "type": "message",
            }
        ),
        MagicMock(
            payload={
                "role": "assistant",
                "content": "Message 2",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": "session_1",
                "type": "message",
            }
        ),
    ]

    qdrant_backend._client.scroll = AsyncMock(return_value=(mock_points, None))

    messages = await qdrant_backend.retrieve_messages("session_1")

    assert len(messages) == 2
    assert messages[0].content == "Message 1"
    assert messages[1].content == "Message 2"


@pytest.mark.asyncio
async def test_search_similar(qdrant_backend):
    """Test semantic similarity search."""
    query_vector = [0.1] * 1536

    # Mock search response
    mock_results = [
        MagicMock(
            payload={
                "role": "assistant",
                "content": "Similar message",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "message",
            },
            score=0.95,
        )
    ]

    qdrant_backend._client.search = AsyncMock(return_value=mock_results)

    results = await qdrant_backend.search_similar(query_vector, limit=5)

    assert len(results) == 1
    message, score = results[0]
    assert message.content == "Similar message"
    assert score == 0.95


@pytest.mark.asyncio
async def test_search_similar_wrong_vector_size(qdrant_backend):
    """Test that wrong query vector size raises error."""
    query_vector = [0.1] * 512  # Wrong size

    with pytest.raises(ValueError, match="Query vector size"):
        await qdrant_backend.search_similar(query_vector)


@pytest.mark.asyncio
async def test_search_with_session_filter(qdrant_backend):
    """Test similarity search with session filter."""
    query_vector = [0.1] * 1536

    qdrant_backend._client.search = AsyncMock(return_value=[])

    await qdrant_backend.search_similar(query_vector, session_id="session_1")

    # Verify filter was applied
    call_args = qdrant_backend._client.search.call_args
    query_filter = call_args[1]["query_filter"]
    assert query_filter is not None


@pytest.mark.asyncio
async def test_store_memory(qdrant_backend):
    """Test memory storage."""
    memory = MemoryEntry(content="Important fact", memory_type=MemoryType.FACT, user_id="test_user")
    embedding = [0.1] * 1536

    qdrant_backend._client.upsert = AsyncMock()

    memory_id = await qdrant_backend.store_memory(memory, embedding=embedding)

    assert memory_id is not None
    UUID(memory_id)

    qdrant_backend._client.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_retrieve_memories(qdrant_backend):
    """Test memory retrieval."""
    # Mock scroll response
    mock_points = [
        MagicMock(
            payload={
                "content": "Memory 1",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "importance": 0.8,
                "tags": ["important", "fact"],
                "type": "memory",
            }
        ),
        MagicMock(
            payload={
                "content": "Memory 2",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "importance": 0.6,
                "tags": ["fact"],
                "type": "memory",
            }
        ),
    ]

    qdrant_backend._client.scroll = AsyncMock(return_value=(mock_points, None))

    memories = await qdrant_backend.retrieve_memories(min_importance=0.5)

    assert len(memories) == 2
    assert all(m.metadata.importance >= 0.5 for m in memories)


@pytest.mark.asyncio
async def test_retrieve_memories_with_tags(qdrant_backend):
    """Test memory retrieval with tag filtering."""
    qdrant_backend._client.scroll = AsyncMock(return_value=([], None))

    await qdrant_backend.retrieve_memories(tags={"important", "fact"})

    # Verify tag filters were applied
    call_args = qdrant_backend._client.scroll.call_args
    scroll_filter = call_args[1]["scroll_filter"]
    assert scroll_filter is not None


@pytest.mark.asyncio
async def test_search_memories(qdrant_backend):
    """Test memory semantic search."""
    query_vector = [0.1] * 1536

    # Mock search response
    mock_results = [
        MagicMock(
            payload={
                "content": "Important AI fact",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "importance": 0.9,
                "tags": ["important", "ai"],
                "type": "memory",
            },
            score=0.92,
        )
    ]

    qdrant_backend._client.search = AsyncMock(return_value=mock_results)

    results = await qdrant_backend.search_memories(query_vector, limit=5)

    assert len(results) == 1
    memory, score = results[0]
    assert memory.content == "Important AI fact"
    assert score == 0.92


@pytest.mark.asyncio
async def test_search_memories_with_min_importance(qdrant_backend):
    """Test memory search with minimum importance filter."""
    query_vector = [0.1] * 1536

    qdrant_backend._client.search = AsyncMock(return_value=[])

    await qdrant_backend.search_memories(query_vector, min_importance=0.7)

    # Verify importance filter was applied
    call_args = qdrant_backend._client.search.call_args
    query_filter = call_args[1]["query_filter"]
    assert query_filter is not None


@pytest.mark.asyncio
async def test_delete_session(qdrant_backend):
    """Test session deletion."""
    qdrant_backend._client.delete = AsyncMock()

    result = await qdrant_backend.delete_session("session_1")

    assert result is True
    qdrant_backend._client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_clear_all(qdrant_backend):
    """Test clearing all data."""
    qdrant_backend._client.delete = AsyncMock()

    await qdrant_backend.clear_all()

    qdrant_backend._client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_connection_error():
    """Test connection error handling."""
    config = QdrantConfig(host="invalid-host", port=6333, collection_name="test")
    backend = QdrantBackend(config)

    with patch("bruno_memory.backends.vector.qdrant_backend.AsyncQdrantClient") as mock_qdrant:
        mock_client = AsyncMock()
        mock_qdrant.return_value = mock_client
        mock_client.get_collection = AsyncMock(side_effect=Exception("Connection failed"))
        mock_client.create_collection = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(ConnectionError):
            await backend.initialize()


@pytest.mark.asyncio
async def test_close(qdrant_backend):
    """Test closing connection."""
    await qdrant_backend.close()

    assert not qdrant_backend._is_connected
    assert qdrant_backend._client is None


@pytest.mark.asyncio
async def test_ensure_connected_raises_error():
    """Test that operations fail when not connected."""
    config = QdrantConfig(host="localhost", port=6333, collection_name="test")
    backend = QdrantBackend(config)

    with pytest.raises(ConnectionError):
        await backend.retrieve_messages("session_1")


@pytest.mark.asyncio
async def test_metadata_storage(qdrant_backend):
    """Test that additional metadata is stored correctly."""
    message = Message(role="user", content="Test message", timestamp=datetime.now(timezone.utc))
    embedding = [0.1] * 1536
    metadata = {"custom_field": "custom_value"}

    qdrant_backend._client.upsert = AsyncMock()

    await qdrant_backend.store_message("session_1", message, metadata=metadata, embedding=embedding)

    # Verify metadata was included in the call
    call_args = qdrant_backend._client.upsert.call_args
    point = call_args[1]["points"][0]
    assert point.payload["custom_field"] == "custom_value"


@pytest.mark.asyncio
async def test_distance_metrics():
    """Test that different distance metrics are properly configured."""
    for metric in ["cosine", "euclidean", "dot"]:
        config = QdrantConfig(
            host="localhost", port=6333, collection_name="test", distance_metric=metric
        )
        backend = QdrantBackend(config)

        with patch("bruno_memory.backends.vector.qdrant_backend.AsyncQdrantClient") as mock_qdrant:
            mock_client = AsyncMock()
            mock_qdrant.return_value = mock_client
            mock_client.get_collection = AsyncMock(side_effect=Exception("Not found"))
            mock_client.create_collection = AsyncMock()

            await backend.initialize()

            # Verify create_collection was called with correct distance metric
            call_args = mock_client.create_collection.call_args
            vectors_config = call_args[1]["vectors_config"]
            assert vectors_config.distance is not None
