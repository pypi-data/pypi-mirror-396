"""
PostgreSQL backend implementation for bruno-memory.

Production-ready backend with connection pooling, JSON operations,
and optimized queries for scalability.
"""

import asyncio
import json
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import asyncpg
from bruno_core.models import (
    ConversationContext,
    MemoryEntry,
    MemoryMetadata,
    MemoryQuery,
    MemoryType,
    Message,
    MessageRole,
    SessionContext,
)

from bruno_memory.base.base_backend import BaseMemoryBackend
from bruno_memory.base.config import PostgreSQLConfig
from bruno_memory.exceptions import (
    ConnectionError,
    StorageError,
)

from .schema import get_full_schema_sql


class PostgreSQLMemoryBackend(BaseMemoryBackend):
    """
    PostgreSQL backend for bruno-memory.

    Features:
    - Connection pooling for high concurrency
    - JSON/JSONB support for flexible metadata
    - Full-text search on content
    - Transaction support
    - Prepared for pgvector semantic search
    """

    def __init__(self, config: PostgreSQLConfig):
        """Initialize PostgreSQL backend.

        Args:
            config: PostgreSQL configuration
        """
        super().__init__(config)
        self.config: PostgreSQLConfig = config
        self._pool: asyncpg.Pool | None = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize connection pool and create schema."""
        if self._initialized:
            return

        try:
            # Create connection pool
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                min_size=self.config.pool_min_size,
                max_size=self.config.pool_max_size,
                command_timeout=self.config.command_timeout,
                server_settings=self.config.server_settings or {},
            )

            # Create schema
            async with self._pool.acquire() as conn:
                await conn.execute(get_full_schema_sql())

            self._initialized = True

        except Exception as e:
            raise ConnectionError(f"Failed to initialize PostgreSQL backend: {e}") from e

    async def connect(self) -> None:
        """Connect to PostgreSQL (alias for initialize)."""
        await self.initialize()

    async def disconnect(self) -> None:
        """Disconnect from PostgreSQL (alias for close)."""
        await self.close()

    async def health_check(self) -> bool:
        """Check if PostgreSQL backend is healthy.

        Returns:
            bool: True if healthy, False otherwise
        """
        if not self._initialized or not self._pool:
            return False

        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception:
            return False

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
        self._initialized = False

    async def store_message(
        self,
        message: Message,
        conversation_id: UUID,
        parent_id: UUID | None = None,
    ) -> UUID:
        """Store a message in the database.

        Args:
            message: Message to store
            conversation_id: ID of the conversation
            parent_id: Optional parent message ID

        Returns:
            UUID: ID of the stored message

        Raises:
            StorageError: If storage fails
        """
        await self._ensure_initialized()
        self.validate_message(message)

        try:
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    # Store message
                    message_id = uuid4()
                    metadata_json = json.dumps(message.metadata or {})

                    await conn.execute(
                        """
                        INSERT INTO messages 
                        (id, role, content, message_type, timestamp, metadata, parent_id, conversation_id)
                        VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8)
                        """,
                        message_id,
                        (
                            message.role.value
                            if isinstance(message.role, MessageRole)
                            else message.role
                        ),
                        message.content,
                        message.message_type or "text",
                        message.timestamp or datetime.now(),
                        metadata_json,
                        parent_id,
                        conversation_id,
                    )

                    # Update conversation context
                    await conn.execute(
                        """
                        UPDATE conversation_contexts 
                        SET message_count = message_count + 1, updated_at = NOW()
                        WHERE conversation_id = $1
                        """,
                        conversation_id,
                    )

                    return message_id

        except Exception as e:
            raise StorageError(f"Failed to store message: {e}") from e

    async def retrieve_messages(
        self,
        conversation_id: UUID,
        limit: int | None = None,
        before: datetime | None = None,
        after: datetime | None = None,
    ) -> list[Message]:
        """Retrieve messages from a conversation.

        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to retrieve
            before: Only return messages before this timestamp
            after: Only return messages after this timestamp

        Returns:
            List[Message]: Retrieved messages

        Raises:
            StorageError: If retrieval fails
        """
        await self._ensure_initialized()

        try:
            query = """
                SELECT id, role, content, message_type, timestamp, metadata, parent_id
                FROM messages
                WHERE conversation_id = $1
            """
            params = [conversation_id]
            param_idx = 2

            if after:
                query += f" AND timestamp > ${param_idx}"
                params.append(after)
                param_idx += 1

            if before:
                query += f" AND timestamp < ${param_idx}"
                params.append(before)
                param_idx += 1

            query += " ORDER BY timestamp ASC"

            if limit:
                query += f" LIMIT ${param_idx}"
                params.append(limit)

            async with self._pool.acquire() as conn:
                rows = await conn.fetch(query, *params)

            messages = []
            for row in rows:
                metadata = dict(row["metadata"]) if row["metadata"] else {}
                message = Message(
                    role=MessageRole(row["role"]),
                    content=row["content"],
                    message_type=row["message_type"],
                    timestamp=row["timestamp"],
                    metadata=metadata,
                )
                messages.append(message)

            return messages

        except Exception as e:
            raise StorageError(f"Failed to retrieve messages: {e}") from e

    async def search_messages(
        self,
        query: str,
        conversation_id: UUID | None = None,
        limit: int = 10,
    ) -> list[Message]:
        """Search messages using full-text search.

        Args:
            query: Search query
            conversation_id: Optional conversation to search within
            limit: Maximum number of results

        Returns:
            List[Message]: Matching messages

        Raises:
            StorageError: If search fails
        """
        await self._ensure_initialized()

        try:
            sql = """
                SELECT id, role, content, message_type, timestamp, metadata, parent_id,
                       ts_rank(to_tsvector('english', content), plainto_tsquery('english', $1)) as rank
                FROM messages
                WHERE to_tsvector('english', content) @@ plainto_tsquery('english', $1)
            """
            params = [query]
            param_idx = 2

            if conversation_id:
                sql += f" AND conversation_id = ${param_idx}"
                params.append(conversation_id)
                param_idx += 1

            sql += f" ORDER BY rank DESC LIMIT ${param_idx}"
            params.append(limit)

            async with self._pool.acquire() as conn:
                rows = await conn.fetch(sql, *params)

            messages = []
            for row in rows:
                metadata = dict(row["metadata"]) if row["metadata"] else {}
                message = Message(
                    role=MessageRole(row["role"]),
                    content=row["content"],
                    message_type=row["message_type"],
                    timestamp=row["timestamp"],
                    metadata=metadata,
                )
                messages.append(message)

            return messages

        except Exception as e:
            raise StorageError(f"Failed to search messages: {e}") from e

    async def store_memory(self, memory: MemoryEntry) -> UUID:
        """Store a memory entry.

        Args:
            memory: Memory entry to store

        Returns:
            UUID: ID of the stored memory

        Raises:
            StorageError: If storage fails
        """
        await self._ensure_initialized()
        self.validate_memory_entry(memory)

        try:
            async with self._pool.acquire() as conn:
                memory_id = uuid4()

                # Extract metadata fields
                metadata = memory.metadata.model_dump() if memory.metadata else {}
                importance = metadata.get("importance", 0.0)
                confidence = metadata.get("confidence", 0.0)

                metadata_json = json.dumps(metadata)

                await conn.execute(
                    """
                    INSERT INTO memory_entries
                    (id, content, memory_type, user_id, conversation_id, metadata,
                     importance, confidence, expires_at)
                    VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8, $9)
                    """,
                    memory_id,
                    memory.content,
                    (
                        memory.memory_type.value
                        if isinstance(memory.memory_type, MemoryType)
                        else memory.memory_type
                    ),
                    memory.user_id,
                    memory.conversation_id,
                    metadata_json,
                    importance,
                    confidence,
                    metadata.get("expires_at"),
                )

                return memory_id

        except Exception as e:
            raise StorageError(f"Failed to store memory: {e}") from e

    async def retrieve_memories(
        self,
        user_id: str,
        memory_type: MemoryType | None = None,
        limit: int | None = None,
    ) -> list[MemoryEntry]:
        """Retrieve memory entries for a user.

        Args:
            user_id: User ID
            memory_type: Optional memory type filter
            limit: Maximum number of memories to retrieve

        Returns:
            List[MemoryEntry]: Retrieved memories

        Raises:
            StorageError: If retrieval fails
        """
        await self._ensure_initialized()

        try:
            query = """
                SELECT id, content, memory_type, user_id, conversation_id, 
                       metadata, created_at, updated_at, last_accessed,
                       importance, confidence, expires_at
                FROM memory_entries
                WHERE user_id = $1
                  AND (expires_at IS NULL OR expires_at > NOW())
            """
            params = [user_id]
            param_idx = 2

            if memory_type:
                query += f" AND memory_type = ${param_idx}"
                params.append(
                    memory_type.value if isinstance(memory_type, MemoryType) else memory_type
                )
                param_idx += 1

            query += " ORDER BY importance DESC, updated_at DESC"

            if limit:
                query += f" LIMIT ${param_idx}"
                params.append(limit)

            async with self._pool.acquire() as conn:
                # Update last_accessed for retrieved memories
                async with conn.transaction():
                    rows = await conn.fetch(query, *params)

                    if rows:
                        memory_ids = [row["id"] for row in rows]
                        await conn.execute(
                            """
                            UPDATE memory_entries
                            SET last_accessed = NOW()
                            WHERE id = ANY($1::uuid[])
                            """,
                            memory_ids,
                        )

            memories = []
            for row in rows:
                metadata_dict = dict(row["metadata"]) if row["metadata"] else {}
                metadata_dict["importance"] = row["importance"]
                metadata_dict["confidence"] = row["confidence"]
                metadata_dict["created_at"] = row["created_at"]
                metadata_dict["updated_at"] = row["updated_at"]
                metadata_dict["last_accessed"] = row["last_accessed"]
                if row["expires_at"]:
                    metadata_dict["expires_at"] = row["expires_at"]

                memory = MemoryEntry(
                    content=row["content"],
                    memory_type=MemoryType(row["memory_type"]),
                    user_id=row["user_id"],
                    conversation_id=row["conversation_id"],
                    metadata=MemoryMetadata(**metadata_dict),
                )
                memories.append(memory)

            return memories

        except Exception as e:
            raise StorageError(f"Failed to retrieve memories: {e}") from e

    async def search_memories(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Search memories with full-text search.

        Args:
            query: Memory query with filters

        Returns:
            List[MemoryEntry]: Matching memories

        Raises:
            StorageError: If search fails
        """
        await self._ensure_initialized()

        try:
            sql = """
                SELECT id, content, memory_type, user_id, conversation_id,
                       metadata, created_at, updated_at, last_accessed,
                       importance, confidence, expires_at,
                       ts_rank(to_tsvector('english', content), plainto_tsquery('english', $1)) as rank
                FROM memory_entries
                WHERE user_id = $2
                  AND (expires_at IS NULL OR expires_at > NOW())
                  AND to_tsvector('english', content) @@ plainto_tsquery('english', $1)
            """
            params = [query.query_text, query.user_id]
            param_idx = 3

            if query.memory_types:
                type_values = [
                    t.value if isinstance(t, MemoryType) else t for t in query.memory_types
                ]
                sql += f" AND memory_type = ANY(${param_idx}::varchar[])"
                params.append(type_values)
                param_idx += 1

            if query.conversation_id:
                sql += f" AND conversation_id = ${param_idx}"
                params.append(query.conversation_id)
                param_idx += 1

            if query.min_importance is not None:
                sql += f" AND importance >= ${param_idx}"
                params.append(query.min_importance)
                param_idx += 1

            if query.time_range:
                start, end = query.time_range
                if start:
                    sql += f" AND created_at >= ${param_idx}"
                    params.append(start)
                    param_idx += 1
                if end:
                    sql += f" AND created_at <= ${param_idx}"
                    params.append(end)
                    param_idx += 1

            sql += f" ORDER BY rank DESC, importance DESC LIMIT ${param_idx}"
            params.append(query.limit or 10)

            async with self._pool.acquire() as conn:
                rows = await conn.fetch(sql, *params)

            memories = []
            for row in rows:
                metadata_dict = dict(row["metadata"]) if row["metadata"] else {}
                metadata_dict["importance"] = row["importance"]
                metadata_dict["confidence"] = row["confidence"]
                metadata_dict["created_at"] = row["created_at"]
                metadata_dict["updated_at"] = row["updated_at"]
                metadata_dict["last_accessed"] = row["last_accessed"]
                if row["expires_at"]:
                    metadata_dict["expires_at"] = row["expires_at"]

                memory = MemoryEntry(
                    content=row["content"],
                    memory_type=MemoryType(row["memory_type"]),
                    user_id=row["user_id"],
                    conversation_id=row["conversation_id"],
                    metadata=MemoryMetadata(**metadata_dict),
                )
                memories.append(memory)

            return memories

        except Exception as e:
            raise StorageError(f"Failed to search memories: {e}") from e

    async def delete_memory(self, memory_id: UUID) -> None:
        """Delete a memory entry.

        Args:
            memory_id: UUID of the memory entry to delete

        Raises:
            StorageError: If deletion fails
        """
        await self._ensure_initialized()

        try:
            async with self._pool.acquire() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM memory_entries
                    WHERE id = $1
                    """,
                    memory_id,
                )

                # Check if any rows were deleted
                deleted_count = int(result.split()[-1])
                if deleted_count == 0:
                    from bruno_memory.exceptions import NotFoundError

                    raise NotFoundError(f"Memory entry {memory_id} not found")

        except Exception as e:
            raise StorageError(f"Failed to delete memory: {e}") from e

    async def create_session(
        self,
        user_id: str,
        conversation_id: UUID,
        initial_state: dict[str, Any] | None = None,
    ) -> SessionContext:
        """Create a new session.

        Args:
            user_id: User ID
            conversation_id: Conversation ID
            initial_state: Optional initial session state

        Returns:
            SessionContext: Created session

        Raises:
            StorageError: If creation fails
        """
        await self._ensure_initialized()

        try:
            async with self._pool.acquire() as conn:
                session_id = uuid4()
                now = datetime.now()
                state_json = json.dumps(initial_state or {})

                await conn.execute(
                    """
                    INSERT INTO session_contexts
                    (session_id, user_id, conversation_id, state)
                    VALUES ($1, $2, $3, $4::jsonb)
                    """,
                    session_id,
                    user_id,
                    conversation_id,
                    state_json,
                )

                return SessionContext(
                    session_id=session_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    started_at=now,
                    last_activity=now,
                    is_active=True,
                    state=initial_state or {},
                )

        except Exception as e:
            raise StorageError(f"Failed to create session: {e}") from e

    async def get_session(self, session_id: UUID) -> SessionContext | None:
        """Retrieve a session by ID.

        Args:
            session_id: Session ID

        Returns:
            Optional[SessionContext]: Session if found

        Raises:
            StorageError: If retrieval fails
        """
        await self._ensure_initialized()

        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT session_id, user_id, conversation_id, started_at, ended_at,
                           last_activity, is_active, state, metadata
                    FROM session_contexts
                    WHERE session_id = $1
                    """,
                    session_id,
                )

            if not row:
                return None

            return SessionContext(
                session_id=row["session_id"],
                user_id=row["user_id"],
                conversation_id=row["conversation_id"],
                started_at=row["started_at"],
                ended_at=row["ended_at"],
                last_activity=row["last_activity"],
                is_active=row["is_active"],
                state=dict(row["state"]) if row["state"] else {},
                metadata=dict(row["metadata"]) if row["metadata"] else {},
            )

        except Exception as e:
            raise StorageError(f"Failed to get session: {e}") from e

    async def update_session_state(
        self,
        session_id: UUID,
        state: dict[str, Any],
    ) -> None:
        """Update session state.

        Args:
            session_id: Session ID
            state: New session state

        Raises:
            StorageError: If update fails
        """
        await self._ensure_initialized()

        try:
            async with self._pool.acquire() as conn:
                state_json = json.dumps(state)
                await conn.execute(
                    """
                    UPDATE session_contexts
                    SET state = $2::jsonb
                    WHERE session_id = $1
                    """,
                    session_id,
                    state_json,
                )

        except Exception as e:
            raise StorageError(f"Failed to update session state: {e}") from e

    async def end_session(self, session_id: UUID) -> None:
        """End a session.

        Args:
            session_id: Session ID

        Raises:
            StorageError: If ending fails
        """
        await self._ensure_initialized()

        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE session_contexts
                    SET is_active = FALSE, ended_at = NOW()
                    WHERE session_id = $1
                    """,
                    session_id,
                )

        except Exception as e:
            raise StorageError(f"Failed to end session: {e}") from e

    async def get_context(
        self,
        conversation_id: UUID,
        max_turns: int | None = None,
    ) -> ConversationContext:
        """Get conversation context.

        Args:
            conversation_id: Conversation ID
            max_turns: Maximum number of message turns to include

        Returns:
            ConversationContext: Conversation context

        Raises:
            StorageError: If retrieval fails
        """
        await self._ensure_initialized()

        try:
            async with self._pool.acquire() as conn:
                # Get conversation details
                conv_row = await conn.fetchrow(
                    """
                    SELECT conversation_id, user_id, title, metadata, message_count, created_at, updated_at
                    FROM conversation_contexts
                    WHERE conversation_id = $1
                    """,
                    conversation_id,
                )

                if not conv_row:
                    raise StorageError(f"Conversation {conversation_id} not found")

                # Get recent messages
                messages = await self.retrieve_messages(
                    conversation_id,
                    limit=max_turns * 2 if max_turns else None,  # Estimate 2 messages per turn
                )

            return ConversationContext(
                conversation_id=conv_row["conversation_id"],
                user_id=conv_row["user_id"],
                messages=messages,
                metadata=dict(conv_row["metadata"]) if conv_row["metadata"] else {},
                created_at=conv_row["created_at"],
                updated_at=conv_row["updated_at"],
            )

        except Exception as e:
            raise StorageError(f"Failed to get context: {e}") from e

    async def clear_history(
        self,
        conversation_id: UUID,
        before: datetime | None = None,
    ) -> int:
        """Clear message history.

        Args:
            conversation_id: Conversation ID
            before: Only clear messages before this timestamp

        Returns:
            int: Number of messages deleted

        Raises:
            StorageError: If clearing fails
        """
        await self._ensure_initialized()

        try:
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    if before:
                        result = await conn.execute(
                            """
                            DELETE FROM messages
                            WHERE conversation_id = $1 AND timestamp < $2
                            """,
                            conversation_id,
                            before,
                        )
                    else:
                        result = await conn.execute(
                            """
                            DELETE FROM messages
                            WHERE conversation_id = $1
                            """,
                            conversation_id,
                        )

                    # Update conversation context
                    count_row = await conn.fetchrow(
                        """
                        SELECT COUNT(*) as count FROM messages
                        WHERE conversation_id = $1
                        """,
                        conversation_id,
                    )

                    await conn.execute(
                        """
                        UPDATE conversation_contexts
                        SET message_count = $2, updated_at = NOW()
                        WHERE conversation_id = $1
                        """,
                        conversation_id,
                        count_row["count"],
                    )

                    # Parse deletion count from result
                    deleted = int(result.split()[-1])
                    return deleted

        except Exception as e:
            raise StorageError(f"Failed to clear history: {e}") from e

    async def get_statistics(self) -> dict[str, Any]:
        """Get backend statistics.

        Returns:
            Dict[str, Any]: Statistics dictionary

        Raises:
            StorageError: If retrieval fails
        """
        await self._ensure_initialized()

        try:
            async with self._pool.acquire() as conn:
                stats = {}

                # Message statistics
                msg_row = await conn.fetchrow("SELECT COUNT(*) as count FROM messages")
                stats["total_messages"] = msg_row["count"]

                # Memory statistics
                mem_row = await conn.fetchrow(
                    "SELECT COUNT(*) as count FROM memory_entries WHERE expires_at IS NULL OR expires_at > NOW()"
                )
                stats["total_memories"] = mem_row["count"]

                # Session statistics
                sess_row = await conn.fetchrow(
                    "SELECT COUNT(*) as count FROM session_contexts WHERE is_active = TRUE"
                )
                stats["active_sessions"] = sess_row["count"]

                # Conversation statistics
                conv_row = await conn.fetchrow(
                    "SELECT COUNT(*) as count FROM conversation_contexts"
                )
                stats["total_conversations"] = conv_row["count"]

                # Pool statistics
                stats["pool_size"] = self._pool.get_size()
                stats["pool_free"] = self._pool.get_idle_size()

                return stats

        except Exception as e:
            raise StorageError(f"Failed to get statistics: {e}") from e
