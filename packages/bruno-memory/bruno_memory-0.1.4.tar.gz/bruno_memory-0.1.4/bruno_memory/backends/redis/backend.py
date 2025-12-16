"""
Redis backend implementation for bruno-memory.

Optimized for caching, session management, and real-time operations
with automatic expiration and pub/sub support.
"""

import pickle
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

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
from redis.asyncio import ConnectionPool, Redis

from bruno_memory.base.base_backend import BaseMemoryBackend
from bruno_memory.base.config import RedisConfig
from bruno_memory.exceptions import (
    ConnectionError,
    NotFoundError,
    StorageError,
)


class RedisMemoryBackend(BaseMemoryBackend):
    """
    Redis backend for bruno-memory.

    Features:
    - In-memory storage with optional persistence
    - Automatic key expiration (TTL)
    - High-performance caching
    - Pub/Sub for real-time events
    - Session state management

    Key Structure:
    - msg:{conversation_id}:{message_id} - Individual messages
    - msgs:{conversation_id} - Sorted set of message IDs by timestamp
    - mem:{user_id}:{memory_id} - Individual memories
    - mems:{user_id} - Set of memory IDs
    - sess:{session_id} - Session contexts
    - conv:{conversation_id} - Conversation metadata
    - user:{user_id} - User context
    """

    def __init__(self, config: RedisConfig):
        """Initialize Redis backend.

        Args:
            config: Redis configuration
        """
        super().__init__(config)
        self.config: RedisConfig = config
        self._client: Redis | None = None
        self._pool: ConnectionPool | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize Redis connection pool."""
        if self._initialized:
            return

        try:
            # Create connection pool
            self._pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.database,
                password=self.config.password if self.config.password else None,
                decode_responses=False,  # We'll handle encoding ourselves
                max_connections=self.config.max_connections,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
            )

            # Create Redis client
            self._client = Redis(connection_pool=self._pool)

            # Test connection
            await self._client.ping()

            self._initialized = True

        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}") from e

    async def connect(self) -> None:
        """Connect to Redis (alias for initialize)."""
        await self.initialize()

    async def disconnect(self) -> None:
        """Disconnect from Redis (alias for close)."""
        await self.close()

    async def health_check(self) -> bool:
        """Check if Redis backend is healthy.

        Returns:
            bool: True if healthy, False otherwise
        """
        if not self._initialized or not self._client:
            return False

        try:
            await self._client.ping()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close Redis connection and pool."""
        if self._client:
            await self._client.close()
            self._client = None

        if self._pool:
            await self._pool.disconnect()
            self._pool = None

        self._initialized = False

    def _serialize(self, obj: Any) -> bytes:
        """Serialize object to bytes using pickle.

        Args:
            obj: Object to serialize

        Returns:
            bytes: Serialized data
        """
        return pickle.dumps(obj)

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to object.

        Args:
            data: Serialized data

        Returns:
            Any: Deserialized object
        """
        return pickle.loads(data)

    def _get_message_key(self, conversation_id: UUID, message_id: UUID) -> str:
        """Get Redis key for a message."""
        return f"msg:{conversation_id}:{message_id}"

    def _get_messages_set_key(self, conversation_id: UUID) -> str:
        """Get Redis key for messages sorted set."""
        return f"msgs:{conversation_id}"

    def _get_memory_key(self, user_id: str, memory_id: UUID) -> str:
        """Get Redis key for a memory entry."""
        return f"mem:{user_id}:{memory_id}"

    def _get_memories_set_key(self, user_id: str) -> str:
        """Get Redis key for memories set."""
        return f"mems:{user_id}"

    def _get_session_key(self, session_id: UUID) -> str:
        """Get Redis key for a session."""
        return f"sess:{session_id}"

    def _get_conversation_key(self, conversation_id: UUID) -> str:
        """Get Redis key for conversation metadata."""
        return f"conv:{conversation_id}"

    def _get_user_key(self, user_id: str) -> str:
        """Get Redis key for user context."""
        return f"user:{user_id}"

    async def store_message(
        self,
        message: Message,
        conversation_id: UUID,
        parent_id: UUID | None = None,
    ) -> UUID:
        """Store a message in Redis.

        Args:
            message: Message to store
            conversation_id: Conversation ID
            parent_id: Optional parent message ID

        Returns:
            UUID: Message ID

        Raises:
            StorageError: If storage fails
        """
        await self._ensure_initialized()
        self.validate_message(message)

        try:
            message_id = uuid4()
            timestamp = message.timestamp or datetime.now()

            # Store message data
            message_data = {
                "id": str(message_id),
                "role": (
                    message.role.value if isinstance(message.role, MessageRole) else message.role
                ),
                "content": message.content,
                "message_type": message.message_type or "text",
                "timestamp": timestamp.isoformat(),
                "metadata": message.metadata or {},
                "parent_id": str(parent_id) if parent_id else None,
                "conversation_id": str(conversation_id),
            }

            message_key = self._get_message_key(conversation_id, message_id)
            messages_set_key = self._get_messages_set_key(conversation_id)

            # Use pipeline for atomic operations
            async with self._client.pipeline(transaction=True) as pipe:
                # Store message
                pipe.set(message_key, self._serialize(message_data))

                # Add to sorted set (sorted by timestamp)
                pipe.zadd(messages_set_key, {str(message_id): timestamp.timestamp()})

                # Set TTL if configured
                if self.config.ttl_default:
                    pipe.expire(message_key, self.config.ttl_default)
                    pipe.expire(messages_set_key, self.config.ttl_default)

                await pipe.execute()

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
        """Retrieve messages from Redis.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
            before: Only messages before this timestamp
            after: Only messages after this timestamp

        Returns:
            List[Message]: Retrieved messages

        Raises:
            StorageError: If retrieval fails
        """
        await self._ensure_initialized()

        try:
            messages_set_key = self._get_messages_set_key(conversation_id)

            # Determine score range for timestamp filtering
            min_score = after.timestamp() if after else "-inf"
            max_score = before.timestamp() if before else "+inf"

            # Get message IDs from sorted set
            message_ids = await self._client.zrangebyscore(
                messages_set_key,
                min_score,
                max_score,
                start=0,
                num=limit if limit else -1,
            )

            if not message_ids:
                return []

            # Retrieve message data
            messages = []
            for msg_id_bytes in message_ids:
                msg_id = msg_id_bytes.decode("utf-8")
                message_key = self._get_message_key(conversation_id, UUID(msg_id))

                data = await self._client.get(message_key)
                if data:
                    message_data = self._deserialize(data)
                    message = Message(
                        role=MessageRole(message_data["role"]),
                        content=message_data["content"],
                        message_type=message_data["message_type"],
                        timestamp=datetime.fromisoformat(message_data["timestamp"]),
                        metadata=message_data.get("metadata", {}),
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
        """Search messages (basic content filtering in Redis).

        Note: Redis doesn't have full-text search built-in.
        This performs simple substring matching.
        For production full-text search, use PostgreSQL or a search engine.

        Args:
            query: Search query
            conversation_id: Optional conversation ID to filter
            limit: Maximum results

        Returns:
            List[Message]: Matching messages
        """
        await self._ensure_initialized()

        try:
            if conversation_id:
                messages = await self.retrieve_messages(conversation_id, limit=None)
            else:
                # Search across all conversations (expensive!)
                # In production, maintain a separate index
                messages = []
                cursor = 0
                while True:
                    cursor, keys = await self._client.scan(cursor, match="msg:*:*", count=100)
                    for key in keys:
                        data = await self._client.get(key)
                        if data:
                            message_data = self._deserialize(data)
                            message = Message(
                                role=MessageRole(message_data["role"]),
                                content=message_data["content"],
                                message_type=message_data["message_type"],
                                timestamp=datetime.fromisoformat(message_data["timestamp"]),
                                metadata=message_data.get("metadata", {}),
                            )
                            messages.append(message)

                    if cursor == 0:
                        break

            # Filter by query
            query_lower = query.lower()
            results = [m for m in messages if query_lower in m.content.lower()]

            return results[:limit]

        except Exception as e:
            raise StorageError(f"Failed to search messages: {e}") from e

    async def store_memory(self, memory: MemoryEntry) -> UUID:
        """Store a memory entry in Redis.

        Args:
            memory: Memory entry to store

        Returns:
            UUID: Memory ID

        Raises:
            StorageError: If storage fails
        """
        await self._ensure_initialized()
        self.validate_memory_entry(memory)

        try:
            memory_id = uuid4()

            # Extract metadata
            metadata = memory.metadata.model_dump() if memory.metadata else {}

            memory_data = {
                "id": str(memory_id),
                "content": memory.content,
                "memory_type": (
                    memory.memory_type.value
                    if isinstance(memory.memory_type, MemoryType)
                    else memory.memory_type
                ),
                "user_id": memory.user_id,
                "conversation_id": str(memory.conversation_id) if memory.conversation_id else None,
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
            }

            memory_key = self._get_memory_key(memory.user_id, memory_id)
            memories_set_key = self._get_memories_set_key(memory.user_id)

            # Calculate TTL based on expires_at
            ttl = None
            if metadata.get("expires_at"):
                expires_at = metadata["expires_at"]
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at)
                ttl = int((expires_at - datetime.now()).total_seconds())
            elif self.config.ttl_default:
                ttl = self.config.ttl_default

            # Store memory
            async with self._client.pipeline(transaction=True) as pipe:
                pipe.set(memory_key, self._serialize(memory_data))
                pipe.sadd(memories_set_key, str(memory_id))

                if ttl and ttl > 0:
                    pipe.expire(memory_key, ttl)

                await pipe.execute()

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
            limit: Maximum number of memories

        Returns:
            List[MemoryEntry]: Retrieved memories

        Raises:
            StorageError: If retrieval fails
        """
        await self._ensure_initialized()

        try:
            memories_set_key = self._get_memories_set_key(user_id)

            # Get all memory IDs
            memory_ids = await self._client.smembers(memories_set_key)

            if not memory_ids:
                return []

            # Retrieve memory data
            memories = []
            for mem_id_bytes in memory_ids:
                mem_id = mem_id_bytes.decode("utf-8")
                memory_key = self._get_memory_key(user_id, UUID(mem_id))

                data = await self._client.get(memory_key)
                if data:
                    memory_data = self._deserialize(data)

                    # Apply memory type filter
                    if memory_type and memory_data["memory_type"] != (
                        memory_type.value if isinstance(memory_type, MemoryType) else memory_type
                    ):
                        continue

                    metadata_dict = memory_data.get("metadata", {})
                    memory = MemoryEntry(
                        content=memory_data["content"],
                        memory_type=MemoryType(memory_data["memory_type"]),
                        user_id=memory_data["user_id"],
                        conversation_id=(
                            UUID(memory_data["conversation_id"])
                            if memory_data.get("conversation_id")
                            else None
                        ),
                        metadata=MemoryMetadata(**metadata_dict) if metadata_dict else None,
                    )
                    memories.append(memory)

            # Sort by importance (if available) and limit
            memories.sort(key=lambda m: m.metadata.importance if m.metadata else 0.0, reverse=True)

            if limit:
                memories = memories[:limit]

            return memories

        except Exception as e:
            raise StorageError(f"Failed to retrieve memories: {e}") from e

    async def search_memories(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Search memories (basic filtering).

        Args:
            query: Memory query

        Returns:
            List[MemoryEntry]: Matching memories

        Raises:
            StorageError: If search fails
        """
        await self._ensure_initialized()

        try:
            # Get all memories for user
            memories = await self.retrieve_memories(query.user_id, limit=None)

            # Filter by query text
            query_lower = query.query_text.lower()
            results = [m for m in memories if query_lower in m.content.lower()]

            # Filter by memory types
            if query.memory_types:
                type_values = [
                    t.value if isinstance(t, MemoryType) else t for t in query.memory_types
                ]
                results = [m for m in results if m.memory_type.value in type_values]

            # Filter by conversation ID
            if query.conversation_id:
                results = [m for m in results if m.conversation_id == query.conversation_id]

            # Filter by importance
            if query.min_importance is not None:
                results = [
                    m
                    for m in results
                    if m.metadata and m.metadata.importance >= query.min_importance
                ]

            # Limit results
            return results[: query.limit or 10]

        except Exception as e:
            raise StorageError(f"Failed to search memories: {e}") from e

    async def delete_memory(self, memory_id: UUID) -> None:
        """Delete a memory entry.

        Args:
            memory_id: Memory ID to delete

        Raises:
            StorageError: If deletion fails
        """
        await self._ensure_initialized()

        try:
            # Find the memory key by scanning
            cursor = 0
            found = False

            while True:
                cursor, keys = await self._client.scan(
                    cursor, match=f"mem:*:{memory_id}", count=100
                )

                if keys:
                    for key in keys:
                        # Extract user_id from key
                        parts = key.decode("utf-8").split(":")
                        if len(parts) == 3:
                            user_id = parts[1]
                            memories_set_key = self._get_memories_set_key(user_id)

                            # Delete memory and remove from set
                            async with self._client.pipeline(transaction=True) as pipe:
                                pipe.delete(key)
                                pipe.srem(memories_set_key, str(memory_id))
                                await pipe.execute()

                            found = True
                            break

                if cursor == 0:
                    break

            if not found:
                raise NotFoundError(f"Memory entry {memory_id} not found")

        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to delete memory: {e}") from e

    async def create_session(
        self,
        user_id: str,
        conversation_id: UUID,
        initial_state: dict[str, Any] | None = None,
    ) -> SessionContext:
        """Create a new session in Redis.

        Args:
            user_id: User ID
            conversation_id: Conversation ID
            initial_state: Optional initial state

        Returns:
            SessionContext: Created session

        Raises:
            StorageError: If creation fails
        """
        await self._ensure_initialized()

        try:
            session_id = uuid4()
            now = datetime.now()

            session_data = {
                "session_id": str(session_id),
                "user_id": user_id,
                "conversation_id": str(conversation_id),
                "started_at": now.isoformat(),
                "last_activity": now.isoformat(),
                "is_active": True,
                "state": initial_state or {},
                "metadata": {},
            }

            session_key = self._get_session_key(session_id)

            # Store session
            await self._client.set(session_key, self._serialize(session_data))

            # Set TTL if configured
            if self.config.ttl_default:
                await self._client.expire(session_key, self.config.ttl_default)

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
        """Retrieve a session from Redis.

        Args:
            session_id: Session ID

        Returns:
            Optional[SessionContext]: Session if found

        Raises:
            StorageError: If retrieval fails
        """
        await self._ensure_initialized()

        try:
            session_key = self._get_session_key(session_id)
            data = await self._client.get(session_key)

            if not data:
                return None

            session_data = self._deserialize(data)

            return SessionContext(
                session_id=UUID(session_data["session_id"]),
                user_id=session_data["user_id"],
                conversation_id=UUID(session_data["conversation_id"]),
                started_at=datetime.fromisoformat(session_data["started_at"]),
                ended_at=(
                    datetime.fromisoformat(session_data["ended_at"])
                    if session_data.get("ended_at")
                    else None
                ),
                last_activity=datetime.fromisoformat(session_data["last_activity"]),
                is_active=session_data["is_active"],
                state=session_data.get("state", {}),
                metadata=session_data.get("metadata", {}),
            )

        except Exception as e:
            raise StorageError(f"Failed to get session: {e}") from e

    async def update_session_state(
        self,
        session_id: UUID,
        state: dict[str, Any],
    ) -> None:
        """Update session state in Redis.

        Args:
            session_id: Session ID
            state: New state

        Raises:
            StorageError: If update fails
        """
        await self._ensure_initialized()

        try:
            session_key = self._get_session_key(session_id)
            data = await self._client.get(session_key)

            if not data:
                raise NotFoundError(f"Session {session_id} not found")

            session_data = self._deserialize(data)
            session_data["state"] = state
            session_data["last_activity"] = datetime.now().isoformat()

            await self._client.set(session_key, self._serialize(session_data))

            # Refresh TTL
            if self.config.ttl_default:
                await self._client.expire(session_key, self.config.ttl_default)

        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to update session state: {e}") from e

    async def end_session(self, session_id: UUID) -> None:
        """End a session in Redis.

        Args:
            session_id: Session ID

        Raises:
            StorageError: If ending fails
        """
        await self._ensure_initialized()

        try:
            session_key = self._get_session_key(session_id)
            data = await self._client.get(session_key)

            if not data:
                raise NotFoundError(f"Session {session_id} not found")

            session_data = self._deserialize(data)
            session_data["is_active"] = False
            session_data["ended_at"] = datetime.now().isoformat()

            await self._client.set(session_key, self._serialize(session_data))

        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to end session: {e}") from e

    async def get_context(
        self,
        conversation_id: UUID,
        max_turns: int | None = None,
    ) -> ConversationContext:
        """Get conversation context from Redis.

        Args:
            conversation_id: Conversation ID
            max_turns: Maximum turns to include

        Returns:
            ConversationContext: Conversation context

        Raises:
            StorageError: If retrieval fails
        """
        await self._ensure_initialized()

        try:
            # Get conversation metadata
            conv_key = self._get_conversation_key(conversation_id)
            conv_data = await self._client.get(conv_key)

            if not conv_data:
                # Create default context
                conv_metadata = {
                    "conversation_id": str(conversation_id),
                    "user_id": "unknown",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "metadata": {},
                }
            else:
                conv_metadata = self._deserialize(conv_data)

            # Get messages
            limit = max_turns * 2 if max_turns else None  # Estimate 2 messages per turn
            messages = await self.retrieve_messages(conversation_id, limit=limit)

            return ConversationContext(
                conversation_id=UUID(conv_metadata["conversation_id"]),
                user_id=conv_metadata["user_id"],
                messages=messages,
                metadata=conv_metadata.get("metadata", {}),
                created_at=datetime.fromisoformat(conv_metadata["created_at"]),
                updated_at=datetime.fromisoformat(conv_metadata["updated_at"]),
            )

        except Exception as e:
            raise StorageError(f"Failed to get context: {e}") from e

    async def clear_history(
        self,
        conversation_id: UUID,
        before: datetime | None = None,
    ) -> int:
        """Clear message history from Redis.

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
            messages_set_key = self._get_messages_set_key(conversation_id)

            if before:
                # Get messages to delete
                message_ids = await self._client.zrangebyscore(
                    messages_set_key,
                    "-inf",
                    before.timestamp(),
                )
            else:
                # Get all messages
                message_ids = await self._client.zrange(messages_set_key, 0, -1)

            if not message_ids:
                return 0

            # Delete messages
            async with self._client.pipeline(transaction=True) as pipe:
                for msg_id_bytes in message_ids:
                    msg_id = msg_id_bytes.decode("utf-8")
                    message_key = self._get_message_key(conversation_id, UUID(msg_id))
                    pipe.delete(message_key)

                # Remove from sorted set
                if before:
                    pipe.zremrangebyscore(messages_set_key, "-inf", before.timestamp())
                else:
                    pipe.delete(messages_set_key)

                await pipe.execute()

            return len(message_ids)

        except Exception as e:
            raise StorageError(f"Failed to clear history: {e}") from e

    async def get_statistics(self) -> dict[str, Any]:
        """Get Redis backend statistics.

        Returns:
            Dict[str, Any]: Statistics

        Raises:
            StorageError: If retrieval fails
        """
        await self._ensure_initialized()

        try:
            info = await self._client.info()

            # Count keys by pattern
            stats = {
                "total_messages": 0,
                "total_memories": 0,
                "active_sessions": 0,
                "total_conversations": 0,
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_keys": await self._client.dbsize(),
            }

            # Count messages (expensive operation, use with caution)
            cursor = 0
            while True:
                cursor, keys = await self._client.scan(cursor, match="msg:*:*", count=1000)
                stats["total_messages"] += len(keys)
                if cursor == 0:
                    break

            # Count memories
            cursor = 0
            while True:
                cursor, keys = await self._client.scan(cursor, match="mem:*:*", count=1000)
                stats["total_memories"] += len(keys)
                if cursor == 0:
                    break

            # Count active sessions
            cursor = 0
            while True:
                cursor, keys = await self._client.scan(cursor, match="sess:*", count=1000)
                for key in keys:
                    data = await self._client.get(key)
                    if data:
                        session_data = self._deserialize(data)
                        if session_data.get("is_active", False):
                            stats["active_sessions"] += 1
                if cursor == 0:
                    break

            return stats

        except Exception as e:
            raise StorageError(f"Failed to get statistics: {e}") from e
