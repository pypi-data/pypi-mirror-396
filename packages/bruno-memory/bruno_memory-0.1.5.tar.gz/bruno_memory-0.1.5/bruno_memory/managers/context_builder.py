"""
Context Builder for bruno-memory.

Provides intelligent context building strategies for managing conversation
context windows with token limits and various retrieval strategies.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum

from bruno_core.models import Message, MessageRole

from ..exceptions import ValidationError


class ContextStrategy(str, Enum):
    """Context building strategies."""

    SLIDING_WINDOW = "sliding_window"
    RECENT_MESSAGES = "recent_messages"
    SEMANTIC = "semantic"
    IMPORTANCE = "importance"
    HYBRID = "hybrid"


class BaseContextStrategy(ABC):
    """Base class for context building strategies."""

    @abstractmethod
    async def select_messages(
        self,
        messages: list[Message],
        max_messages: int | None = None,
        max_tokens: int | None = None,
        **kwargs,
    ) -> list[Message]:
        """Select messages for context based on strategy.

        Args:
            messages: All available messages
            max_messages: Maximum number of messages
            max_tokens: Maximum token count (approximate)
            **kwargs: Strategy-specific parameters

        Returns:
            List[Message]: Selected messages for context
        """
        pass


class SlidingWindowStrategy(BaseContextStrategy):
    """Sliding window strategy - takes most recent N messages."""

    async def select_messages(
        self,
        messages: list[Message],
        max_messages: int | None = None,
        max_tokens: int | None = None,
        **kwargs,
    ) -> list[Message]:
        """Select most recent messages within limits."""
        if not messages:
            return []

        # Sort by timestamp (most recent last)
        sorted_messages = sorted(messages, key=lambda m: m.timestamp)

        if max_messages:
            sorted_messages = sorted_messages[-max_messages:]

        if max_tokens:
            # Rough token estimation: ~4 chars per token
            selected = []
            token_count = 0

            for msg in reversed(sorted_messages):
                msg_tokens = len(msg.content) // 4
                if token_count + msg_tokens <= max_tokens:
                    selected.insert(0, msg)
                    token_count += msg_tokens
                else:
                    break

            return selected

        return sorted_messages


class RecentMessagesStrategy(BaseContextStrategy):
    """Recent messages strategy - includes messages from recent time window."""

    async def select_messages(
        self,
        messages: list[Message],
        max_messages: int | None = None,
        max_tokens: int | None = None,
        time_window_minutes: int = 60,
        **kwargs,
    ) -> list[Message]:
        """Select messages from recent time window."""
        if not messages:
            return []

        # Filter by time window
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_messages = [m for m in messages if m.timestamp >= cutoff_time]

        # Sort by timestamp
        sorted_messages = sorted(recent_messages, key=lambda m: m.timestamp)

        if max_messages:
            sorted_messages = sorted_messages[-max_messages:]

        return sorted_messages


class ImportanceStrategy(BaseContextStrategy):
    """Importance-based strategy - selects most important messages."""

    async def select_messages(
        self,
        messages: list[Message],
        max_messages: int | None = None,
        max_tokens: int | None = None,
        **kwargs,
    ) -> list[Message]:
        """Select messages by importance score."""
        if not messages:
            return []

        # Calculate importance scores
        scored_messages = []
        for msg in messages:
            score = self._calculate_importance(msg)
            scored_messages.append((score, msg))

        # Sort by importance (highest first)
        scored_messages.sort(key=lambda x: x[0], reverse=True)

        # Take top N
        if max_messages:
            scored_messages = scored_messages[:max_messages]

        # Return in chronological order
        selected = [msg for _, msg in scored_messages]
        return sorted(selected, key=lambda m: m.timestamp)

    def _calculate_importance(self, message: Message) -> float:
        """Calculate importance score for a message.

        Factors:
        - Message length (longer = more important)
        - Role (system > user > assistant for context)
        - Recency (more recent = more important)
        - Keywords presence
        """
        score = 0.0

        # Base score from role
        role_scores = {MessageRole.SYSTEM: 10.0, MessageRole.USER: 5.0, MessageRole.ASSISTANT: 3.0}
        score += role_scores.get(message.role, 1.0)

        # Length score (normalized)
        score += min(len(message.content) / 100, 5.0)

        # Recency score (messages in last hour get boost)
        age = datetime.now() - message.timestamp
        if age.total_seconds() < 3600:
            score += 5.0
        elif age.total_seconds() < 86400:
            score += 2.0

        # Keywords boost
        important_keywords = ["error", "important", "critical", "help", "please"]
        content_lower = message.content.lower()
        for keyword in important_keywords:
            if keyword in content_lower:
                score += 2.0

        return score


class HybridStrategy(BaseContextStrategy):
    """Hybrid strategy combining multiple approaches."""

    async def select_messages(
        self,
        messages: list[Message],
        max_messages: int | None = None,
        max_tokens: int | None = None,
        **kwargs,
    ) -> list[Message]:
        """Combine recent messages with important ones."""
        if not messages:
            return []

        # Get recent messages (half quota)
        recent_limit = (max_messages // 2) if max_messages else 10
        recent_strategy = SlidingWindowStrategy()
        recent_messages = await recent_strategy.select_messages(messages, max_messages=recent_limit)

        # Get important messages (other half)
        importance_strategy = ImportanceStrategy()
        important_messages = await importance_strategy.select_messages(
            messages, max_messages=max_messages - len(recent_messages) if max_messages else 10
        )

        # Combine and deduplicate
        message_ids = {str(m.id) for m in recent_messages}
        for msg in important_messages:
            if str(msg.id) not in message_ids:
                recent_messages.append(msg)

        # Sort chronologically and apply limits
        result = sorted(recent_messages, key=lambda m: m.timestamp)

        if max_messages:
            result = result[-max_messages:]

        return result


class ContextBuilder:
    """
    Builds conversation context with intelligent message selection.

    Supports multiple strategies for context building including:
    - Sliding window (most recent N messages)
    - Time-based (messages from recent time window)
    - Importance-based (most important messages)
    - Hybrid (combination of strategies)
    """

    def __init__(
        self,
        strategy: ContextStrategy = ContextStrategy.SLIDING_WINDOW,
        max_messages: int = 50,
        max_tokens: int | None = None,
        include_system_messages: bool = True,
    ):
        """Initialize context builder.

        Args:
            strategy: Context building strategy to use
            max_messages: Maximum number of messages in context
            max_tokens: Optional maximum token count
            include_system_messages: Whether to include system messages
        """
        self.strategy = strategy
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.include_system_messages = include_system_messages

        # Initialize strategy handlers
        self._strategies: dict[ContextStrategy, BaseContextStrategy] = {
            ContextStrategy.SLIDING_WINDOW: SlidingWindowStrategy(),
            ContextStrategy.RECENT_MESSAGES: RecentMessagesStrategy(),
            ContextStrategy.IMPORTANCE: ImportanceStrategy(),
            ContextStrategy.HYBRID: HybridStrategy(),
        }

    async def build_context(
        self,
        messages: list[Message],
        max_messages: int | None = None,
        max_tokens: int | None = None,
        **strategy_params,
    ) -> list[Message]:
        """Build context from available messages.

        Args:
            messages: All available messages
            max_messages: Override default max messages
            max_tokens: Override default max tokens
            **strategy_params: Strategy-specific parameters

        Returns:
            List[Message]: Selected messages for context
        """
        if not messages:
            return []

        # Filter system messages if needed
        filtered_messages = messages
        if not self.include_system_messages:
            filtered_messages = [m for m in messages if m.role != MessageRole.SYSTEM]

        # Get strategy handler
        strategy_handler = self._strategies.get(self.strategy)
        if not strategy_handler:
            raise ValidationError(f"Unknown strategy: {self.strategy}")

        # Apply strategy
        selected = await strategy_handler.select_messages(
            filtered_messages,
            max_messages=max_messages or self.max_messages,
            max_tokens=max_tokens or self.max_tokens,
            **strategy_params,
        )

        return selected

    def estimate_token_count(self, messages: list[Message]) -> int:
        """Estimate token count for messages.

        Uses rough approximation of 4 characters per token.

        Args:
            messages: Messages to estimate

        Returns:
            int: Estimated token count
        """
        total_chars = sum(len(m.content) for m in messages)
        return total_chars // 4

    def truncate_to_token_limit(self, messages: list[Message], token_limit: int) -> list[Message]:
        """Truncate messages to fit within token limit.

        Keeps most recent messages that fit within limit.

        Args:
            messages: Messages to truncate
            token_limit: Maximum tokens allowed

        Returns:
            List[Message]: Truncated message list
        """
        if not messages:
            return []

        result = []
        token_count = 0

        # Start from most recent and work backwards
        for msg in reversed(sorted(messages, key=lambda m: m.timestamp)):
            msg_tokens = len(msg.content) // 4
            if token_count + msg_tokens <= token_limit:
                result.insert(0, msg)
                token_count += msg_tokens
            else:
                break

        return result

    def set_strategy(self, strategy: ContextStrategy) -> None:
        """Change the context building strategy.

        Args:
            strategy: New strategy to use
        """
        if strategy not in self._strategies:
            raise ValidationError(f"Unknown strategy: {strategy}")
        self.strategy = strategy

    def get_strategy(self) -> ContextStrategy:
        """Get current strategy.

        Returns:
            ContextStrategy: Current strategy
        """
        return self.strategy
