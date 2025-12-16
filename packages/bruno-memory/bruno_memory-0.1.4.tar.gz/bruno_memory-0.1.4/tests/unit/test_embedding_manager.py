"""
Tests for embedding manager.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from bruno_memory.exceptions import EmbeddingError
from bruno_memory.managers.embedding import EmbeddingCache, EmbeddingManager


@pytest.fixture
def mock_embedding_provider():
    """Create mock embedding provider."""
    provider = Mock()
    provider.embed_text = AsyncMock(return_value=[0.1, 0.2, 0.3, 0.4, 0.5])
    provider.embed_batch = AsyncMock(
        return_value=[
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.2, 0.3, 0.4, 0.5, 0.6],
            [0.3, 0.4, 0.5, 0.6, 0.7],
        ]
    )
    return provider


@pytest.fixture
def embedding_manager(mock_embedding_provider):
    """Create embedding manager with mock provider."""
    return EmbeddingManager(
        embedding_provider=mock_embedding_provider,
        cache_ttl=60,  # 1 minute for testing
        batch_size=2,
    )


@pytest.mark.asyncio
class TestEmbeddingManager:
    """Test suite for EmbeddingManager."""

    async def test_embed_text(self, embedding_manager):
        """Test basic text embedding."""
        embedding = await embedding_manager.embed_text("Hello world")

        assert len(embedding) == 5
        assert embedding == [0.1, 0.2, 0.3, 0.4, 0.5]

    async def test_embed_empty_text(self, embedding_manager):
        """Test embedding empty text raises error."""
        with pytest.raises(EmbeddingError):
            await embedding_manager.embed_text("")

    async def test_embed_with_cache(self, embedding_manager):
        """Test embedding caching."""
        text = "Test text for caching"

        # First call
        embedding1 = await embedding_manager.embed_text(text, use_cache=True)

        # Second call should use cache
        embedding2 = await embedding_manager.embed_text(text, use_cache=True)

        assert embedding1 == embedding2

        # Provider should only be called once
        assert embedding_manager.embedding_provider.embed_text.call_count == 1

    async def test_cache_expiration(self, embedding_manager):
        """Test cache expiration."""
        text = "Test text"

        # First call
        await embedding_manager.embed_text(text, use_cache=True)

        # Manually expire cache entry
        cache_key = embedding_manager._get_cache_key(text)
        if cache_key in embedding_manager._cache:
            old_embedding, _ = embedding_manager._cache[cache_key]
            # Set timestamp to past
            embedding_manager._cache[cache_key] = (
                old_embedding,
                datetime.now() - timedelta(seconds=120),
            )

        # Second call should generate new embedding
        await embedding_manager.embed_text(text, use_cache=True)

        # Provider should be called twice
        assert embedding_manager.embedding_provider.embed_text.call_count == 2

    async def test_embed_batch(self, embedding_manager):
        """Test batch embedding."""
        texts = ["Text 1", "Text 2", "Text 3"]

        embeddings = await embedding_manager.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 5 for emb in embeddings)

    async def test_embed_batch_with_cache(self, embedding_manager):
        """Test batch embedding with partial caching."""
        texts = ["Text A", "Text B", "Text C"]

        # Pre-cache one text
        await embedding_manager.embed_text(texts[0], use_cache=True)

        # Batch embed all three
        embeddings = await embedding_manager.embed_batch(texts, use_cache=True)

        assert len(embeddings) == 3

        # embed_batch should be called once for the uncached texts
        assert embedding_manager.embedding_provider.embed_batch.call_count == 1

    async def test_embed_message(self, embedding_manager):
        """Test message embedding."""
        message_content = "This is a test message"

        embedding = await embedding_manager.embed_message(message_content)

        assert len(embedding) == 5

    async def test_embed_message_with_metadata(self, embedding_manager):
        """Test message embedding with metadata context."""
        message_content = "Response to question"
        metadata = {
            "include_in_embedding": True,
            "context": "User asked about Python",
        }

        embedding = await embedding_manager.embed_message(message_content, metadata=metadata)

        assert len(embedding) == 5

    async def test_embed_memory(self, embedding_manager):
        """Test memory embedding with type prefix."""
        memory_content = "User prefers dark mode"
        memory_type = "preference"

        embedding = await embedding_manager.embed_memory(memory_content, memory_type)

        assert len(embedding) == 5

    async def test_clear_cache(self, embedding_manager):
        """Test cache clearing."""
        # Add some cached embeddings
        await embedding_manager.embed_text("Text 1", use_cache=True)
        await embedding_manager.embed_text("Text 2", use_cache=True)

        assert len(embedding_manager._cache) > 0

        # Clear cache
        embedding_manager.clear_cache()

        assert len(embedding_manager._cache) == 0

    async def test_get_cache_stats(self, embedding_manager):
        """Test cache statistics."""
        # Add some cached embeddings
        await embedding_manager.embed_text("Text 1", use_cache=True)
        await embedding_manager.embed_text("Text 2", use_cache=True)

        stats = embedding_manager.get_cache_stats()

        assert "total_cached" in stats
        assert "active" in stats
        assert "expired" in stats
        assert stats["total_cached"] >= 2

    async def test_find_similar(self, embedding_manager):
        """Test finding similar texts."""
        query_text = "Python programming"
        candidates = [
            ("Python is a programming language", {"id": 1}),
            ("JavaScript is also a language", {"id": 2}),
            ("Machine learning with Python", {"id": 3}),
        ]

        results = await embedding_manager.find_similar(
            query_text,
            candidates,
            top_k=2,
            similarity_threshold=0.0,
        )

        assert len(results) <= 2
        assert all(len(r) == 2 for r in results)  # (metadata, similarity) tuples

    async def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        similarity = EmbeddingManager._cosine_similarity(vec1, vec2)
        assert similarity == 1.0

        vec3 = [0.0, 1.0, 0.0]
        similarity = EmbeddingManager._cosine_similarity(vec1, vec3)
        assert similarity == 0.0

    async def test_cosine_similarity_different_dimensions(self):
        """Test cosine similarity with different dimension vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        with pytest.raises(ValueError):
            EmbeddingManager._cosine_similarity(vec1, vec2)
