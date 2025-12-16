"""Tests for analytics utilities."""

from datetime import datetime, timedelta, timezone

import pytest
from bruno_core.models import (
    MemoryEntry,
    MemoryMetadata,
    MemoryType,
    Message,
    MessageRole,
    MessageType,
)

from bruno_memory.utils.analytics import (
    MemoryAnalytics,
    PerformanceTracker,
    quick_analyze,
)


@pytest.fixture
def sample_messages():
    """Create sample messages with timestamps."""
    base_time = datetime.now(timezone.utc)

    return [
        Message(
            content="Hello, how can you help me?",
            role=MessageRole.USER,
            message_type=MessageType.TEXT,
            timestamp=base_time,
        ),
        Message(
            content="I can help you with many things!",
            role=MessageRole.ASSISTANT,
            message_type=MessageType.TEXT,
            timestamp=base_time + timedelta(seconds=2),
        ),
        Message(
            content="Tell me about Python",
            role=MessageRole.USER,
            message_type=MessageType.TEXT,
            timestamp=base_time + timedelta(seconds=5),
        ),
        Message(
            content="Python is a high-level programming language...",
            role=MessageRole.ASSISTANT,
            message_type=MessageType.TEXT,
            timestamp=base_time + timedelta(seconds=8),
        ),
    ]


@pytest.fixture
def sample_memories():
    """Create sample memories."""
    return [
        MemoryEntry(
            content="User prefers Python over JavaScript",
            memory_type=MemoryType.FACT,
            user_id="user1",
            metadata=MemoryMetadata(
                importance=0.8,
                tags={"python", "preferences"},
            ),
        ),
        MemoryEntry(
            content="Previous discussion about web development",
            memory_type=MemoryType.EPISODIC,
            user_id="user1",
            metadata=MemoryMetadata(
                importance=0.6,
                tags={"web", "development"},
            ),
        ),
        MemoryEntry(
            content="User works as a data scientist",
            memory_type=MemoryType.FACT,
            user_id="user1",
            metadata=MemoryMetadata(
                importance=0.9,
                tags={"career", "data"},
            ),
        ),
        MemoryEntry(
            content="Another user's preference",
            memory_type=MemoryType.FACT,
            user_id="user2",
            metadata=MemoryMetadata(
                importance=0.5,
                tags={"preferences"},
            ),
        ),
    ]


class TestMemoryAnalytics:
    """Tests for MemoryAnalytics."""

    def test_initialization(self):
        """Test analytics initialization."""
        analytics = MemoryAnalytics()
        assert analytics._metrics == {}

    def test_analyze_messages_basic(self, sample_messages):
        """Test basic message analysis."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_messages(sample_messages)

        assert result["total_messages"] == 4
        assert "user" in result["role_distribution"]
        assert "assistant" in result["role_distribution"]
        assert result["role_distribution"]["user"] == 2
        assert result["role_distribution"]["assistant"] == 2

    def test_analyze_messages_content_length(self, sample_messages):
        """Test content length analysis."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_messages(sample_messages)

        assert "content_length" in result
        assert result["content_length"]["average"] > 0
        assert result["content_length"]["min"] > 0
        assert result["content_length"]["max"] > 0

    def test_analyze_messages_temporal(self, sample_messages):
        """Test temporal analysis."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_messages(sample_messages)

        assert "temporal" in result
        assert result["temporal"]["first_message"] is not None
        assert result["temporal"]["last_message"] is not None
        assert result["temporal"]["duration_seconds"] > 0

    def test_analyze_empty_messages(self):
        """Test analyzing empty message list."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_messages([])

        assert result["total_messages"] == 0
        assert "error" in result

    def test_analyze_memories_basic(self, sample_memories):
        """Test basic memory analysis."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_memories(sample_memories)

        assert result["total_memories"] == 4
        assert "fact" in result["memory_types"]
        assert "episodic" in result["memory_types"]
        assert result["memory_types"]["fact"] == 3
        assert result["memory_types"]["episodic"] == 1

    def test_analyze_memories_users(self, sample_memories):
        """Test user distribution analysis."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_memories(sample_memories)

        assert "user_distribution" in result
        assert result["user_distribution"]["user1"] == 3
        assert result["user_distribution"]["user2"] == 1

    def test_analyze_memories_importance(self, sample_memories):
        """Test importance analysis."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_memories(sample_memories)

        assert "importance" in result
        assert result["importance"]["average"] is not None
        assert 0 < result["importance"]["average"] <= 1
        assert result["importance"]["samples"] == 4

    def test_analyze_memories_tags(self, sample_memories):
        """Test tag analysis."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_memories(sample_memories)

        assert "tags" in result
        assert result["tags"]["total_tags"] > 0
        assert result["tags"]["unique_tags"] > 0
        assert "preferences" in result["tags"]["top_tags"]

    def test_analyze_empty_memories(self):
        """Test analyzing empty memory list."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_memories([])

        assert result["total_memories"] == 0
        assert "error" in result

    def test_analyze_conversation_flow(self, sample_messages):
        """Test conversation flow analysis."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_conversation_flow(sample_messages)

        assert "total_exchanges" in result
        assert result["total_exchanges"] == 3  # 4 messages = 3 transitions
        assert "transition_patterns" in result
        assert "response_times" in result

    def test_analyze_conversation_flow_response_times(self, sample_messages):
        """Test response time calculation."""
        analytics = MemoryAnalytics()
        result = analytics.analyze_conversation_flow(sample_messages)

        assert result["response_times"]["average_seconds"] is not None
        assert result["response_times"]["samples"] == 3
        assert result["response_times"]["min_seconds"] is not None
        assert result["response_times"]["max_seconds"] is not None

    def test_analyze_conversation_flow_insufficient_messages(self):
        """Test flow analysis with insufficient messages."""
        analytics = MemoryAnalytics()

        message = Message(
            content="Hello",
            role=MessageRole.USER,
            message_type=MessageType.TEXT,
        )

        result = analytics.analyze_conversation_flow([message])
        assert "error" in result

    def test_analyze_with_pandas(self, sample_messages):
        """Test pandas DataFrame creation."""
        try:
            import pandas as pd

            analytics = MemoryAnalytics()
            df = analytics.analyze_with_pandas(sample_messages)

            if df is not None:  # pandas available
                assert len(df) == 4
                assert "content_length" in df.columns
                assert "role" in df.columns
                assert "hour" in df.columns  # Derived column

        except ImportError:
            pytest.skip("pandas not available")

    def test_generate_report_messages_only(self, sample_messages):
        """Test report generation with messages only."""
        analytics = MemoryAnalytics()
        report = analytics.generate_report(messages=sample_messages)

        assert "generated_at" in report
        assert "messages" in report
        assert "conversation_flow" in report

    def test_generate_report_memories_only(self, sample_memories):
        """Test report generation with memories only."""
        analytics = MemoryAnalytics()
        report = analytics.generate_report(memories=sample_memories)

        assert "generated_at" in report
        assert "memories" in report

    def test_generate_report_comprehensive(self, sample_messages, sample_memories):
        """Test comprehensive report generation."""
        analytics = MemoryAnalytics()
        report = analytics.generate_report(messages=sample_messages, memories=sample_memories)

        assert "generated_at" in report
        assert "messages" in report
        assert "memories" in report
        assert "conversation_flow" in report

    def test_track_metric(self):
        """Test metric tracking."""
        analytics = MemoryAnalytics()

        analytics.track_metric("test_metric", 42)
        analytics.track_metric("test_metric", 84)

        metrics = analytics.get_metrics()
        assert "test_metric" in metrics
        assert len(metrics["test_metric"]) == 2
        assert metrics["test_metric"][0]["value"] == 42

    def test_clear_metrics(self):
        """Test clearing metrics."""
        analytics = MemoryAnalytics()

        analytics.track_metric("test", 1)
        analytics.clear_metrics()

        metrics = analytics.get_metrics()
        assert len(metrics) == 0


