"""
Qdrant backend implementation for bruno-memory.

Provides vector storage and semantic search using Qdrant.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from bruno_core.models import MemoryEntry, MemoryType, Message
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    Range,
    VectorParams,
)

from bruno_memory.base.base_backend import BaseMemoryBackend
from bruno_memory.base.config import QdrantConfig
from bruno_memory.exceptions import (
    ConnectionError,
    MemoryError,
    QueryError,
)

logger = logging.getLogger(__name__)


class QdrantBackend(BaseMemoryBackend):
    """
    Qdrant backend for bruno-memory with vector search capabilities.

    Features:
    - High-performance vector search
    - Persistent storage
    - Metadata filtering
    - Multiple distance metrics
    - Async operations
    """

    def __init__(self, config: QdrantConfig):
        """Initialize Qdrant backend."""
        super().__init__(config)
        self.config: QdrantConfig = config
        self._client: AsyncQdrantClient | None = None
        self._is_connected: bool = False

    async def initialize(self) -> None:
        """Initialize Qdrant client and collection."""
        try:
            # Initialize async client
            self._client = AsyncQdrantClient(
                host=self.config.host,
                port=self.config.port,
                api_key=self.config.api_key,
                timeout=self.config.timeout,
            )

            # Map distance metric
            distance_map = {
                "cosine": Distance.COSINE,
                "euclidean": Distance.EUCLID,
                "dot": Distance.DOT,
            }
            distance = distance_map.get(self.config.distance_metric, Distance.COSINE)

            # Create collection if it doesn't exist
            try:
                await self._client.get_collection(self.config.collection_name)
                logger.info(f"Using existing collection: {self.config.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                await self._client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=VectorParams(size=self.config.vector_size, distance=distance),
                )
                logger.info(f"Created collection: {self.config.collection_name}")

            self._is_connected = True
            logger.info(f"Qdrant backend initialized at {self.config.get_connection_string()}")

        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}")
            raise ConnectionError(f"Qdrant initialization failed: {e}")

    async def close(self) -> None:
        """Close Qdrant connection."""
        try:
            if self._client:
                await self._client.close()
                self._client = None

            self._is_connected = False
            logger.info("Qdrant connection closed")

        except Exception as e:
            logger.error(f"Error closing Qdrant: {e}")

    # Abstract method implementations from BaseMemoryBackend
    async def connect(self) -> None:
        """Connect to Qdrant (alias for initialize)."""
        await self.initialize()

    async def disconnect(self) -> None:
        """Disconnect from Qdrant (alias for close)."""
        await self.close()

    async def health_check(self) -> bool:
        """Check if Qdrant is healthy."""
        try:
            if not self._is_connected or not self._client:
                return False
            # Try to get collection info
            await self._client.get_collection(self.config.collection_name)
            return True
        except Exception:
            return False

    async def store_message(
        self,
        session_id: str,
        message: Message,
        metadata: dict[str, Any] | None = None,
        embedding: list[float] | None = None,
    ) -> str:
        """
        Store a message with vector embedding.

        Args:
            session_id: Session identifier
            message: Message to store
            metadata: Optional metadata
            embedding: Pre-computed embedding vector (required for Qdrant)

        Returns:
            Message ID
        """
        self._ensure_connected()

        if not embedding:
            raise ValueError("Embedding vector is required for Qdrant backend")

        if len(embedding) != self.config.vector_size:
            raise ValueError(
                f"Embedding size {len(embedding)} doesn't match "
                f"configured size {self.config.vector_size}"
            )

        try:
            # Generate unique ID
            message_id = str(uuid4())

            # Prepare payload
            payload = {
                "session_id": session_id,
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "type": "message",
            }

            if metadata:
                payload.update(metadata)

            # Create point
            point = PointStruct(id=message_id, vector=embedding, payload=payload)

            # Upsert point
            await self._client.upsert(collection_name=self.config.collection_name, points=[point])

            logger.debug(f"Stored message {message_id} in Qdrant")
            return message_id

        except Exception as e:
            logger.error(f"Failed to store message: {e}")
            raise MemoryError(f"Failed to store message: {e}")

    async def retrieve_messages(
        self, session_id: str, limit: int = 100, offset: int = 0
    ) -> list[Message]:
        """Retrieve messages for a session."""
        self._ensure_connected()

        try:
            # Build filter
            query_filter = Filter(
                must=[
                    FieldCondition(key="session_id", match=MatchValue(value=session_id)),
                    FieldCondition(key="type", match=MatchValue(value="message")),
                ]
            )

            # Scroll through results
            points, _ = await self._client.scroll(
                collection_name=self.config.collection_name,
                scroll_filter=query_filter,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            messages = []
            for point in points:
                payload = point.payload
                message = Message(
                    role=payload["role"],
                    content=payload["content"],
                    timestamp=datetime.fromisoformat(payload["timestamp"]),
                )
                messages.append(message)

            # Sort by timestamp
            messages.sort(key=lambda m: m.timestamp)

            logger.debug(f"Retrieved {len(messages)} messages for session {session_id}")
            return messages

        except Exception as e:
            logger.error(f"Failed to retrieve messages: {e}")
            raise QueryError(f"Failed to retrieve messages: {e}")

    async def search_similar(
        self,
        query_vector: list[float],
        limit: int = 10,
        session_id: str | None = None,
        min_score: float = 0.0,
    ) -> list[tuple[Message, float]]:
        """
        Search for semantically similar messages.

        Args:
            query_vector: Query embedding vector
            limit: Maximum results
            session_id: Optional session filter
            min_score: Minimum similarity score

        Returns:
            List of (message, score) tuples
        """
        self._ensure_connected()

        if len(query_vector) != self.config.vector_size:
            raise ValueError(
                f"Query vector size {len(query_vector)} doesn't match "
                f"configured size {self.config.vector_size}"
            )

        try:
            # Build filter
            must_conditions = [FieldCondition(key="type", match=MatchValue(value="message"))]

            if session_id:
                must_conditions.append(
                    FieldCondition(key="session_id", match=MatchValue(value=session_id))
                )

            query_filter = Filter(must=must_conditions)

            # Search
            results = await self._client.search(
                collection_name=self.config.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=min_score,
            )

            matches = []
            for scored_point in results:
                payload = scored_point.payload
                message = Message(
                    role=payload["role"],
                    content=payload["content"],
                    timestamp=datetime.fromisoformat(payload["timestamp"]),
                )
                matches.append((message, scored_point.score))

            logger.debug(f"Found {len(matches)} similar messages")
            return matches

        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise QueryError(f"Similarity search failed: {e}")

    async def store_memory(
        self,
        memory: MemoryEntry,
        metadata: dict[str, Any] | None = None,
        embedding: list[float] | None = None,
    ) -> str:
        """Store a memory entry with vector embedding."""
        self._ensure_connected()

        if not embedding:
            raise ValueError("Embedding vector is required for Qdrant backend")

        if len(embedding) != self.config.vector_size:
            raise ValueError(
                f"Embedding size {len(embedding)} doesn't match "
                f"configured size {self.config.vector_size}"
            )

        try:
            # Generate unique ID
            memory_id = str(uuid4())

            # Prepare payload
            payload = {
                "type": "memory",
                "content": memory.content,
                "timestamp": memory.created_at.isoformat(),
                "memory_type": memory.memory_type.value,
                "user_id": memory.user_id,
            }

            if memory.metadata:
                if memory.metadata.tags:
                    payload["tags"] = list(memory.metadata.tags)
                payload["importance"] = memory.metadata.importance
                if memory.metadata.source:
                    payload["source"] = memory.metadata.source

            if metadata:
                payload.update(metadata)

            # Create point
            point = PointStruct(id=memory_id, vector=embedding, payload=payload)

            # Upsert point
            await self._client.upsert(collection_name=self.config.collection_name, points=[point])

            logger.debug(f"Stored memory {memory_id} in Qdrant")
            return memory_id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise MemoryError(f"Failed to store memory: {e}")

    async def retrieve_memories(
        self, tags: set[str] | None = None, min_importance: float = 0.0, limit: int = 100
    ) -> list[MemoryEntry]:
        """Retrieve memories filtered by tags and importance."""
        self._ensure_connected()

        try:
            # Build filter
            must_conditions = [
                FieldCondition(key="type", match=MatchValue(value="memory")),
                FieldCondition(key="importance", range=Range(gte=min_importance)),
            ]

            if tags:
                for tag in tags:
                    must_conditions.append(FieldCondition(key="tags", match=MatchValue(value=tag)))

            query_filter = Filter(must=must_conditions)

            # Scroll through results
            points, _ = await self._client.scroll(
                collection_name=self.config.collection_name,
                scroll_filter=query_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )

            memories = []
            for point in points:
                payload = point.payload
                memory = MemoryEntry(
                    content=payload["content"],
                    memory_type=MemoryType(payload.get("memory_type", "fact")),
                    user_id=payload.get("user_id", "default"),
                    created_at=datetime.fromisoformat(payload["timestamp"]),
                )
                memories.append(memory)

            # Sort by created_at
            memories.sort(key=lambda m: m.created_at, reverse=True)

            logger.debug(f"Retrieved {len(memories)} memories")
            return memories

        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            raise QueryError(f"Failed to retrieve memories: {e}")

    async def search_memories(
        self, query_vector: list[float], limit: int = 10, min_importance: float = 0.0
    ) -> list[tuple[MemoryEntry, float]]:
        """Search for semantically similar memories."""
        self._ensure_connected()

        if len(query_vector) != self.config.vector_size:
            raise ValueError(
                f"Query vector size {len(query_vector)} doesn't match "
                f"configured size {self.config.vector_size}"
            )

        try:
            # Build filter
            query_filter = Filter(
                must=[
                    FieldCondition(key="type", match=MatchValue(value="memory")),
                    FieldCondition(key="importance", range=Range(gte=min_importance)),
                ]
            )

            # Search
            results = await self._client.search(
                collection_name=self.config.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
            )

            matches = []
            for scored_point in results:
                payload = scored_point.payload
                memory = MemoryEntry(
                    content=payload["content"],
                    memory_type=MemoryType(payload.get("memory_type", "fact")),
                    user_id=payload.get("user_id", "default"),
                    created_at=datetime.fromisoformat(payload["timestamp"]),
                )
                matches.append((memory, scored_point.score))

            logger.debug(f"Found {len(matches)} similar memories")
            return matches

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            raise QueryError(f"Memory search failed: {e}")

    async def delete_session(self, session_id: str) -> bool:
        """Delete all messages in a session."""
        self._ensure_connected()

        try:
            # Build filter
            query_filter = Filter(
                must=[
                    FieldCondition(key="session_id", match=MatchValue(value=session_id)),
                    FieldCondition(key="type", match=MatchValue(value="message")),
                ]
            )

            # Delete points
            await self._client.delete(
                collection_name=self.config.collection_name, points_selector=query_filter
            )

            logger.info(f"Deleted session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            raise MemoryError(f"Failed to delete session: {e}")

    async def clear_all(self) -> None:
        """Clear all data from the collection."""
        self._ensure_connected()

        try:
            # Delete all points
            await self._client.delete(
                collection_name=self.config.collection_name,
                points_selector=Filter(must=[]),  # Empty filter matches all
            )

            logger.info("Qdrant collection cleared")

        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise MemoryError(f"Failed to clear collection: {e}")

    def _ensure_connected(self) -> None:
        """Ensure connection is established."""
        if not self._is_connected or not self._client:
            raise ConnectionError("Qdrant not connected. Call initialize() first.")

    # MemoryInterface abstract methods (not fully implemented for vector backend)
    async def create_session(self, session_id: str, user_id: str) -> None:
        """Create session (no-op for vector backend)."""
        pass

    async def end_session(self, session_id: str) -> None:
        """End session (no-op for vector backend)."""
        pass

    async def get_session(self, session_id: str) -> dict[str, Any]:
        """Get session info."""
        return {"session_id": session_id, "backend": "qdrant"}

    async def get_context(self, session_id: str, limit: int = 10) -> list[Message]:
        """Get conversation context (alias for retrieve_messages)."""
        return await self.retrieve_messages(session_id, limit=limit)

    async def search_messages(
        self, query_vector: list[float], session_id: str | None = None, limit: int = 10
    ) -> list[Message]:
        """Search messages (returns only messages from search_similar)."""
        results = await self.search_similar(query_vector, limit=limit, session_id=session_id)
        return [msg for msg, score in results]

    async def get_statistics(self) -> dict[str, Any]:
        """Get backend statistics."""
        try:
            collection_info = await self._client.get_collection(self.config.collection_name)
            return {
                "backend": "qdrant",
                "collection": self.config.collection_name,
                "total_entries": collection_info.points_count,
                "vector_size": self.config.vector_size,
                "connected": self._is_connected,
            }
        except Exception:
            return {"backend": "qdrant", "connected": self._is_connected}

    async def clear_history(self, session_id: str) -> None:
        """Clear session history (alias for delete_session)."""
        await self.delete_session(session_id)

    async def delete_memory(self, memory_id: str) -> None:
        """Delete a specific memory."""
        try:
            from qdrant_client.models import PointIdsList

            await self._client.delete(
                collection_name=self.config.collection_name,
                points_selector=PointIdsList(points=[memory_id]),
            )
            logger.debug(f"Deleted memory {memory_id}")
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            raise MemoryError(f"Failed to delete memory: {e}")
