"""
Conversation Manager for bruno-memory.

Handles conversation lifecycle management, session tracking, turn-taking,
and conversation boundaries with support for branching conversations.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from bruno_core.models import Message, MessageRole, SessionContext

from ..base import BaseMemoryBackend
from ..exceptions import NotFoundError, StorageError, ValidationError


class ConversationManager:
    """
    Manages conversation lifecycle and session state.

    Provides high-level conversation management including:
    - Session creation and tracking
    - Turn-taking and message ordering
    - Conversation boundaries
    - Multi-party conversation support
    - Conversation branching
    """

    def __init__(self, backend: BaseMemoryBackend):
        """Initialize conversation manager with a backend.

        Args:
            backend: Memory backend for storage operations
        """
        self.backend = backend
        self._active_sessions: dict[str, SessionContext] = {}

    async def start_conversation(
        self,
        user_id: str,
        conversation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SessionContext:
        """Start a new conversation session.

        Args:
            user_id: User ID for the conversation
            conversation_id: Optional conversation ID (generated if not provided)
            metadata: Optional metadata for the session

        Returns:
            SessionContext: New session context

        Raises:
            ValidationError: If user_id is invalid
        """
        if not user_id:
            raise ValidationError("user_id is required")

        if not conversation_id:
            conversation_id = str(uuid4())

        try:
            session = await self.backend.create_session(user_id, conversation_id)
            self._active_sessions[session.session_id] = session
            return session
        except Exception as e:
            raise StorageError(f"Failed to start conversation: {e}")

    async def end_conversation(self, session_id: str) -> None:
        """End an active conversation session.

        Args:
            session_id: Session ID to end

        Raises:
            NotFoundError: If session not found
        """
        try:
            await self.backend.end_session(session_id)
            if session_id in self._active_sessions:
                del self._active_sessions[session_id]
        except Exception as e:
            raise StorageError(f"Failed to end conversation: {e}")

    async def get_session(self, session_id: str) -> SessionContext:
        """Get session context by ID.

        Args:
            session_id: Session ID to retrieve

        Returns:
            SessionContext: Session context

        Raises:
            NotFoundError: If session not found
        """
        # Check cache first
        if session_id in self._active_sessions:
            return self._active_sessions[session_id]

        try:
            session = await self.backend.get_session(session_id)
            if session.is_active:
                self._active_sessions[session_id] = session
            return session
        except Exception as e:
            raise NotFoundError(f"Session {session_id} not found: {e}")

    async def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        parent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        """Add a message to the conversation.

        Args:
            session_id: Session ID for the message
            role: Message role (user, assistant, system)
            content: Message content
            parent_id: Optional parent message ID for threading
            metadata: Optional message metadata

        Returns:
            Message: Created message

        Raises:
            NotFoundError: If session not found
            ValidationError: If message data is invalid
        """
        session = await self.get_session(session_id)

        message = Message(
            id=str(uuid4()),
            role=role,
            content=content,
            conversation_id=session.conversation_id,
            timestamp=datetime.now(timezone.utc),
            parent_id=parent_id,
            metadata=metadata or {},
        )

        try:
            await self.backend.store_message(message)
            return message
        except Exception as e:
            raise StorageError(f"Failed to add message: {e}")

    async def get_conversation_messages(
        self, conversation_id: str, limit: int | None = None, include_system: bool = True
    ) -> list[Message]:
        """Get messages for a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Optional limit on number of messages
            include_system: Whether to include system messages

        Returns:
            List[Message]: List of messages in chronological order
        """
        try:
            messages = await self.backend.retrieve_messages(
                conversation_id=conversation_id, limit=limit or 1000
            )

            if not include_system:
                messages = [m for m in messages if m.role != MessageRole.SYSTEM]

            return messages
        except Exception as e:
            raise StorageError(f"Failed to retrieve messages: {e}")

    async def get_turn_count(self, conversation_id: str) -> int:
        """Get the number of conversational turns.

        A turn is counted as a user message followed by an assistant response.

        Args:
            conversation_id: Conversation ID

        Returns:
            int: Number of turns
        """
        messages = await self.get_conversation_messages(conversation_id, include_system=False)

        # Count user-assistant pairs
        turn_count = 0
        last_role = None

        for message in messages:
            if last_role == MessageRole.USER and message.role == MessageRole.ASSISTANT:
                turn_count += 1
            last_role = message.role

        return turn_count

    async def branch_conversation(
        self, original_conversation_id: str, from_message_id: str, user_id: str
    ) -> SessionContext:
        """Create a new conversation branch from a specific message.

        Args:
            original_conversation_id: Original conversation ID
            from_message_id: Message ID to branch from
            user_id: User ID for the new branch

        Returns:
            SessionContext: New branched conversation session
        """
        # Get messages up to the branch point
        all_messages = await self.get_conversation_messages(original_conversation_id)

        # Find the branch point
        branch_index = None
        for i, msg in enumerate(all_messages):
            if str(msg.id) == from_message_id:
                branch_index = i
                break

        if branch_index is None:
            raise NotFoundError(f"Message {from_message_id} not found in conversation")

        # Create new conversation
        new_session = await self.start_conversation(
            user_id=user_id,
            metadata={"branched_from": original_conversation_id, "branch_point": from_message_id},
        )

        # Copy messages up to branch point
        for msg in all_messages[: branch_index + 1]:
            new_message = Message(
                id=str(uuid4()),
                role=msg.role,
                content=msg.content,
                conversation_id=new_session.conversation_id,
                timestamp=datetime.now(timezone.utc),
                metadata={**msg.metadata, "copied_from": str(msg.id)},
            )
            await self.backend.store_message(new_message)

        return new_session

    async def clear_conversation(
        self, conversation_id: str, keep_system_messages: bool = True
    ) -> None:
        """Clear conversation history.

        Args:
            conversation_id: Conversation ID to clear
            keep_system_messages: Whether to keep system messages
        """
        try:
            await self.backend.clear_history(conversation_id, keep_system_messages)
        except Exception as e:
            raise StorageError(f"Failed to clear conversation: {e}")

    async def get_active_sessions(self, user_id: str | None = None) -> list[SessionContext]:
        """Get all active sessions, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List[SessionContext]: List of active sessions
        """
        # For now, return cached active sessions
        # In a full implementation, this would query the backend
        sessions = list(self._active_sessions.values())

        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]

        return sessions

    async def update_session_metadata(self, session_id: str, metadata: dict[str, Any]) -> None:
        """Update session metadata.

        Args:
            session_id: Session ID
            metadata: New metadata to merge
        """
        session = await self.get_session(session_id)

        # Merge metadata
        updated_metadata = {**session.metadata, **metadata}

        # Update session (would need backend support)
        session.metadata.update(metadata)

        if session_id in self._active_sessions:
            self._active_sessions[session_id] = session
