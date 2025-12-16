"""
Tests for memory compressor.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from bruno_core.models import MemoryEntry, MemoryType, Message, MessageRole

from bruno_memory.exceptions import CompressionError
from bruno_memory.managers.compressor import (
    AdaptiveCompressor,
    ImportanceFilterStrategy,
    MemoryCompressor,
    SummarizationStrategy,
    TimeWindowStrategy,
)


@pytest.fixture
def mock_backend():
    """Create mock backend."""
    backend = Mock()
    backend.retrieve_messages = AsyncMock()
    backend.clear_history = AsyncMock()
    backend.store_message = AsyncMock()
    backend.store_memory = AsyncMock()
    return backend


@pytest.fixture
def sample_messages():
    """Create sample messages for testing."""
    now = datetime.now()
    messages = []

    for i in range(10):
        msg = Message(
            role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
            content=f"Message {i}",
            timestamp=now - timedelta(hours=10 - i),
            metadata={"importance": 0.5 + (i * 0.05)},
        )
        messages.append(msg)

    return messages


@pytest.mark.asyncio
class TestTimeWindowStrategy:
    """Test suite for TimeWindowStrategy."""

    async def test_compress_by_time_window(self, sample_messages):
        """Test compression by time window."""
        strategy = TimeWindowStrategy(window_hours=5)

        compressed, metadata = await strategy.compress(sample_messages)

        # Should keep messages from last 5 hours
        assert len(compressed) < len(sample_messages)
        assert metadata["compressed"] is True
        assert metadata["strategy"] == "time_window"

    async def test_compress_with_target_size(self, sample_messages):
        """Test compression with target size."""
        strategy = TimeWindowStrategy(window_hours=24)

        compressed, metadata = await strategy.compress(sample_messages, target_size=5)

        assert len(compressed) == 5
        assert metadata["compressed"] is True


@pytest.mark.asyncio
class TestImportanceFilterStrategy:
    """Test suite for ImportanceFilterStrategy."""

    async def test_filter_by_importance(self, sample_messages):
        """Test filtering by importance threshold."""
        strategy = ImportanceFilterStrategy(importance_threshold=0.7)

        compressed, metadata = await strategy.compress(sample_messages)

        # Should keep only high-importance messages
        assert len(compressed) < len(sample_messages)
        assert all(msg.metadata.get("importance", 0) >= 0.7 for msg in compressed)

    async def test_filter_with_target_size(self, sample_messages):
        """Test filtering with target size limit."""
        strategy = ImportanceFilterStrategy(importance_threshold=0.5)

        compressed, metadata = await strategy.compress(sample_messages, target_size=3)

        assert len(compressed) == 3
        # Should be sorted by importance
        importances = [msg.metadata.get("importance", 0) for msg in compressed]
        assert importances == sorted(importances, reverse=True)


@pytest.mark.asyncio
class TestSummarizationStrategy:
    """Test suite for SummarizationStrategy."""

    async def test_summarization(self, sample_messages):
        """Test summarization strategy."""
        mock_llm = Mock()
        mock_llm.generate = AsyncMock(return_value="Summary of the conversation")

        strategy = SummarizationStrategy(mock_llm, summary_threshold=5)

        compressed, metadata = await strategy.compress(sample_messages, target_size=3)

        # Should have summary + recent messages
        assert len(compressed) == 4  # 1 summary + 3 recent
        assert compressed[0].message_type == "summary"
        assert compressed[0].role == MessageRole.SYSTEM
        assert metadata["compressed"] is True

    async def test_no_summarization_below_threshold(self, sample_messages):
        """Test no summarization when below threshold."""
        mock_llm = Mock()
        strategy = SummarizationStrategy(mock_llm, summary_threshold=20)

        compressed, metadata = await strategy.compress(sample_messages)

        # Should return original messages
        assert compressed == sample_messages
        assert metadata["compressed"] is False


@pytest.mark.asyncio
class TestMemoryCompressor:
    """Test suite for MemoryCompressor."""

    async def test_compress_conversation(self, mock_backend, sample_messages):
        """Test compressing a conversation."""
        conversation_id = uuid4()
        mock_backend.retrieve_messages.return_value = sample_messages

        strategy = TimeWindowStrategy(window_hours=1)
        compressor = MemoryCompressor(
            backend=mock_backend,
            strategy=strategy,
            auto_compress_threshold=5,
            target_size=3,
        )

        result = await compressor.compress_conversation(conversation_id, force=True)

        assert result["compressed"] is True
        assert mock_backend.clear_history.called
        assert mock_backend.store_message.called

    async def test_no_compress_below_threshold(self, mock_backend, sample_messages):
        """Test no compression below threshold."""
        conversation_id = uuid4()
        # Return fewer messages than threshold
        mock_backend.retrieve_messages.return_value = sample_messages[:3]

        compressor = MemoryCompressor(
            backend=mock_backend,
            auto_compress_threshold=10,
        )

        result = await compressor.compress_conversation(conversation_id, force=False)

        assert result["compressed"] is False
        assert result["reason"] == "below_threshold"

    async def test_force_compress(self, mock_backend, sample_messages):
        """Test forced compression."""
        conversation_id = uuid4()
        mock_backend.retrieve_messages.return_value = sample_messages[:3]

        strategy = TimeWindowStrategy(window_hours=1)
        compressor = MemoryCompressor(
            backend=mock_backend,
            strategy=strategy,
            auto_compress_threshold=10,
        )

        result = await compressor.compress_conversation(conversation_id, force=True)

        # Should compress even below threshold
        assert mock_backend.clear_history.called

    async def test_auto_compress(self, mock_backend, sample_messages):
        """Test automatic compression."""
        conversation_id = uuid4()
        mock_backend.retrieve_messages.return_value = sample_messages

        compressor = MemoryCompressor(
            backend=mock_backend,
            auto_compress_threshold=5,
        )

        compressed = await compressor.auto_compress(conversation_id)

        assert compressed is True

    async def test_compress_to_memory(self, mock_backend, sample_messages):
        """Test compressing conversation to memory entries."""
        conversation_id = uuid4()
        user_id = "test_user"

        # Give high importance to some messages
        for i in [0, 5, 9]:
            sample_messages[i].metadata["importance"] = 0.9

        mock_backend.retrieve_messages.return_value = sample_messages

        compressor = MemoryCompressor(backend=mock_backend)

        count = await compressor.compress_to_memory(
            conversation_id,
            user_id,
            importance_threshold=0.8,
        )

        assert count == 3
        assert mock_backend.store_memory.call_count == 3

    async def test_get_compression_stats(self, mock_backend, sample_messages):
        """Test getting compression statistics."""
        conversation_id = uuid4()
        mock_backend.retrieve_messages.return_value = sample_messages

        compressor = MemoryCompressor(backend=mock_backend, auto_compress_threshold=5)

        await compressor.compress_conversation(conversation_id, force=True)

        stats = await compressor.get_compression_stats(conversation_id)

        assert stats is not None
        assert "compressed" in stats
        assert "timestamp" in stats


@pytest.mark.asyncio
class TestAdaptiveCompressor:
    """Test suite for AdaptiveCompressor."""

    async def test_strategy_selection_with_importance(self, mock_backend, sample_messages):
        """Test strategy selection based on importance metadata."""
        conversation_id = uuid4()
        mock_backend.retrieve_messages.return_value = sample_messages

        compressor = AdaptiveCompressor(
            backend=mock_backend,
            auto_compress_threshold=5,
        )

        result = await compressor.compress_conversation(conversation_id, force=True)

        # Should select importance strategy since all messages have importance
        assert result["strategy_used"] == "importance"

    async def test_strategy_selection_default(self, mock_backend):
        """Test default strategy selection."""
        conversation_id = uuid4()

        # Messages without importance metadata
        messages = [
            Message(
                role=MessageRole.USER,
                content=f"Message {i}",
                timestamp=datetime.now(),
            )
            for i in range(10)
        ]

        mock_backend.retrieve_messages.return_value = messages

        compressor = AdaptiveCompressor(
            backend=mock_backend,
            auto_compress_threshold=5,
        )

        result = await compressor.compress_conversation(conversation_id, force=True)

        # Should use default time_window strategy
        assert result["strategy_used"] == "time_window"

    async def test_summarization_strategy_selection(self, mock_backend):
        """Test summarization strategy selection with LLM."""
        conversation_id = uuid4()

        # Many messages without importance
        messages = [
            Message(
                role=MessageRole.USER,
                content=f"Message {i}",
                timestamp=datetime.now(),
            )
            for i in range(35)
        ]

        mock_backend.retrieve_messages.return_value = messages

        mock_llm = Mock()
        mock_llm.generate = AsyncMock(return_value="Summary")

        compressor = AdaptiveCompressor(
            backend=mock_backend,
            llm_provider=mock_llm,
            auto_compress_threshold=10,
        )

        result = await compressor.compress_conversation(conversation_id, force=True)

        # Should select summarization for long conversations
        assert result["strategy_used"] == "summarization"
