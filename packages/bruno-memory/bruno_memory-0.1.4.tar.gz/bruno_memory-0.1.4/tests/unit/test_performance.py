"""
Tests for performance optimization utilities.
"""

import time
from datetime import datetime, timedelta

import pytest
from bruno_core.models import MemoryEntry, Message

from bruno_memory.utils.performance import (
    BatchProcessor,
    CacheWarmer,
    PerformanceMetrics,
    PerformanceMonitor,
    QueryOptimizer,
    benchmark_operation,
    profile_function,
    time_operation,
)


@pytest.fixture
def monitor():
    """Create performance monitor."""
    return PerformanceMonitor()


@pytest.fixture
def sample_messages():
    """Create sample messages."""
    return [Message(role="user", content=f"Message {i}", metadata={"index": i}) for i in range(100)]


class TestPerformanceMetrics:
    """Test performance metrics data class."""

    def test_create_metrics(self):
        """Test creating metrics."""
        metrics = PerformanceMetrics(operation="test_op", duration_ms=100.5, item_count=50)

        assert metrics.operation == "test_op"
        assert metrics.duration_ms == 100.5
        assert metrics.item_count == 50

    def test_items_per_second(self):
        """Test throughput calculation."""
        metrics = PerformanceMetrics(
            operation="test_op", duration_ms=1000, item_count=100  # 1 second
        )

        # 100 items in 1 second = 100 items/sec
        assert metrics.items_per_second == 100.0

    def test_items_per_second_none(self):
        """Test throughput with missing data."""
        metrics = PerformanceMetrics(operation="test_op", duration_ms=100)

        # No item_count
        assert metrics.items_per_second is None


class TestPerformanceMonitor:
    """Test performance monitoring."""

    def test_record_metrics(self, monitor):
        """Test recording metrics."""
        metrics = PerformanceMetrics(operation="test_op", duration_ms=50.0)

        monitor.record(metrics)

        assert len(monitor.metrics) == 1
        assert monitor.operation_stats["test_op"] == [50.0]

    def test_get_stats_single_operation(self, monitor):
        """Test getting statistics for operation."""
        # Record multiple measurements
        for duration in [10, 20, 30, 40, 50]:
            metrics = PerformanceMetrics(operation="test_op", duration_ms=float(duration))
            monitor.record(metrics)

        stats = monitor.get_stats("test_op")

        assert stats["count"] == 5
        assert stats["mean_ms"] == 30.0
        assert stats["median_ms"] == 30.0
        assert stats["min_ms"] == 10.0
        assert stats["max_ms"] == 50.0

    def test_get_stats_all_operations(self, monitor):
        """Test getting all operation statistics."""
        monitor.record(PerformanceMetrics("op1", duration_ms=10))
        monitor.record(PerformanceMetrics("op2", duration_ms=20))
        monitor.record(PerformanceMetrics("op1", duration_ms=15))

        all_stats = monitor.get_stats()

        assert "op1" in all_stats
        assert "op2" in all_stats
        assert all_stats["op1"]["count"] == 2
        assert all_stats["op2"]["count"] == 1

    def test_get_slow_operations(self, monitor):
        """Test finding slow operations."""
        monitor.record(PerformanceMetrics("fast_op", duration_ms=50))
        monitor.record(PerformanceMetrics("slow_op", duration_ms=150))
        monitor.record(PerformanceMetrics("very_slow_op", duration_ms=300))

        slow = monitor.get_slow_operations(threshold_ms=100)

        assert len(slow) == 2
        assert all(m.duration_ms > 100 for m in slow)

    def test_max_metrics_limit(self):
        """Test metrics trimming."""
        monitor = PerformanceMonitor(max_metrics=10)

        # Record more than max
        for i in range(20):
            monitor.record(PerformanceMetrics("op", duration_ms=float(i)))

        # Should trim to max
        assert len(monitor.metrics) == 10

    def test_clear(self, monitor):
        """Test clearing metrics."""
        monitor.record(PerformanceMetrics("op", duration_ms=10))
        monitor.clear()

        assert len(monitor.metrics) == 0
        assert len(monitor.operation_stats) == 0


