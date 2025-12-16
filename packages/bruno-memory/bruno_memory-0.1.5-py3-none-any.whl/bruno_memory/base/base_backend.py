"""
Abstract base backend for bruno-memory implementations.

Provides common utilities and implements the bruno-core MemoryInterface
with proper model handling and serialization.
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from bruno_core.interfaces import MemoryInterface
from bruno_core.models import (
    ConversationContext,
    MemoryEntry,
    MemoryQuery,
    MemoryType,
    Message,
    MessageRole,
    MessageType,
    SessionContext,
)
from bruno_core.models.context import UserContext
from bruno_core.models.memory import MemoryMetadata

from ..exceptions import SerializationError, ValidationError
from .config import MemoryConfig


class BaseMemoryBackend(MemoryInterface, ABC):
    """Abstract base class for all memory backend implementations."""

    def __init__(self, config: MemoryConfig):
        """Initialize base backend with configuration.

        Args:
            config: Backend configuration instance
        """
        self.config = config
        self._connected = False

    # Abstract connection methods that must be implemented
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the backend storage."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the backend storage."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the backend is healthy and responsive."""
        pass

    # Model validation utilities
    def validate_message(self, message: Message) -> None:
        """Validate a Message model instance.

        Args:
            message: Message to validate

        Raises:
            ValidationError: If message is invalid
        """
        if not isinstance(message, Message):
            raise ValidationError(f"Expected Message instance, got {type(message)}")

        if not message.content or len(message.content.strip()) == 0:
            raise ValidationError("Message content cannot be empty")

        if not isinstance(message.role, MessageRole):
            raise ValidationError(f"Invalid message role: {message.role}")

    def validate_memory_entry(self, memory_entry: MemoryEntry) -> None:
        """Validate a MemoryEntry model instance.

        Args:
            memory_entry: MemoryEntry to validate

        Raises:
            ValidationError: If memory entry is invalid
        """
        if not isinstance(memory_entry, MemoryEntry):
            raise ValidationError(f"Expected MemoryEntry instance, got {type(memory_entry)}")

        if not memory_entry.content or len(memory_entry.content.strip()) == 0:
            raise ValidationError("Memory content cannot be empty")

        if not isinstance(memory_entry.memory_type, MemoryType):
            raise ValidationError(f"Invalid memory type: {memory_entry.memory_type}")

        if not memory_entry.user_id or len(memory_entry.user_id.strip()) == 0:
            raise ValidationError("Memory entry user_id cannot be empty")

    # Model serialization utilities for database storage
    def serialize_message(self, message: Message) -> dict[str, Any]:
        """Serialize Message to database-compatible dictionary.

        Args:
            message: Message instance to serialize

        Returns:
            Dictionary with string keys and JSON-serializable values
        """
        try:
            return {
                "id": str(message.id),
                "role": message.role.value,
                "content": message.content,
                "message_type": message.message_type.value,
                "timestamp": message.timestamp.isoformat(),
                "metadata": json.dumps(message.metadata) if message.metadata else None,
                "parent_id": str(message.parent_id) if message.parent_id else None,
                "conversation_id": message.conversation_id,
            }
        except Exception as e:
            raise SerializationError(f"Failed to serialize message: {e}")

    def deserialize_message(self, data: dict[str, Any]) -> Message:
        """Deserialize database data to Message instance.

        Args:
            data: Dictionary from database

        Returns:
            Message instance
        """
        try:
            return Message(
                id=UUID(data["id"]),
                role=MessageRole(data["role"]),
                content=data["content"],
                message_type=MessageType(data["message_type"]),
                timestamp=datetime.fromisoformat(data["timestamp"]),
                metadata=json.loads(data["metadata"]) if data["metadata"] else {},
                parent_id=UUID(data["parent_id"]) if data["parent_id"] else None,
                conversation_id=data["conversation_id"],
            )
        except Exception as e:
            raise SerializationError(f"Failed to deserialize message: {e}")

    def serialize_memory_entry(self, memory_entry: MemoryEntry) -> dict[str, Any]:
        """Serialize MemoryEntry to database-compatible dictionary.

        Args:
            memory_entry: MemoryEntry instance to serialize

        Returns:
            Dictionary with string keys and JSON-serializable values
        """
        try:
            return {
                "id": str(memory_entry.id),
                "content": memory_entry.content,
                "memory_type": memory_entry.memory_type.value,
                "user_id": memory_entry.user_id,
                "conversation_id": memory_entry.conversation_id,
                "metadata": json.dumps(memory_entry.metadata.model_dump()),
                "created_at": memory_entry.created_at.isoformat(),
                "updated_at": memory_entry.updated_at.isoformat(),
                "last_accessed": memory_entry.last_accessed.isoformat(),
                "expires_at": (
                    memory_entry.expires_at.isoformat() if memory_entry.expires_at else None
                ),
            }
        except Exception as e:
            raise SerializationError(f"Failed to serialize memory entry: {e}")

    def deserialize_memory_entry(self, data: dict[str, Any]) -> MemoryEntry:
        """Deserialize database data to MemoryEntry instance.

        Args:
            data: Dictionary from database

        Returns:
            MemoryEntry instance
        """
        try:
            metadata_dict = json.loads(data["metadata"]) if data["metadata"] else {}
            metadata = MemoryMetadata.model_validate(metadata_dict)

            return MemoryEntry(
                id=UUID(data["id"]),
                content=data["content"],
                memory_type=MemoryType(data["memory_type"]),
                user_id=data["user_id"],
                conversation_id=data["conversation_id"],
                metadata=metadata,
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                last_accessed=datetime.fromisoformat(data["last_accessed"]),
                expires_at=(
                    datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None
                ),
            )
        except Exception as e:
            raise SerializationError(f"Failed to deserialize memory entry: {e}")

    def serialize_session_context(self, session: SessionContext) -> dict[str, Any]:
        """Serialize SessionContext to database-compatible dictionary.

        Args:
            session: SessionContext instance to serialize

        Returns:
            Dictionary with string keys and JSON-serializable values
        """
        try:
            return {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "conversation_id": session.conversation_id,
                "started_at": session.started_at.isoformat(),
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "last_activity": session.last_activity.isoformat(),
                "is_active": session.is_active,
                "state": json.dumps(session.state),
                "metadata": json.dumps(session.metadata),
            }
        except Exception as e:
            raise SerializationError(f"Failed to serialize session context: {e}")

    def deserialize_session_context(self, data: dict[str, Any]) -> SessionContext:
        """Deserialize database data to SessionContext instance.

        Args:
            data: Dictionary from database

        Returns:
            SessionContext instance
        """
        try:
            return SessionContext(
                session_id=data["session_id"],
                user_id=data["user_id"],
                conversation_id=data["conversation_id"],
                started_at=datetime.fromisoformat(data["started_at"]),
                ended_at=datetime.fromisoformat(data["ended_at"]) if data["ended_at"] else None,
                last_activity=datetime.fromisoformat(data["last_activity"]),
                is_active=bool(data["is_active"]),
                state=json.loads(data["state"]) if data["state"] else {},
                metadata=json.loads(data["metadata"]) if data["metadata"] else {},
            )
        except Exception as e:
            raise SerializationError(f"Failed to deserialize session context: {e}")

    def serialize_user_context(self, user: UserContext) -> dict[str, Any]:
        """Serialize UserContext to database-compatible dictionary.

        Args:
            user: UserContext instance to serialize

        Returns:
            Dictionary with string keys and JSON-serializable values
        """
        try:
            return {
                "user_id": user.user_id,
                "name": user.name,
                "preferences": json.dumps(user.preferences),
                "profile": json.dumps(user.profile),
                "metadata": json.dumps(user.metadata),
                "created_at": user.created_at.isoformat(),
                "last_active": user.last_active.isoformat(),
            }
        except Exception as e:
            raise SerializationError(f"Failed to serialize user context: {e}")

    def deserialize_user_context(self, data: dict[str, Any]) -> UserContext:
        """Deserialize database data to UserContext instance.

        Args:
            data: Dictionary from database

        Returns:
            UserContext instance
        """
        try:
            return UserContext(
                user_id=data["user_id"],
                name=data["name"],
                preferences=json.loads(data["preferences"]) if data["preferences"] else {},
                profile=json.loads(data["profile"]) if data["profile"] else {},
                metadata=json.loads(data["metadata"]) if data["metadata"] else {},
                created_at=datetime.fromisoformat(data["created_at"]),
                last_active=datetime.fromisoformat(data["last_active"]),
            )
        except Exception as e:
            raise SerializationError(f"Failed to deserialize user context: {e}")

    # Utility methods for common operations
    def build_memory_query_filters(self, query: MemoryQuery) -> dict[str, Any]:
        """Build filter dictionary from MemoryQuery for backend-specific use.

        Args:
            query: MemoryQuery instance

        Returns:
            Dictionary of filters for backend implementation
        """
        filters = {
            "user_id": query.user_id,
            "query_text": query.query_text,
            "memory_types": [mt.value for mt in query.memory_types] if query.memory_types else [],
            "categories": query.categories,
            "tags": query.tags,
            "min_confidence": query.min_confidence,
            "min_importance": query.min_importance,
            "limit": query.limit,
            "include_expired": query.include_expired,
            "similarity_threshold": query.similarity_threshold,
        }
        return {k: v for k, v in filters.items() if v is not None and v != []}

    def create_conversation_context(
        self,
        user_id: str,
        session_id: str | None = None,
        messages: list[Message] | None = None,
        conversation_id: str | None = None,
    ) -> ConversationContext:
        """Helper to create ConversationContext with proper linking.

        Args:
            user_id: User ID
            session_id: Optional session ID
            messages: Optional list of messages
            conversation_id: Optional conversation ID

        Returns:
            ConversationContext instance
        """
        # Create UserContext
        user_context = UserContext(user_id=user_id)

        # Create SessionContext
        session_context = SessionContext(user_id=user_id, conversation_id=conversation_id)
        if session_id:
            session_context.session_id = session_id

        # Create ConversationContext
        return ConversationContext(
            conversation_id=conversation_id or session_context.conversation_id,
            user=user_context,
            session=session_context,
            messages=messages or [],
            metadata={},
        )

    # Connection state properties
    @property
    def is_connected(self) -> bool:
        """Check if backend is connected."""
        return self._connected