class TestPerformanceTracker:
    """Tests for PerformanceTracker."""

    def test_initialization(self):
        """Test tracker initialization."""
        tracker = PerformanceTracker()
        assert tracker._operations == []

    def test_record_operation(self):
        """Test recording operations."""
        tracker = PerformanceTracker()

        tracker.record_operation("store_message", 25.5, True)
        tracker.record_operation("retrieve_messages", 15.2, True)

        assert len(tracker._operations) == 2

    def test_record_operation_with_metadata(self):
        """Test recording with metadata."""
        tracker = PerformanceTracker()

        tracker.record_operation(
            "store_message", 25.5, True, {"backend": "sqlite", "message_count": 100}
        )

        assert tracker._operations[0]["metadata"]["backend"] == "sqlite"

    def test_get_statistics(self):
        """Test getting statistics."""
        tracker = PerformanceTracker()

        # Record multiple operations
        tracker.record_operation("store", 10.0, True)
        tracker.record_operation("store", 20.0, True)
        tracker.record_operation("retrieve", 5.0, True)

        stats = tracker.get_statistics()

        assert "overall" in stats
        assert stats["overall"]["total_operations"] == 3
        assert stats["overall"]["success_rate"] == 100.0

        assert "by_operation" in stats
        assert "store" in stats["by_operation"]
        assert stats["by_operation"]["store"]["count"] == 2
        assert stats["by_operation"]["store"]["avg_ms"] == 15.0

    def test_get_statistics_with_failures(self):
        """Test statistics with failed operations."""
        tracker = PerformanceTracker()

        tracker.record_operation("store", 10.0, True)
        tracker.record_operation("store", 20.0, False)  # Failed

        stats = tracker.get_statistics()
        assert stats["overall"]["success_rate"] == 50.0

    def test_get_statistics_empty(self):
        """Test statistics with no operations."""
        tracker = PerformanceTracker()

        stats = tracker.get_statistics()
        assert "error" in stats

    def test_clear_operations(self):
        """Test clearing operations."""
        tracker = PerformanceTracker()

        tracker.record_operation("test", 10.0, True)
        tracker.clear()

        assert len(tracker._operations) == 0


class TestQuickUtilities:
    """Tests for quick utility functions."""

    def test_quick_analyze(self, sample_messages):
        """Test quick analyze function."""
        result = quick_analyze(sample_messages)

        assert "total_messages" in result
        assert result["total_messages"] == 4
        assert "role_distribution" in result