class TestDecorators:
    """Test performance decorators."""

    def test_time_operation_decorator(self, monitor):
        """Test time_operation decorator."""

        @time_operation("test_func", monitor)
        def slow_function():
            time.sleep(0.01)  # 10ms
            return "done"

        result = slow_function()

        assert result == "done"
        assert len(monitor.metrics) == 1
        assert monitor.metrics[0].operation == "test_func"
        assert monitor.metrics[0].duration_ms >= 10

    def test_time_operation_without_monitor(self):
        """Test time_operation without monitor."""

        @time_operation("test_func")
        def fast_function():
            return "done"

        # Should work without crashing
        result = fast_function()
        assert result == "done"

    def test_profile_function_decorator(self):
        """Test profile_function decorator."""

        @profile_function
        def example_function():
            # Some work
            total = 0
            for i in range(100):
                total += i
            return total

        # Should work (profiling output goes to logs)
        result = example_function()
        assert result == sum(range(100))


class TestBatchProcessor:
    """Test batch processing."""

    def test_batch_messages(self, sample_messages):
        """Test splitting messages into batches."""
        processor = BatchProcessor(batch_size=25)

        batches = processor.batch_messages(sample_messages)

        assert len(batches) == 4  # 100 messages / 25 per batch
        assert len(batches[0]) == 25
        assert len(batches[-1]) == 25

    def test_process_batches(self, sample_messages):
        """Test processing with batch function."""
        processor = BatchProcessor(batch_size=20)
        processed = []

        def batch_processor(batch):
            processed.extend(batch)

        processor.process_batches(sample_messages, batch_processor)

        assert len(processed) == 100
        assert processed == sample_messages

    def test_partial_batch(self):
        """Test handling partial last batch."""
        processor = BatchProcessor(batch_size=30)
        messages = [Message(role="user", content=str(i)) for i in range(50)]

        batches = processor.batch_messages(messages)

        assert len(batches) == 2
        assert len(batches[0]) == 30
        assert len(batches[1]) == 20  # Partial batch


class TestQueryOptimizer:
    """Test query optimization."""

    def test_analyze_query(self):
        """Test query analysis."""
        optimizer = QueryOptimizer()

        query = "SELECT * FROM messages WHERE user_id = 'user123'"
        analysis = optimizer.analyze_query(query, duration_ms=50)

        assert "pattern" in analysis
        assert "is_slow" in analysis
        assert "suggestions" in analysis

    def test_slow_query_detection(self):
        """Test slow query tracking."""
        optimizer = QueryOptimizer()

        slow_query = "SELECT * FROM messages ORDER BY timestamp"
        optimizer.analyze_query(slow_query, duration_ms=150)

        slow_queries = optimizer.get_slow_queries()

        assert len(slow_queries) >= 1
        assert slow_queries[0]["duration_ms"] == 150

    def test_query_pattern_extraction(self):
        """Test extracting query patterns."""
        optimizer = QueryOptimizer()

        # Same pattern, different values
        optimizer.analyze_query("SELECT * FROM messages WHERE id = '1'", 10)
        optimizer.analyze_query("SELECT * FROM messages WHERE id = '2'", 10)
        optimizer.analyze_query("SELECT * FROM messages WHERE id = '3'", 10)

        patterns = optimizer.get_frequent_patterns()

        # Should recognize as same pattern
        assert len(patterns) >= 1
        assert patterns[0][1] == 3  # Count of 3

    def test_optimization_suggestions(self):
        """Test getting optimization suggestions."""
        optimizer = QueryOptimizer()

        # Query with SELECT *
        analysis = optimizer.analyze_query(
            "SELECT * FROM messages WHERE user_id = 'user123'", duration_ms=50
        )

        suggestions = analysis["suggestions"]
        assert any("columns" in s.lower() for s in suggestions)

    def test_get_frequent_patterns(self):
        """Test getting frequent query patterns."""
        optimizer = QueryOptimizer()

        # Record multiple queries
        for i in range(5):
            optimizer.analyze_query(f"SELECT content FROM messages WHERE id = '{i}'", 10)

        for i in range(3):
            optimizer.analyze_query(f"DELETE FROM messages WHERE id = '{i}'", 5)

        patterns = optimizer.get_frequent_patterns(limit=2)

        assert len(patterns) <= 2
        # Most frequent should be first
        assert patterns[0][1] >= patterns[1][1]


