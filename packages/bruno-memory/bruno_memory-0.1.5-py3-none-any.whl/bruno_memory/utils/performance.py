"""
Performance optimization utilities for bruno-memory.

Provides profiling, benchmarking, query optimization, and batch processing.
Uses standard library and proven external libraries where applicable.
"""

import functools
import logging
import statistics
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, TypeVar

try:
    import cProfile
    import io
    import pstats

    PROFILER_AVAILABLE = True
except ImportError:
    PROFILER_AVAILABLE = False

from bruno_core.models import Message

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""

    operation: str
    duration_ms: float
    memory_kb: float | None = None
    item_count: int | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def items_per_second(self) -> float | None:
        """Calculate throughput."""
        if self.item_count and self.duration_ms > 0:
            return (self.item_count / self.duration_ms) * 1000
        return None


class PerformanceMonitor:
    """
    Monitor and collect performance metrics.

    Tracks operation durations, throughput, and resource usage.
    """

    def __init__(self, max_metrics: int = 1000):
        """
        Initialize monitor.

        Args:
            max_metrics: Maximum metrics to keep in memory
        """
        self.metrics: list[PerformanceMetrics] = []
        self.max_metrics = max_metrics
        self.operation_stats: dict[str, list[float]] = defaultdict(list)
        logger.info("PerformanceMonitor initialized")

    def record(self, metrics: PerformanceMetrics) -> None:
        """
        Record performance metrics.

        Args:
            metrics: Metrics to record
        """
        self.metrics.append(metrics)
        self.operation_stats[metrics.operation].append(metrics.duration_ms)

        # Trim if needed
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics :]

        logger.debug(f"Performance: {metrics.operation} took {metrics.duration_ms:.2f}ms")

    def get_stats(self, operation: str | None = None) -> dict[str, Any]:
        """
        Get statistics for operations.

        Args:
            operation: Specific operation (None = all)

        Returns:
            Statistics dictionary
        """
        if operation:
            durations = self.operation_stats.get(operation, [])
            if not durations:
                return {}

            return {
                "operation": operation,
                "count": len(durations),
                "mean_ms": statistics.mean(durations),
                "median_ms": statistics.median(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "stdev_ms": statistics.stdev(durations) if len(durations) > 1 else 0,
            }

        # All operations
        return {op: self.get_stats(op) for op in self.operation_stats.keys()}

    def get_slow_operations(self, threshold_ms: float = 100) -> list[PerformanceMetrics]:
        """
        Find operations slower than threshold.

        Args:
            threshold_ms: Threshold in milliseconds

        Returns:
            List of slow operations
        """
        return [m for m in self.metrics if m.duration_ms > threshold_ms]

    def clear(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()
        self.operation_stats.clear()
        logger.info("Performance metrics cleared")


def profile_function(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to profile function execution.

    Uses cProfile for detailed profiling.

    Args:
        func: Function to profile

    Returns:
        Wrapped function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        if not PROFILER_AVAILABLE:
            logger.warning("cProfile not available, skipping profiling")
            return func(*args, **kwargs)

        profiler = cProfile.Profile()
        profiler.enable()

        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()

            # Print stats
            s = io.StringIO()
            stats = pstats.Stats(profiler, stream=s)
            stats.sort_stats("cumulative")
            stats.print_stats(20)  # Top 20 functions

            logger.info(f"Profile for {func.__name__}:\n{s.getvalue()}")

        return result

    return wrapper


def time_operation(operation_name: str, monitor: PerformanceMonitor | None = None) -> Callable:
    """
    Decorator to time operation execution.

    Args:
        operation_name: Name of operation
        monitor: Optional monitor to record metrics

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = (time.perf_counter() - start) * 1000  # ms

            metrics = PerformanceMetrics(operation=operation_name, duration_ms=duration)

            if monitor:
                monitor.record(metrics)
            else:
                logger.debug(f"{operation_name} took {duration:.2f}ms")

            return result

        return wrapper

    return decorator


class BatchProcessor:
    """
    Process items in optimized batches.

    Improves performance for bulk operations.
    """

    def __init__(self, batch_size: int = 100):
        """
        Initialize batch processor.

        Args:
            batch_size: Number of items per batch
        """
        self.batch_size = batch_size
        logger.info(f"BatchProcessor initialized: batch_size={batch_size}")

    def process_batches(self, items: list[T], processor: Callable[[list[T]], None]) -> None:
        """
        Process items in batches.

        Args:
            items: Items to process
            processor: Function to process each batch
        """
        total = len(items)
        for i in range(0, total, self.batch_size):
            batch = items[i : i + self.batch_size]
            processor(batch)

            if (i + self.batch_size) % (self.batch_size * 10) == 0:
                logger.info(f"Processed {i + self.batch_size}/{total} items")

    def batch_messages(self, messages: list[Message]) -> list[list[Message]]:
        """
        Split messages into batches.

        Args:
            messages: Messages to batch

        Returns:
            List of message batches
        """
        return [messages[i : i + self.batch_size] for i in range(0, len(messages), self.batch_size)]


class QueryOptimizer:
    """
    Optimize database queries.

    Provides query analysis and optimization suggestions.
    """

    def __init__(self):
        """Initialize query optimizer."""
        self.slow_queries: list[dict[str, Any]] = []
        self.query_patterns: dict[str, int] = defaultdict(int)
        logger.info("QueryOptimizer initialized")

    def analyze_query(
        self, query: str, duration_ms: float, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Analyze a query execution.

        Args:
            query: SQL query or operation
            duration_ms: Execution time
            params: Query parameters

        Returns:
            Analysis results
        """
        # Track query pattern
        pattern = self._extract_pattern(query)
        self.query_patterns[pattern] += 1

        # Track slow queries
        if duration_ms > 100:  # 100ms threshold
            self.slow_queries.append(
                {
                    "query": query,
                    "pattern": pattern,
                    "duration_ms": duration_ms,
                    "params": params,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        return {
            "pattern": pattern,
            "is_slow": duration_ms > 100,
            "suggestions": self._get_suggestions(query, duration_ms),
        }

    def _extract_pattern(self, query: str) -> str:
        """Extract query pattern (remove values)."""
        # Simple pattern extraction - replace values with placeholders
        import re

        # Remove string literals
        pattern = re.sub(r"'[^']*'", "?", query)
        # Remove numbers
        pattern = re.sub(r"\b\d+\b", "?", pattern)
        # Normalize whitespace
        pattern = " ".join(pattern.split())

        return pattern

    def _get_suggestions(self, query: str, duration_ms: float) -> list[str]:
        """Get optimization suggestions."""
        suggestions = []

        if duration_ms > 100:
            suggestions.append("Consider adding indexes for filtered columns")

        if "SELECT *" in query.upper():
            suggestions.append("Select only needed columns instead of *")

        if query.upper().count("JOIN") > 3:
            suggestions.append("Consider denormalization for complex joins")

        if "ORDER BY" in query.upper() and "LIMIT" not in query.upper():
            suggestions.append("Add LIMIT clause when ordering results")

        return suggestions

    def get_slow_queries(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get slowest queries.

        Args:
            limit: Maximum number to return

        Returns:
            List of slow queries
        """
        sorted_queries = sorted(self.slow_queries, key=lambda q: q["duration_ms"], reverse=True)
        return sorted_queries[:limit]

    def get_frequent_patterns(self, limit: int = 10) -> list[tuple[str, int]]:
        """
        Get most frequent query patterns.

        Args:
            limit: Maximum number to return

        Returns:
            List of (pattern, count) tuples
        """
        sorted_patterns = sorted(self.query_patterns.items(), key=lambda x: x[1], reverse=True)
        return sorted_patterns[:limit]


class CacheWarmer:
    """
    Pre-warm caches for improved performance.

    Loads frequently accessed data into cache before it's needed.
    """

    def __init__(self, cache_ttl: timedelta = timedelta(hours=1)):
        """
        Initialize cache warmer.

        Args:
            cache_ttl: Cache time-to-live
        """
        self.cache_ttl = cache_ttl
        self.warmed_at: dict[str, datetime] = {}
        logger.info(f"CacheWarmer initialized: ttl={cache_ttl}")

    def should_warm(self, cache_key: str) -> bool:
        """
        Check if cache should be warmed.

        Args:
            cache_key: Cache identifier

        Returns:
            True if warming needed
        """
        if cache_key not in self.warmed_at:
            return True

        age = datetime.utcnow() - self.warmed_at[cache_key]
        return age > self.cache_ttl

    def mark_warmed(self, cache_key: str) -> None:
        """
        Mark cache as warmed.

        Args:
            cache_key: Cache identifier
        """
        self.warmed_at[cache_key] = datetime.utcnow()
        logger.debug(f"Cache warmed: {cache_key}")

    def warm_user_data(self, user_id: str, loader: Callable[[str], Any]) -> Any:
        """
        Warm cache for user data.

        Args:
            user_id: User identifier
            loader: Function to load data

        Returns:
            Loaded data
        """
        cache_key = f"user:{user_id}"

        if not self.should_warm(cache_key):
            logger.debug(f"Cache still fresh: {cache_key}")
            return None

        data = loader(user_id)
        self.mark_warmed(cache_key)

        return data


# Convenience functions
def benchmark_operation(
    func: Callable[..., T], *args, iterations: int = 10, **kwargs
) -> dict[str, Any]:
    """
    Benchmark a function.

    Args:
        func: Function to benchmark
        iterations: Number of iterations
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Benchmark results
    """
    durations = []

    for _ in range(iterations):
        start = time.perf_counter()
        func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000
        durations.append(duration)

    return {
        "function": func.__name__,
        "iterations": iterations,
        "mean_ms": statistics.mean(durations),
        "median_ms": statistics.median(durations),
        "min_ms": min(durations),
        "max_ms": max(durations),
        "stdev_ms": statistics.stdev(durations) if len(durations) > 1 else 0,
    }
