"""
SQLite backend implementation for bruno-memory.

Provides a high-performance, file-based memory storage solution
with full-text search, embedding support, and ACID compliance.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

import aiosqlite
from bruno_core.models import (
    ConversationContext,
    MemoryEntry,
    MemoryQuery,
    Message,
    SessionContext,
)
from bruno_core.models.context import UserContext

from ...base import BaseMemoryBackend, SQLiteConfig
from ...exceptions import (
    ConnectionError,
    DuplicateError,
    NotFoundError,
    QueryError,
    StorageError,
)
from .schema import get_full_schema_sql


class SQLiteMemoryBackend(BaseMemoryBackend):
    """SQLite-based memory backend with async support."""

    def __init__(self, config: SQLiteConfig):
        """Initialize SQLite backend.

        Args:
            config: SQLite configuration
        """
        super().__init__(config)
        self.config: SQLiteConfig = config
        self._db_path = Path(config.database_path)
        self._connection: aiosqlite.Connection | None = None

        # Ensure database directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    async def connect(self) -> None:
        """Connect to SQLite database and initialize schema."""
        if self._connected:
            return

        try:
            self._connection = await aiosqlite.connect(
                str(self._db_path), timeout=self.config.connection_timeout
            )

            # Configure SQLite for optimal performance
            await self._connection.execute("PRAGMA journal_mode = WAL")
            await self._connection.execute("PRAGMA synchronous = NORMAL")
            await self._connection.execute("PRAGMA cache_size = -64000")  # 64MB cache
            await self._connection.execute("PRAGMA foreign_keys = ON")
            await self._connection.execute("PRAGMA temp_store = MEMORY")

            # Initialize schema
            await self._initialize_schema()

            self._connected = True

        except Exception as e:
            raise ConnectionError(f"Failed to connect to SQLite database: {e}")

    async def disconnect(self) -> None:
        """Disconnect from SQLite database."""
        if self._connection:
            try:
                await self._connection.close()
            except Exception:
                pass  # Ignore close errors
            finally:
                self._connection = None
                self._connected = False

    async def health_check(self) -> bool:
        """Check SQLite database health."""
        if not self._connected or not self._connection:
            return False

        try:
            async with self._connection.execute("SELECT 1") as cursor:
                result = await cursor.fetchone()
                return result is not None
        except Exception:
            return False

    async def _initialize_schema(self) -> None:
        """Initialize database schema if needed."""
        try:
            # Execute schema SQL
            await self._connection.executescript(get_full_schema_sql())
            await self._connection.commit()

        except Exception as e:
            raise StorageError(f"Failed to initialize SQLite schema: {e}")

    # MemoryInterface implementation

    async def store_message(self, message: Message) -> None:
        """Store a message in the database."""
        self.validate_message(message)

        try:
            data = self.serialize_message(message)

            await self._connection.execute(
                """
                INSERT INTO messages (
                    id, role, content, message_type, timestamp,
                    metadata, parent_id, conversation_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data["id"],
                    data["role"],
                    data["content"],
                    data["message_type"],
                    data["timestamp"],
                    data["metadata"],
                    data["parent_id"],
                    data["conversation_id"],
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            # Update conversation message count
            await self._update_conversation_count(message.conversation_id)

            await self._connection.commit()

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateError(f"Message {message.id} already exists")
            raise StorageError(f"Failed to store message: {e}")
        except Exception as e:
            raise StorageError(f"Failed to store message: {e}")

    async def get_message(self, message_id: UUID) -> Message:
        """Retrieve a message by ID."""
        try:
            async with self._connection.execute(
                "SELECT * FROM messages WHERE id = ?", (str(message_id),)
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    raise NotFoundError(f"Message {message_id} not found")

                # Convert row to dict
                columns = [desc[0] for desc in cursor.description]
                data = dict(zip(columns, row))

                return self.deserialize_message(data)

        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to retrieve message: {e}")

    async def get_messages(
        self,
        conversation_id: str | None = None,
        user_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Message]:
        """Retrieve messages with optional filtering."""
        try:
            query_parts = ["SELECT * FROM messages"]
            params = []
            conditions = []

            if conversation_id:
                conditions.append("conversation_id = ?")
                params.append(conversation_id)

            if user_id:
                # Note: Messages don't have user_id directly, would need to join
                # with conversation context or add user_id to messages table
                pass

            if conditions:
                query_parts.append("WHERE " + " AND ".join(conditions))

            query_parts.append("ORDER BY timestamp ASC")
            query_parts.append("LIMIT ? OFFSET ?")
            params.extend([limit, offset])

            query = " ".join(query_parts)

            messages = []
            async with self._connection.execute(query, params) as cursor:
                columns = [desc[0] for desc in cursor.description]
                async for row in cursor:
                    data = dict(zip(columns, row))
                    messages.append(self.deserialize_message(data))

            return messages

        except Exception as e:
            raise StorageError(f"Failed to retrieve messages: {e}")

    async def store_memory(self, memory_entry: MemoryEntry) -> None:
        """Store a memory entry in the database."""
        self.validate_memory_entry(memory_entry)

        try:
            data = self.serialize_memory_entry(memory_entry)

            await self._connection.execute(
                """
                INSERT INTO memory_entries (
                    id, content, memory_type, user_id, conversation_id,
                    metadata, created_at, updated_at, last_accessed, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data["id"],
                    data["content"],
                    data["memory_type"],
                    data["user_id"],
                    data["conversation_id"],
                    data["metadata"],
                    data["created_at"],
                    data["updated_at"],
                    data["last_accessed"],
                    data["expires_at"],
                ),
            )

            await self._connection.commit()

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateError(f"Memory entry {memory_entry.id} already exists")
            raise StorageError(f"Failed to store memory: {e}")
        except Exception as e:
            raise StorageError(f"Failed to store memory: {e}")

    async def get_memory(self, memory_id: UUID) -> MemoryEntry:
        """Retrieve a memory entry by ID."""
        try:
            async with self._connection.execute(
                "SELECT * FROM memory_entries WHERE id = ?", (str(memory_id),)
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    raise NotFoundError(f"Memory entry {memory_id} not found")

                columns = [desc[0] for desc in cursor.description]
                data = dict(zip(columns, row))

                # Update last accessed time
                await self._update_memory_access_time(memory_id)

                return self.deserialize_memory_entry(data)

        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to retrieve memory: {e}")

    async def search_memories(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Search memory entries based on query criteria."""
        try:
            filters = self.build_memory_query_filters(query)

            # Build dynamic query based on filters
            query_parts = ["SELECT * FROM memory_entries"]
            params = []
            conditions = []

            if filters.get("user_id"):
                conditions.append("user_id = ?")
                params.append(filters["user_id"])

            if filters.get("memory_types"):
                placeholders = ",".join("?" * len(filters["memory_types"]))
                conditions.append(f"memory_type IN ({placeholders})")
                params.extend(filters["memory_types"])

            if filters.get("query_text"):
                # Use FTS for text search
                conditions.append("id IN (SELECT id FROM memory_entries_fts WHERE content MATCH ?)")
                params.append(filters["query_text"])

            # Add expiration filter
            if not filters.get("include_expired", False):
                conditions.append("(expires_at IS NULL OR expires_at > ?)")
                params.append(datetime.now(timezone.utc).isoformat())

            if conditions:
                query_parts.append("WHERE " + " AND ".join(conditions))

            # Add ordering and limits
            query_parts.append("ORDER BY updated_at DESC")

            if filters.get("limit"):
                query_parts.append("LIMIT ?")
                params.append(filters["limit"])

            query_sql = " ".join(query_parts)

            memories = []
            async with self._connection.execute(query_sql, params) as cursor:
                columns = [desc[0] for desc in cursor.description]
                async for row in cursor:
                    data = dict(zip(columns, row))
                    memories.append(self.deserialize_memory_entry(data))

            return memories

        except Exception as e:
            raise QueryError(f"Failed to search memories: {e}")

    async def update_memory(self, memory_id: UUID, updates: dict[str, Any]) -> None:
        """Update a memory entry."""
        try:
            # Build dynamic update query
            set_clauses = []
            params = []

            for field, value in updates.items():
                if field in ["content", "memory_type", "user_id", "conversation_id", "expires_at"]:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
                elif field == "metadata":
                    set_clauses.append("metadata = ?")
                    params.append(json.dumps(value) if isinstance(value, dict) else value)

            if not set_clauses:
                return  # Nothing to update

            # Always update the updated_at timestamp
            set_clauses.append("updated_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())

            params.append(str(memory_id))

            query = f"UPDATE memory_entries SET {', '.join(set_clauses)} WHERE id = ?"

            async with self._connection.execute(query, params) as cursor:
                if cursor.rowcount == 0:
                    raise NotFoundError(f"Memory entry {memory_id} not found")

            await self._connection.commit()

        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to update memory: {e}")

    async def delete_memory(self, memory_id: UUID) -> None:
        """Delete a memory entry."""
        try:
            async with self._connection.execute(
                "DELETE FROM memory_entries WHERE id = ?", (str(memory_id),)
            ) as cursor:
                if cursor.rowcount == 0:
                    raise NotFoundError(f"Memory entry {memory_id} not found")

            await self._connection.commit()

        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to delete memory: {e}")

    async def store_session_context(self, session: SessionContext) -> None:
        """Store session context."""
        try:
            data = self.serialize_session_context(session)

            await self._connection.execute(
                """
                INSERT OR REPLACE INTO session_contexts (
                    session_id, user_id, conversation_id, started_at,
                    ended_at, last_activity, is_active, state, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data["session_id"],
                    data["user_id"],
                    data["conversation_id"],
                    data["started_at"],
                    data["ended_at"],
                    data["last_activity"],
                    data["is_active"],
                    data["state"],
                    data["metadata"],
                ),
            )

            await self._connection.commit()

        except Exception as e:
            raise StorageError(f"Failed to store session context: {e}")

    async def get_session_context(self, session_id: str) -> SessionContext:
        """Retrieve session context by ID."""
        try:
            async with self._connection.execute(
                "SELECT * FROM session_contexts WHERE session_id = ?", (session_id,)
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    raise NotFoundError(f"Session {session_id} not found")

                columns = [desc[0] for desc in cursor.description]
                data = dict(zip(columns, row))

                return self.deserialize_session_context(data)

        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to retrieve session context: {e}")

    async def get_context(self, user_id: str, conversation_id: str) -> ConversationContext:
        """Retrieve conversation context."""
        try:
            # Get user context
            user_context = await self._get_or_create_user_context(user_id)

            # Get or create conversation context
            conversation_context = await self._get_or_create_conversation_context(
                conversation_id, user_id
            )

            # Get session context (latest active session for this conversation)
            session_context = await self._get_latest_session_context(user_id, conversation_id)

            # Get recent messages for this conversation
            messages = await self.get_messages(
                conversation_id=conversation_id, limit=self.config.max_context_messages
            )

            # Parse metadata from JSON string
            metadata_str = conversation_context.get("metadata", "{}")
            metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str

            return ConversationContext(
                conversation_id=conversation_id,
                user=user_context,
                session=session_context,
                messages=messages,
                metadata=metadata,
            )

        except Exception as e:
            raise StorageError(f"Failed to get conversation context: {e}")

    async def clear_history(self, conversation_id: str) -> None:
        """Clear conversation history."""
        try:
            # Delete messages for this conversation
            await self._connection.execute(
                "DELETE FROM messages WHERE conversation_id = ?", (conversation_id,)
            )

            # Reset conversation message count
            await self._connection.execute(
                """
                UPDATE conversation_contexts 
                SET message_count = 0, updated_at = ? 
                WHERE conversation_id = ?
            """,
                (datetime.now(timezone.utc).isoformat(), conversation_id),
            )

            await self._connection.commit()

        except Exception as e:
            raise StorageError(f"Failed to clear conversation history: {e}")

    # Helper methods

    async def _update_conversation_count(self, conversation_id: str) -> None:
        """Update message count for a conversation."""
        await self._connection.execute(
            """
            UPDATE conversation_contexts 
            SET message_count = message_count + 1, updated_at = ?
            WHERE conversation_id = ?
        """,
            (datetime.now(timezone.utc).isoformat(), conversation_id),
        )

    async def _update_memory_access_time(self, memory_id: UUID) -> None:
        """Update last accessed time for a memory entry."""
        await self._connection.execute(
            """
            UPDATE memory_entries 
            SET last_accessed = ?
            WHERE id = ?
        """,
            (datetime.now(timezone.utc).isoformat(), str(memory_id)),
        )
        await self._connection.commit()

    async def _get_or_create_user_context(self, user_id: str) -> UserContext:
        """Get or create user context."""
        try:
            async with self._connection.execute(
                "SELECT * FROM user_contexts WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()

                if row:
                    columns = [desc[0] for desc in cursor.description]
                    data = dict(zip(columns, row))
                    return self.deserialize_user_context(data)
                else:
                    # Create new user context
                    user_context = UserContext(user_id=user_id)
                    await self._store_user_context(user_context)
                    return user_context

        except Exception as e:
            raise StorageError(f"Failed to get/create user context: {e}")

    async def _store_user_context(self, user_context: UserContext) -> None:
        """Store user context."""
        data = self.serialize_user_context(user_context)

        await self._connection.execute(
            """
            INSERT OR REPLACE INTO user_contexts (
                user_id, name, preferences, profile, metadata, created_at, last_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["user_id"],
                data["name"],
                data["preferences"],
                data["profile"],
                data["metadata"],
                data["created_at"],
                data["last_active"],
            ),
        )

    async def _get_or_create_conversation_context(
        self, conversation_id: str, user_id: str
    ) -> dict[str, Any]:
        """Get or create conversation context record."""
        try:
            async with self._connection.execute(
                "SELECT * FROM conversation_contexts WHERE conversation_id = ?", (conversation_id,)
            ) as cursor:
                row = await cursor.fetchone()

                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                else:
                    # Create new conversation context
                    now = datetime.now(timezone.utc).isoformat()
                    await self._connection.execute(
                        """
                        INSERT INTO conversation_contexts (
                            conversation_id, user_id, metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?)
                    """,
                        (conversation_id, user_id, "{}", now, now),
                    )

                    return {
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "metadata": "{}",
                        "created_at": now,
                        "updated_at": now,
                    }

        except Exception as e:
            raise StorageError(f"Failed to get/create conversation context: {e}")

    async def _get_latest_session_context(
        self, user_id: str, conversation_id: str
    ) -> SessionContext:
        """Get the latest session context for a conversation."""
        try:
            async with self._connection.execute(
                """
                SELECT * FROM session_contexts 
                WHERE user_id = ? AND conversation_id = ? 
                ORDER BY last_activity DESC 
                LIMIT 1
            """,
                (user_id, conversation_id),
            ) as cursor:
                row = await cursor.fetchone()

                if row:
                    columns = [desc[0] for desc in cursor.description]
                    data = dict(zip(columns, row))
                    return self.deserialize_session_context(data)
                else:
                    # Create new session context
                    session_context = SessionContext(
                        user_id=user_id, conversation_id=conversation_id
                    )
                    await self.store_session_context(session_context)
                    return session_context

        except Exception as e:
            raise StorageError(f"Failed to get latest session context: {e}")

    # Additional MemoryInterface methods

    async def create_session(self, user_id: str, conversation_id: str) -> SessionContext:
        """Create a new session context."""
        session_context = SessionContext(user_id=user_id, conversation_id=conversation_id)
        await self.store_session_context(session_context)
        return session_context

    async def end_session(self, session_id: str) -> None:
        """End a session by setting it inactive."""
        try:
            await self._connection.execute(
                """
                UPDATE session_contexts 
                SET is_active = 0, ended_at = ?
                WHERE session_id = ?
            """,
                (datetime.now(timezone.utc).isoformat(), session_id),
            )

            await self._connection.commit()

        except Exception as e:
            raise StorageError(f"Failed to end session: {e}")

    async def get_session(self, session_id: str) -> SessionContext:
        """Get session context by ID (alias for get_session_context)."""
        return await self.get_session_context(session_id)

    async def retrieve_memories(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[MemoryEntry]:
        """Retrieve memories for a user."""
        query = MemoryQuery(user_id=user_id, limit=limit)
        return await self.search_memories(query)

    async def retrieve_messages(
        self, conversation_id: str, limit: int = 100, offset: int = 0
    ) -> list[Message]:
        """Retrieve messages for a conversation (alias for get_messages)."""
        return await self.get_messages(conversation_id=conversation_id, limit=limit, offset=offset)

    async def search_messages(
        self, query_text: str, conversation_id: str | None = None, limit: int = 50
    ) -> list[Message]:
        """Search messages by text content."""
        try:
            query_parts = ["SELECT * FROM messages"]
            params = []
            conditions = []

            # Add text search condition
            conditions.append("content LIKE ?")
            params.append(f"%{query_text}%")

            if conversation_id:
                conditions.append("conversation_id = ?")
                params.append(conversation_id)

            query_parts.append("WHERE " + " AND ".join(conditions))
            query_parts.append("ORDER BY timestamp DESC")
            query_parts.append("LIMIT ?")
            params.append(limit)

            query_sql = " ".join(query_parts)

            messages = []
            async with self._connection.execute(query_sql, params) as cursor:
                columns = [desc[0] for desc in cursor.description]
                async for row in cursor:
                    data = dict(zip(columns, row))
                    messages.append(self.deserialize_message(data))

            return messages

        except Exception as e:
            raise QueryError(f"Failed to search messages: {e}")

    async def get_statistics(self) -> dict[str, Any]:
        """Get database statistics."""
        try:
            stats = {}

            # Get message count
            async with self._connection.execute("SELECT COUNT(*) FROM messages") as cursor:
                row = await cursor.fetchone()
                stats["total_messages"] = row[0] if row else 0

            # Get memory count
            async with self._connection.execute("SELECT COUNT(*) FROM memory_entries") as cursor:
                row = await cursor.fetchone()
                stats["total_memories"] = row[0] if row else 0

            # Get user count
            async with self._connection.execute("SELECT COUNT(*) FROM user_contexts") as cursor:
                row = await cursor.fetchone()
                stats["total_users"] = row[0] if row else 0

            # Get conversation count
            async with self._connection.execute(
                "SELECT COUNT(*) FROM conversation_contexts"
            ) as cursor:
                row = await cursor.fetchone()
                stats["total_conversations"] = row[0] if row else 0

            # Get active session count
            async with self._connection.execute(
                "SELECT COUNT(*) FROM session_contexts WHERE is_active = 1"
            ) as cursor:
                row = await cursor.fetchone()
                stats["active_sessions"] = row[0] if row else 0

            # Get database size
            stats["database_path"] = str(self._db_path)
            if self._db_path.exists():
                stats["database_size_bytes"] = self._db_path.stat().st_size

            return stats

        except Exception as e:
            raise StorageError(f"Failed to get statistics: {e}")
