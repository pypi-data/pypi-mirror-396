"""
Tests for ChromaDB backend implementation.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from bruno_core.models import MemoryEntry, MemoryType, Message

from bruno_memory.backends.vector import ChromaDBBackend
from bruno_memory.base.config import ChromaDBConfig
from bruno_memory.exceptions import ConnectionError, MemoryError, QueryError


@pytest.fixture
def chromadb_config():
    """Create ChromaDB configuration for testing."""
    return ChromaDBConfig(
        persist_directory=None,  # In-memory for tests
        collection_name="test_memories",
        distance_function="cosine",
    )


@pytest.fixture
async def chromadb_backend(chromadb_config):
    """Create and initialize ChromaDB backend for testing."""
    backend = ChromaDBBackend(chromadb_config)

    # Mock ChromaDB client
    with patch("bruno_memory.backends.vector.chromadb_backend.chromadb") as mock_chromadb:
        mock_client = MagicMock()
        mock_collection = MagicMock()

        mock_chromadb.Client.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        backend._client = mock_client
        backend._collection = mock_collection
        backend._is_connected = True

        # Mock executor
        from concurrent.futures import ThreadPoolExecutor

        backend._executor = ThreadPoolExecutor(max_workers=1)

        yield backend

        await backend.close()


@pytest.mark.asyncio
async def test_initialization(chromadb_config):
    """Test ChromaDB initialization."""
    backend = ChromaDBBackend(chromadb_config)

    with patch("bruno_memory.backends.vector.chromadb_backend.chromadb") as mock_chromadb:
        mock_client = MagicMock()
        mock_collection = MagicMock()

        mock_chromadb.Client.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        await backend.initialize()

        assert backend._is_connected
        assert backend._client is not None
        assert backend._collection is not None

        await backend.close()


@pytest.mark.asyncio
async def test_store_message(chromadb_backend):
    """Test message storage."""
    message = Message(role="user", content="Test message", timestamp=datetime.now(timezone.utc))

    # Mock collection add
    chromadb_backend._collection.add = MagicMock()

    message_id = await chromadb_backend.store_message("session_1", message)

    assert message_id is not None
    assert "session_1" in message_id
    chromadb_backend._collection.add.assert_called_once()


@pytest.mark.asyncio
async def test_retrieve_messages(chromadb_backend):
    """Test message retrieval."""
    # Mock collection get
    chromadb_backend._collection.get = MagicMock(
        return_value={
            "documents": ["Test message 1", "Test message 2"],
            "metadatas": [
                {
                    "role": "user",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "session_id": "session_1",
                    "type": "message",
                },
                {
                    "role": "assistant",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "session_id": "session_1",
                    "type": "message",
                },
            ],
        }
    )

    messages = await chromadb_backend.retrieve_messages("session_1")

    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"


@pytest.mark.asyncio
async def test_search_similar(chromadb_backend):
    """Test semantic similarity search."""
    query = "What is the weather?"

    # Mock collection query
    chromadb_backend._collection.query = MagicMock(
        return_value={
            "documents": [["It is sunny today"]],
            "metadatas": [
                [
                    {
                        "role": "assistant",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "message",
                    }
                ]
            ],
            "distances": [[0.15]],  # 0.15 distance = 0.85 similarity
        }
    )

    results = await chromadb_backend.search_similar(query, limit=5)

    assert len(results) == 1
    message, score = results[0]
    assert message.content == "It is sunny today"
    assert score == pytest.approx(0.85, abs=0.01)


@pytest.mark.asyncio
async def test_store_memory(chromadb_backend):
    """Test memory storage."""
    memory = MemoryEntry(content="Important fact", memory_type=MemoryType.FACT, user_id="test_user")

    # Mock collection add
    chromadb_backend._collection.add = MagicMock()

    memory_id = await chromadb_backend.store_memory(memory)

    assert memory_id is not None
    assert "memory_" in memory_id
    chromadb_backend._collection.add.assert_called_once()


@pytest.mark.asyncio
async def test_retrieve_memories(chromadb_backend):
    """Test memory retrieval."""
    # Mock collection get
    chromadb_backend._collection.get = MagicMock(
        return_value={
            "documents": ["Memory 1", "Memory 2"],
            "metadatas": [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "importance": 0.8,
                    "tags": "important,fact",
                    "type": "memory",
                },
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "importance": 0.6,
                    "tags": "fact",
                    "type": "memory",
                },
            ],
        }
    )

    memories = await chromadb_backend.retrieve_memories(min_importance=0.5)

    assert len(memories) == 2
    assert memories[0].metadata.importance >= 0.5


@pytest.mark.asyncio
async def test_search_memories(chromadb_backend):
    """Test memory semantic search."""
    query = "important facts"

    # Mock collection query
    chromadb_backend._collection.query = MagicMock(
        return_value={
            "documents": [["Important fact about AI"]],
            "metadatas": [
                [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "importance": 0.9,
                        "tags": "important,ai",
                        "type": "memory",
                    }
                ]
            ],
            "distances": [[0.1]],  # High similarity
        }
    )

    results = await chromadb_backend.search_memories(query, limit=5)

    assert len(results) == 1
    memory, score = results[0]
    assert memory.content == "Important fact about AI"
    assert score == pytest.approx(0.9, abs=0.01)


@pytest.mark.asyncio
async def test_delete_session(chromadb_backend):
    """Test session deletion."""
    # Mock collection get and delete
    chromadb_backend._collection.get = MagicMock(return_value={"ids": ["msg1", "msg2", "msg3"]})
    chromadb_backend._collection.delete = MagicMock()

    result = await chromadb_backend.delete_session("session_1")

    assert result is True
    chromadb_backend._collection.delete.assert_called_once()


@pytest.mark.asyncio
async def test_clear_all(chromadb_backend):
    """Test clearing all data."""
    # Mock client delete_collection and get_or_create_collection
    chromadb_backend._client.delete_collection = MagicMock()
    chromadb_backend._client.get_or_create_collection = MagicMock(return_value=MagicMock())

    await chromadb_backend.clear_all()

    chromadb_backend._client.delete_collection.assert_called_once()


@pytest.mark.asyncio
async def test_connection_error():
    """Test connection error handling."""
    config = ChromaDBConfig(persist_directory="/invalid/path", collection_name="test")
    backend = ChromaDBBackend(config)

    with patch(
        "bruno_memory.backends.vector.chromadb_backend.chromadb.PersistentClient"
    ) as mock_client:
        mock_client.side_effect = Exception("Connection failed")

        with pytest.raises(ConnectionError):
            await backend.initialize()


@pytest.mark.asyncio
async def test_filter_by_min_score(chromadb_backend):
    """Test filtering results by minimum score."""
    query = "test query"

    # Mock collection query with varying scores
    chromadb_backend._collection.query = MagicMock(
        return_value={
            "documents": [["Result 1", "Result 2", "Result 3"]],
            "metadatas": [
                [
                    {
                        "role": "user",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "message",
                    },
                    {
                        "role": "user",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "message",
                    },
                    {
                        "role": "user",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "message",
                    },
                ]
            ],
            "distances": [[0.1, 0.5, 0.9]],  # Similarities: 0.9, 0.5, 0.1
        }
    )

    results = await chromadb_backend.search_similar(query, limit=10, min_score=0.6)

    # Only results with score >= 0.6 should be returned
    assert len(results) == 1
    assert results[0][1] >= 0.6


@pytest.mark.asyncio
async def test_session_filter_in_search(chromadb_backend):
    """Test session filtering in similarity search."""
    query = "test query"

    chromadb_backend._collection.query = MagicMock(
        return_value={
            "documents": [["Message from session"]],
            "metadatas": [
                [
                    {
                        "role": "user",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "session_id": "session_1",
                        "type": "message",
                    }
                ]
            ],
            "distances": [[0.2]],
        }
    )

    results = await chromadb_backend.search_similar(query, session_id="session_1")

    assert len(results) == 1
    # Verify the query was called with session filter
    call_args = chromadb_backend._collection.query.call_args
    assert call_args[1]["where"]["session_id"] == "session_1"


@pytest.mark.asyncio
async def test_importance_filtering(chromadb_backend):
    """Test filtering memories by importance."""
    # Mock collection get
    chromadb_backend._collection.get = MagicMock(
        return_value={
            "documents": ["High importance", "Medium importance", "Low importance"],
            "metadatas": [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "importance": 0.9,
                    "type": "memory",
                },
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "importance": 0.6,
                    "type": "memory",
                },
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "importance": 0.3,
                    "type": "memory",
                },
            ],
        }
    )

    memories = await chromadb_backend.retrieve_memories(min_importance=0.5)

    # Should only return memories with importance >= 0.5
    assert len(memories) == 2
    assert all(m.metadata.importance >= 0.5 for m in memories)