class TestCacheWarmer:
    """Test cache warming."""

    def test_should_warm_first_time(self):
        """Test warming on first access."""
        warmer = CacheWarmer()

        assert warmer.should_warm("user:123")

    def test_should_not_warm_if_fresh(self):
        """Test skip warming if cache fresh."""
        warmer = CacheWarmer(cache_ttl=timedelta(hours=1))

        warmer.mark_warmed("user:123")

        # Should not warm immediately
        assert not warmer.should_warm("user:123")

    def test_should_warm_after_ttl(self):
        """Test warming after TTL expires."""
        warmer = CacheWarmer(cache_ttl=timedelta(seconds=0))

        warmer.mark_warmed("user:123")
        time.sleep(0.01)  # Small delay

        # Should warm after TTL
        assert warmer.should_warm("user:123")

    def test_warm_user_data(self):
        """Test warming user data."""
        warmer = CacheWarmer()

        def load_data(user_id):
            return f"data_for_{user_id}"

        data = warmer.warm_user_data("user123", load_data)

        assert data == "data_for_user123"
        assert not warmer.should_warm("user:user123")

    def test_warm_skip_if_fresh(self):
        """Test skipping load if fresh."""
        warmer = CacheWarmer()

        def load_data(user_id):
            return f"data_for_{user_id}"

        # First warm
        warmer.warm_user_data("user123", load_data)

        # Second should skip
        result = warmer.warm_user_data("user123", load_data)
        assert result is None  # Skipped loading


class TestBenchmarking:
    """Test benchmarking utilities."""

    def test_benchmark_operation(self):
        """Test benchmarking a function."""

        def simple_func(x):
            return x * 2

        results = benchmark_operation(simple_func, 5, iterations=10)

        assert results["function"] == "simple_func"
        assert results["iterations"] == 10
        assert "mean_ms" in results
        assert "median_ms" in results
        assert "min_ms" in results
        assert "max_ms" in results

    def test_benchmark_with_kwargs(self):
        """Test benchmarking with keyword arguments."""

        def func_with_kwargs(x, y=10):
            return x + y

        results = benchmark_operation(func_with_kwargs, 5, y=20, iterations=5)

        assert results["iterations"] == 5
        assert results["mean_ms"] >= 0


class TestIntegration:
    """Test integration scenarios."""

    def test_monitor_batch_processing(self, sample_messages, monitor):
        """Test monitoring batch processing."""
        processor = BatchProcessor(batch_size=25)

        @time_operation("batch_process", monitor)
        def process_batch(messages):
            # Simulate processing
            return len(messages)

        batches = processor.batch_messages(sample_messages)
        for batch in batches:
            process_batch(batch)

        # Should have metrics for each batch
        assert len(monitor.metrics) == 4

        stats = monitor.get_stats("batch_process")
        assert stats["count"] == 4

    def test_cache_with_monitoring(self, monitor):
        """Test cache warming with performance monitoring."""
        warmer = CacheWarmer()

        @time_operation("cache_load", monitor)
        def load_data(user_id):
            time.sleep(0.01)  # Simulate slow load
            return f"data_{user_id}"

        # First load (slow)
        warmer.warm_user_data("user123", load_data)

        # Second load (skipped)
        warmer.warm_user_data("user123", load_data)

        # Only one slow load should be recorded
        assert len(monitor.metrics) <= 1
