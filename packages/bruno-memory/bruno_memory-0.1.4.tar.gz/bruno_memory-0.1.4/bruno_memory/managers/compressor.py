"""
Memory compression for bruno-memory.

Handles compression of conversation history to reduce context size
while preserving important information.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from bruno_core.models import MemoryEntry, MemoryType, Message, MessageRole, MessageType
from bruno_llm.base import BaseProvider

from ..base import BaseMemoryBackend
from ..exceptions import CompressionError


class CompressionStrategy:
    """Base class for compression strategies."""

    async def compress(
        self,
        messages: list[Message],
        target_size: int | None = None,
    ) -> tuple[list[Message], dict[str, Any]]:
        """Compress messages.

        Args:
            messages: Messages to compress
            target_size: Optional target message count

        Returns:
            Tuple[List[Message], Dict[str, Any]]: Compressed messages and metadata
        """
        raise NotImplementedError


class SummarizationStrategy(CompressionStrategy):
    """
    Compression strategy using LLM summarization.

    Summarizes older messages into a single context message.
    """

    def __init__(self, llm_provider: BaseProvider, summary_threshold: int = 20):
        """Initialize summarization strategy.

        Args:
            llm_provider: LLM provider from bruno-llm
            summary_threshold: Number of messages to trigger summarization
        """
        self.llm_provider = llm_provider
        self.summary_threshold = summary_threshold

    async def compress(
        self,
        messages: list[Message],
        target_size: int | None = None,
    ) -> tuple[list[Message], dict[str, Any]]:
        """Compress messages using summarization.

        Args:
            messages: Messages to compress
            target_size: Target message count (uses summary_threshold if None)

        Returns:
            Tuple[List[Message], Dict[str, Any]]: Compressed messages and metadata
        """
        if len(messages) <= (target_size or self.summary_threshold):
            return messages, {"compressed": False}

        # Split into old and recent messages
        split_point = len(messages) - (target_size or self.summary_threshold)
        old_messages = messages[:split_point]
        recent_messages = messages[split_point:]

        # Generate summary of old messages
        summary_text = await self._summarize_messages(old_messages)

        # Create summary message
        summary_message = Message(
            role=MessageRole.SYSTEM,
            content=f"[Summary of previous conversation]\n{summary_text}",
            message_type=MessageType.TEXT,
            timestamp=old_messages[-1].timestamp if old_messages else datetime.now(),
            metadata={
                "compressed": True,
                "original_count": len(old_messages),
                "compression_date": datetime.now().isoformat(),
            },
        )

        compressed_messages = [summary_message] + recent_messages

        metadata = {
            "compressed": True,
            "original_count": len(messages),
            "compressed_count": len(compressed_messages),
            "compression_ratio": len(compressed_messages) / len(messages),
        }

        return compressed_messages, metadata

    async def _summarize_messages(self, messages: list[Message]) -> str:
        """Summarize a list of messages.

        Args:
            messages: Messages to summarize

        Returns:
            str: Summary text
        """
        # Format messages for summarization
        conversation_text = self._format_messages(messages)

        # Create summarization prompt
        prompt = f"""Summarize the following conversation, preserving key information, decisions, and context:

{conversation_text}

Provide a concise summary that captures:
1. Main topics discussed
2. Important decisions or conclusions
3. Relevant context for continuing the conversation

