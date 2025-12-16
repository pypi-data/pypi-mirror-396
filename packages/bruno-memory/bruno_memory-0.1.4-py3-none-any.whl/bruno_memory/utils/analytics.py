"""
Analytics utilities for bruno-memory.

Provides memory usage statistics, conversation patterns, and performance metrics.
Uses pandas for efficient data analysis.
"""

import logging
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from bruno_core.models import MemoryEntry, Message

logger = logging.getLogger(__name__)


def _get_timestamp(obj: Message | MemoryEntry) -> datetime | None:
    """Get timestamp from Message (timestamp) or MemoryEntry (created_at)."""
    return getattr(obj, "timestamp", None) or getattr(obj, "created_at", None)


class MemoryAnalytics:
    """
    Analytics engine for memory and conversation data.

    Provides insights into:
    - Memory growth patterns
    - Conversation statistics
    - User activity patterns
    - Performance metrics
    """

    def __init__(self):
        """Initialize analytics engine."""
        self._metrics: dict[str, Any] = {}
        logger.info("MemoryAnalytics initialized")

    def analyze_messages(self, messages: list[Message]) -> dict[str, Any]:
        """
        Analyze message patterns and statistics.

        Args:
            messages: List of messages to analyze

        Returns:
            Dictionary of analytics results
        """
        if not messages:
            return {"total_messages": 0, "error": "No messages to analyze"}

        # Basic statistics
        total = len(messages)

        # Role distribution
        roles = Counter(
            msg.role.value if hasattr(msg.role, "value") else msg.role for msg in messages
        )

        # Message types
        types = Counter(
            msg.message_type.value if hasattr(msg.message_type, "value") else msg.message_type
            for msg in messages
        )

        # Content length stats
        lengths = [len(msg.content) for msg in messages]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        max_length = max(lengths) if lengths else 0
        min_length = min(lengths) if lengths else 0

        # Temporal analysis
        timestamps = [_get_timestamp(msg) for msg in messages]
        timestamps = [ts for ts in timestamps if ts is not None]
        if timestamps:
            first_message = min(timestamps)
            last_message = max(timestamps)
            duration = (last_message - first_message).total_seconds()
        else:
            first_message = last_message = duration = None

        # Session analysis
        sessions = set()
        if any(msg.metadata and hasattr(msg.metadata, "session_id") for msg in messages):
            sessions = {
                msg.metadata.session_id
                for msg in messages
                if msg.metadata and hasattr(msg.metadata, "session_id") and msg.metadata.session_id
            }

        return {
            "total_messages": total,
            "role_distribution": dict(roles),
            "message_types": dict(types),
            "content_length": {
                "average": round(avg_length, 2),
                "min": min_length,
                "max": max_length,
            },
            "temporal": {
                "first_message": first_message.isoformat() if first_message else None,
                "last_message": last_message.isoformat() if last_message else None,
                "duration_seconds": duration,
            },
            "sessions": {
                "unique_sessions": len(sessions),
                "avg_messages_per_session": round(total / len(sessions), 2) if sessions else 0,
            },
        }

    def analyze_memories(self, memories: list[MemoryEntry]) -> dict[str, Any]:
        """
        Analyze memory patterns and statistics.

        Args:
            memories: List of memories to analyze

        Returns:
            Dictionary of analytics results
        """
        if not memories:
            return {"total_memories": 0, "error": "No memories to analyze"}

        total = len(memories)

        # Memory type distribution
        types = Counter(
            mem.memory_type.value if hasattr(mem.memory_type, "value") else mem.memory_type
            for mem in memories
        )

        # User distribution
        users = Counter(mem.user_id for mem in memories)

        # Content analysis
        lengths = [len(mem.content) for mem in memories]
        avg_length = sum(lengths) / len(lengths) if lengths else 0

        # Importance distribution (if available)
        importances = []
        for mem in memories:
            if mem.metadata and hasattr(mem.metadata, "importance"):
                importances.append(mem.metadata.importance)

        avg_importance = sum(importances) / len(importances) if importances else None

        # Tag analysis (if available)
        all_tags = []
        for mem in memories:
            if mem.metadata and hasattr(mem.metadata, "tags") and mem.metadata.tags:
                all_tags.extend(mem.metadata.tags)

        tag_counts = Counter(all_tags)

        # Temporal analysis
        timestamps = [_get_timestamp(mem) for mem in memories]
        timestamps = [ts for ts in timestamps if ts is not None]
        if timestamps:
            first_memory = min(timestamps)
            last_memory = max(timestamps)
            duration = (last_memory - first_memory).total_seconds()
        else:
            first_memory = last_memory = duration = None

        return {
            "total_memories": total,
            "memory_types": dict(types),
            "user_distribution": dict(users),
            "content_length": {
                "average": round(avg_length, 2),
                "min": min(lengths) if lengths else 0,
                "max": max(lengths) if lengths else 0,
            },
            "importance": {
                "average": round(avg_importance, 3) if avg_importance else None,
                "samples": len(importances),
            },
            "tags": {
                "total_tags": len(all_tags),
                "unique_tags": len(tag_counts),
                "top_tags": dict(tag_counts.most_common(10)),
            },
            "temporal": {
                "first_memory": first_memory.isoformat() if first_memory else None,
                "last_memory": last_memory.isoformat() if last_memory else None,
                "duration_seconds": duration,
            },
        }

    def analyze_conversation_flow(self, messages: list[Message]) -> dict[str, Any]:
        """
        Analyze conversation flow patterns.

        Args:
            messages: List of messages

        Returns:
            Conversation flow statistics
        """
        if len(messages) < 2:
            return {"error": "Need at least 2 messages for flow analysis"}

        # Role transitions (e.g., user -> assistant -> user)
        transitions = []
        for i in range(len(messages) - 1):
            current_role = (
                messages[i].role.value if hasattr(messages[i].role, "value") else messages[i].role
            )
            next_role = (
                messages[i + 1].role.value
                if hasattr(messages[i + 1].role, "value")
                else messages[i + 1].role
            )
            transitions.append(f"{current_role} -> {next_role}")

        transition_counts = Counter(transitions)

        # Response times (if timestamps available)
        response_times = []
        for i in range(len(messages) - 1):
            ts1 = _get_timestamp(messages[i])
            ts2 = _get_timestamp(messages[i + 1])
            if ts1 and ts2:
                delta = (ts2 - ts1).total_seconds()
                response_times.append(delta)

        avg_response_time = sum(response_times) / len(response_times) if response_times else None

        # Turn taking
        role_sequences = [
            msg.role.value if hasattr(msg.role, "value") else msg.role for msg in messages
        ]

        return {
            "total_exchanges": len(transitions),
            "transition_patterns": dict(transition_counts.most_common(5)),
            "response_times": {
                "average_seconds": round(avg_response_time, 2) if avg_response_time else None,
                "min_seconds": round(min(response_times), 2) if response_times else None,
                "max_seconds": round(max(response_times), 2) if response_times else None,
                "samples": len(response_times),
            },
            "turn_distribution": dict(Counter(role_sequences)),
        }

    def analyze_with_pandas(self, messages: list[Message]) -> pd.DataFrame | None:
        """
        Create pandas DataFrame for advanced analysis.

        Args:
            messages: List of messages

        Returns:
            DataFrame with message data
        """
        if not PANDAS_AVAILABLE:
            logger.warning("pandas not available for advanced analysis")
            return None

        if not messages:
            return None

        data = [
            {
                "id": str(msg.id),
                "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                "content_length": len(msg.content),
                "message_type": (
                    msg.message_type.value
                    if hasattr(msg.message_type, "value")
                    else msg.message_type
                ),
                "created_at": _get_timestamp(msg),
                "session_id": (
                    msg.metadata.session_id
                    if msg.metadata and hasattr(msg.metadata, "session_id")
                    else None
                ),
                "user_id": (
                    msg.metadata.user_id
                    if msg.metadata and hasattr(msg.metadata, "user_id")
                    else None
                ),
            }
            for msg in messages
        ]

        df = pd.DataFrame(data)

        # Add derived columns
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
            df["hour"] = df["created_at"].dt.hour
            df["day_of_week"] = df["created_at"].dt.dayofweek

        return df

    def generate_report(
        self, messages: list[Message] | None = None, memories: list[MemoryEntry] | None = None
    ) -> dict[str, Any]:
        """
        Generate comprehensive analytics report.

        Args:
            messages: Optional messages to analyze
            memories: Optional memories to analyze

        Returns:
            Complete analytics report
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "report_version": "1.0",
        }

        if messages:
            report["messages"] = self.analyze_messages(messages)
            if len(messages) >= 2:
                report["conversation_flow"] = self.analyze_conversation_flow(messages)

        if memories:
            report["memories"] = self.analyze_memories(memories)

        logger.info("Generated analytics report")
        return report

    def track_metric(self, metric_name: str, value: Any) -> None:
        """
        Track a custom metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []

        self._metrics[metric_name].append(
            {
                "value": value,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_metrics(self) -> dict[str, Any]:
        """Get all tracked metrics."""
        return self._metrics.copy()

    def clear_metrics(self) -> None:
        """Clear all tracked metrics."""
        self._metrics.clear()
        logger.info("Cleared all metrics")


class PerformanceTracker:
    """Track performance metrics for memory operations."""

    def __init__(self):
        """Initialize performance tracker."""
        self._operations: list[dict[str, Any]] = []

    def record_operation(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record an operation's performance.

        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
            metadata: Additional metadata
        """
        self._operations.append(
            {
                "operation": operation,
                "duration_ms": duration_ms,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
            }
        )

    def get_statistics(self) -> dict[str, Any]:
        """
        Get performance statistics.

        Returns:
            Performance statistics
        """
        if not self._operations:
            return {"error": "No operations recorded"}

        # Group by operation type
        by_operation = defaultdict(list)
        for op in self._operations:
            by_operation[op["operation"]].append(op["duration_ms"])

        stats = {}
        for op_name, durations in by_operation.items():
            stats[op_name] = {
                "count": len(durations),
                "avg_ms": round(sum(durations) / len(durations), 2),
                "min_ms": round(min(durations), 2),
                "max_ms": round(max(durations), 2),
            }

        # Overall statistics
        all_durations = [op["duration_ms"] for op in self._operations]
        success_count = sum(1 for op in self._operations if op["success"])

        return {
            "overall": {
                "total_operations": len(self._operations),
                "success_rate": round(success_count / len(self._operations) * 100, 2),
                "avg_duration_ms": round(sum(all_durations) / len(all_durations), 2),
            },
            "by_operation": stats,
        }

    def clear(self) -> None:
        """Clear all recorded operations."""
        self._operations.clear()


def quick_analyze(messages: list[Message]) -> dict[str, Any]:
    """
    Quick utility to analyze messages.

    Args:
        messages: Messages to analyze

    Returns:
        Analytics results
    """
    analytics = MemoryAnalytics()
    return analytics.analyze_messages(messages)