Summary:"""

        try:
            # Generate summary using LLM
            summary = await self.llm_provider.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3,  # Lower temperature for more factual summary
            )

            return summary.strip()

        except Exception as e:
            raise CompressionError(f"Failed to generate summary: {e}") from e

    @staticmethod
    def _format_messages(messages: list[Message]) -> str:
        """Format messages for summarization.

        Args:
            messages: Messages to format

        Returns:
            str: Formatted conversation text
        """
        lines = []
        for msg in messages:
            role_name = (
                msg.role.value.upper()
                if isinstance(msg.role, MessageRole)
                else str(msg.role).upper()
            )
            lines.append(f"{role_name}: {msg.content}")

        return "\n".join(lines)


class ImportanceFilterStrategy(CompressionStrategy):
    """
    Compression strategy based on message importance.

    Keeps only high-importance messages based on metadata.
    """

    def __init__(self, importance_threshold: float = 0.5):
        """Initialize importance filter strategy.

        Args:
            importance_threshold: Minimum importance score to keep
        """
        self.importance_threshold = importance_threshold

    async def compress(
        self,
        messages: list[Message],
        target_size: int | None = None,
    ) -> tuple[list[Message], dict[str, Any]]:
        """Compress messages by filtering based on importance.

        Args:
            messages: Messages to compress
            target_size: Target message count

        Returns:
            Tuple[List[Message], Dict[str, Any]]: Compressed messages and metadata
        """
        # Filter by importance
        important_messages = [
            msg
            for msg in messages
            if msg.metadata and msg.metadata.get("importance", 0) >= self.importance_threshold
        ]

        # If target_size specified, keep top N most important
        if target_size and len(important_messages) > target_size:
            important_messages.sort(key=lambda m: m.metadata.get("importance", 0), reverse=True)
            important_messages = important_messages[:target_size]

            # Re-sort by timestamp
            important_messages.sort(key=lambda m: m.timestamp or datetime.min)

        metadata = {
            "compressed": True,
            "original_count": len(messages),
            "compressed_count": len(important_messages),
            "compression_ratio": len(important_messages) / len(messages) if messages else 0,
            "strategy": "importance_filter",
        }

        return important_messages, metadata


class TimeWindowStrategy(CompressionStrategy):
    """
    Compression strategy based on time windows.

    Keeps only recent messages within a time window.
    """

    def __init__(self, window_hours: int = 24):
        """Initialize time window strategy.

        Args:
            window_hours: Time window in hours
        """
        self.window_hours = window_hours

    async def compress(
        self,
        messages: list[Message],
        target_size: int | None = None,
    ) -> tuple[list[Message], dict[str, Any]]:
        """Compress messages by keeping only recent ones.

        Args:
            messages: Messages to compress
            target_size: Optional target message count (overrides time window)

        Returns:
            Tuple[List[Message], Dict[str, Any]]: Compressed messages and metadata
        """
        if target_size:
            # Use simple recent message selection
            recent_messages = messages[-target_size:]
        else:
            # Filter by time window
            cutoff_time = datetime.now() - timedelta(hours=self.window_hours)
            recent_messages = [
                msg for msg in messages if msg.timestamp and msg.timestamp >= cutoff_time
            ]

        metadata = {
            "compressed": True,
            "original_count": len(messages),
            "compressed_count": len(recent_messages),
            "compression_ratio": len(recent_messages) / len(messages) if messages else 0,
            "strategy": "time_window",
            "window_hours": self.window_hours,
        }

        return recent_messages, metadata


class MemoryCompressor:
    """
    Main compression manager for conversation history.

    Manages multiple compression strategies and automatic compression triggers.
    """

    def __init__(
        self,
        backend: BaseMemoryBackend,
        strategy: CompressionStrategy | None = None,
        auto_compress_threshold: int = 50,
        target_size: int = 20,
    ):
        """Initialize memory compressor.

        Args:
            backend: Backend for storage
            strategy: Compression strategy (uses TimeWindowStrategy if None)
            auto_compress_threshold: Message count to trigger auto-compression
            target_size: Target message count after compression
        """
        self.backend = backend
        self.strategy = strategy or TimeWindowStrategy()
        self.auto_compress_threshold = auto_compress_threshold
        self.target_size = target_size
        self._compression_stats: dict[UUID, dict[str, Any]] = {}

    async def compress_conversation(
        self,
        conversation_id: UUID,
        target_size: int | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """Compress conversation history.

        Args:
            conversation_id: Conversation ID
            target_size: Target message count (uses default if None)
            force: Force compression even if below threshold

        Returns:
            Dict[str, Any]: Compression result metadata
        """
        try:
            # Retrieve current messages
            messages = await self.backend.retrieve_messages(conversation_id)

            if not force and len(messages) < self.auto_compress_threshold:
                return {
                    "compressed": False,
                    "reason": "below_threshold",
                    "message_count": len(messages),
                }

            # Compress messages
            compressed_messages, compression_metadata = await self.strategy.compress(
                messages,
                target_size or self.target_size,
            )

            # Store compressed messages (replace old ones)
            if compression_metadata.get("compressed", False):
                # Clear old history
                await self.backend.clear_history(conversation_id)

                # Store compressed messages
                for msg in compressed_messages:
                    await self.backend.store_message(msg, conversation_id)

                # Update stats
                self._compression_stats[conversation_id] = {
                    **compression_metadata,
                    "timestamp": datetime.now().isoformat(),
                }

            return compression_metadata

        except Exception as e:
            raise CompressionError(f"Failed to compress conversation: {e}") from e

    async def auto_compress(self, conversation_id: UUID) -> bool:
        """Automatically compress conversation if threshold reached.

        Args:
            conversation_id: Conversation ID

        Returns:
            bool: True if compression occurred
        """
        messages = await self.backend.retrieve_messages(conversation_id)

        if len(messages) >= self.auto_compress_threshold:
            result = await self.compress_conversation(conversation_id)
            return result.get("compressed", False)

        return False

    async def get_compression_stats(self, conversation_id: UUID) -> dict[str, Any] | None:
        """Get compression statistics for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            Optional[Dict[str, Any]]: Compression stats if available
        """
        return self._compression_stats.get(conversation_id)

    async def compress_to_memory(
        self,
        conversation_id: UUID,
        user_id: str,
        importance_threshold: float = 0.7,
    ) -> int:
        """Compress conversation into memory entries.

        Extracts important information from conversation and stores as memories.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            importance_threshold: Minimum importance for memory creation

        Returns:
            int: Number of memories created
        """
        try:
            messages = await self.backend.retrieve_messages(conversation_id)

            # Extract important messages
            important_messages = [
                msg
                for msg in messages
                if msg.metadata and msg.metadata.get("importance", 0) >= importance_threshold
            ]

            # Create memories from important messages
            memory_count = 0
            for msg in important_messages:
                # Create memory entry
                memory = MemoryEntry(
                    content=msg.content,
                    memory_type=MemoryType.EPISODIC,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    metadata={
                        "importance": msg.metadata.get("importance", 0.5),
                        "source": "compression",
                        "original_timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    },
                )

                await self.backend.store_memory(memory)
                memory_count += 1

            return memory_count

        except Exception as e:
            raise CompressionError(f"Failed to compress to memory: {e}") from e


class AdaptiveCompressor(MemoryCompressor):
    """
    Adaptive compressor that selects strategy based on conversation characteristics.
    """

    def __init__(
        self, backend: BaseMemoryBackend, llm_provider: BaseProvider | None = None, **kwargs
    ):
        """Initialize adaptive compressor.

        Args:
            backend: Backend for storage
            llm_provider: Optional LLM provider for summarization
            **kwargs: Additional arguments for parent class
        """
        super().__init__(backend, **kwargs)
        self.llm_provider = llm_provider

        # Available strategies
        self.strategies = {
            "time_window": TimeWindowStrategy(),
            "importance": ImportanceFilterStrategy(),
        }

        if llm_provider:
            self.strategies["summarization"] = SummarizationStrategy(llm_provider)

    async def compress_conversation(
        self,
        conversation_id: UUID,
        target_size: int | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """Compress using adaptive strategy selection.

        Args:
            conversation_id: Conversation ID
            target_size: Target message count
            force: Force compression

        Returns:
            Dict[str, Any]: Compression result
        """
        # Retrieve messages
        messages = await self.backend.retrieve_messages(conversation_id)

        if not force and len(messages) < self.auto_compress_threshold:
            return {"compressed": False, "reason": "below_threshold"}

        # Select strategy based on characteristics
        strategy_name = self._select_strategy(messages)
        selected_strategy = self.strategies[strategy_name]

        # Use selected strategy
        self.strategy = selected_strategy

        result = await super().compress_conversation(
            conversation_id,
            target_size,
            force=True,
        )

        result["strategy_used"] = strategy_name
        return result

    def _select_strategy(self, messages: list[Message]) -> str:
        """Select appropriate compression strategy.

        Args:
            messages: Messages to analyze

        Returns:
            str: Strategy name
        """
        # Count messages with importance metadata
        with_importance = sum(
            1 for msg in messages if msg.metadata and "importance" in msg.metadata
        )

        # If most messages have importance scores, use importance filter
        if with_importance / len(messages) > 0.5:
            return "importance"

        # If LLM available and conversation is long, use summarization
        if "summarization" in self.strategies and len(messages) > 30:
            return "summarization"

        # Default to time window
        return "time_window"
