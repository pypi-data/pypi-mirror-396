"""
ChromaDB backend implementation for bruno-memory.

Provides vector storage and semantic search using ChromaDB.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import chromadb
from bruno_core.models import MemoryEntry, MemoryType, Message
from chromadb.config import Settings

from bruno_memory.base.base_backend import BaseMemoryBackend
from bruno_memory.base.config import ChromaDBConfig
from bruno_memory.exceptions import (
    ConfigurationError,
    ConnectionError,
    MemoryError,
    QueryError,
)

logger = logging.getLogger(__name__)


class ChromaDBBackend(BaseMemoryBackend):
    """
    ChromaDB backend for bruno-memory with vector search capabilities.

    Features:
    - Persistent vector storage
    - Semantic search via embeddings
    - Metadata filtering
    - Multiple distance metrics
    - Automatic embedding generation
    """

    def __init__(self, config: ChromaDBConfig):
        """Initialize ChromaDB backend."""
        super().__init__(config)
        self.config: ChromaDBConfig = config
        self._client: chromadb.Client | None = None
        self._collection = None
        self._executor = None  # For async operations

    async def initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            # Create executor for blocking operations
            from concurrent.futures import ThreadPoolExecutor

            self._executor = ThreadPoolExecutor(max_workers=4)

            # Initialize ChromaDB client
            settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )

            if self.config.persist_directory:
                persist_path = Path(self.config.persist_directory)
                persist_path.mkdir(parents=True, exist_ok=True)
                settings.persist_directory = str(persist_path)
                self._client = chromadb.PersistentClient(path=str(persist_path), settings=settings)
                logger.info(f"ChromaDB initialized with persistence at {persist_path}")
            else:
                self._client = chromadb.Client(settings=settings)
                logger.info("ChromaDB initialized in-memory")

            # Get or create collection
            await self._get_or_create_collection()

            self._is_connected = True
            logger.info(f"ChromaDB backend initialized: {self.config.collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise ConnectionError(f"ChromaDB initialization failed: {e}")

    async def _get_or_create_collection(self):
        """Get or create ChromaDB collection."""
        try:
            # Map distance function to ChromaDB format
            distance_map = {"cosine": "cosine", "euclidean": "l2", "manhattan": "l1"}
            distance = distance_map.get(self.config.distance_function, "cosine")

            # Run in executor since chromadb is synchronous
            loop = asyncio.get_event_loop()
            self._collection = await loop.run_in_executor(
                self._executor,
                lambda: self._client.get_or_create_collection(
                    name=self.config.collection_name, metadata={"hnsw:space": distance}
                ),
            )

            logger.info(f"Collection '{self.config.collection_name}' ready")

        except Exception as e:
            raise ConfigurationError(f"Failed to create collection: {e}")

    async def close(self) -> None:
        """Close ChromaDB connection."""
        try:
            if self._executor:
                self._executor.shutdown(wait=True)
                self._executor = None

            self._client = None
            self._collection = None
            self._is_connected = False
            logger.info("ChromaDB connection closed")

        except Exception as e:
            logger.error(f"Error closing ChromaDB: {e}")

    # Abstract method implementations from BaseMemoryBackend
    async def connect(self) -> None:
        """Connect to ChromaDB (alias for initialize)."""
        await self.initialize()

    async def disconnect(self) -> None:
        """Disconnect from ChromaDB (alias for close)."""
        await self.close()

    async def health_check(self) -> bool:
        """Check if ChromaDB is healthy."""
        try:
            return self._is_connected and self._client is not None and self._collection is not None
        except Exception:
            return False

    async def store_message(
        self, session_id: str, message: Message, metadata: dict[str, Any] | None = None
    ) -> str:
        """Store a message with vector embedding."""
        self._ensure_connected()

        try:
            # Generate unique ID
            message_id = f"{session_id}_{message.timestamp.isoformat()}_{message.role}"

            # Prepare metadata
            meta = {
                "session_id": session_id,
                "role": message.role,
                "timestamp": message.timestamp.isoformat(),
                "type": "message",
            }

            if metadata:
                meta.update(metadata)

            # Add message to collection
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self._collection.add(
                    ids=[message_id], documents=[message.content], metadatas=[meta]
                ),
            )

            logger.debug(f"Stored message {message_id} in ChromaDB")
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
            # Query collection with session filter
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self._executor,
                lambda: self._collection.get(
                    where={"session_id": session_id, "type": "message"},
                    limit=limit if limit > 0 else None,
                    offset=offset,
                ),
            )

            messages = []
            if results and results["documents"]:
                for doc, meta in zip(results["documents"], results["metadatas"]):
                    message = Message(
                        role=meta["role"],
                        content=doc,
                        timestamp=datetime.fromisoformat(meta["timestamp"]),
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
        self, query: str, limit: int = 10, session_id: str | None = None, min_score: float = 0.0
    ) -> list[tuple[Message, float]]:
        """
        Search for semantically similar messages.

        Args:
            query: Search query text
            limit: Maximum results
            session_id: Optional session filter
            min_score: Minimum similarity score (0-1)

        Returns:
            List of (message, score) tuples
        """
        self._ensure_connected()

        try:
            # Build filter
            where_filter = {"type": "message"}
            if session_id:
                where_filter["session_id"] = session_id

            # Query collection
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self._executor,
                lambda: self._collection.query(
                    query_texts=[query], n_results=limit, where=where_filter
                ),
            )

            matches = []
            if results and results["documents"] and results["documents"][0]:
                for doc, meta, distance in zip(
                    results["documents"][0], results["metadatas"][0], results["distances"][0]
                ):
                    # Convert distance to similarity score (0-1)
                    # For cosine distance: similarity = 1 - distance
                    score = 1.0 - distance

                    if score >= min_score:
                        message = Message(
                            role=meta["role"],
                            content=doc,
                            timestamp=datetime.fromisoformat(meta["timestamp"]),
                        )
                        matches.append((message, score))

            logger.debug(f"Found {len(matches)} similar messages")
            return matches

        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise QueryError(f"Similarity search failed: {e}")

    async def store_memory(
        self, memory: MemoryEntry, metadata: dict[str, Any] | None = None
    ) -> str:
        """Store a memory entry with vector embedding."""
        self._ensure_connected()

        try:
            # Generate unique ID
            memory_id = f"memory_{memory.created_at.isoformat()}_{hash(memory.content)}"

            # Prepare metadata
            meta = {
                "type": "memory",
                "timestamp": memory.created_at.isoformat(),
                "memory_type": memory.memory_type.value,
                "user_id": memory.user_id,
            }

            if memory.metadata:
                if memory.metadata.tags:
                    meta["tags"] = ",".join(memory.metadata.tags)
                meta["importance"] = memory.metadata.importance
                if memory.metadata.source:
                    meta["source"] = memory.metadata.source

            if metadata:
                meta.update(metadata)

            # Add memory to collection
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self._collection.add(
                    ids=[memory_id], documents=[memory.content], metadatas=[meta]
                ),
            )

            logger.debug(f"Stored memory {memory_id} in ChromaDB")
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
            where_filter = {"type": "memory"}

            # Query collection
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self._executor,
                lambda: self._collection.get(
                    where=where_filter, limit=limit if limit > 0 else None
                ),
            )

            memories = []
            if results and results["documents"]:
                for doc, meta in zip(results["documents"], results["metadatas"]):
                    # Filter by importance
                    if meta.get("importance", 0.0) < min_importance:
                        continue

                    # Filter by tags
                    if tags:
                        memory_tags = set(meta.get("tags", "").split(","))
                        if not tags.intersection(memory_tags):
                            continue

                    memory = MemoryEntry(
                        content=doc,
                        memory_type=MemoryType(meta.get("memory_type", "fact")),
                        user_id=meta.get("user_id", "default"),
                        created_at=datetime.fromisoformat(meta["timestamp"]),
                    )
                    memories.append(memory)

            # Sort by importance and created_at
            memories.sort(key=lambda m: (m.metadata.importance, m.created_at), reverse=True)

            logger.debug(f"Retrieved {len(memories)} memories")
            return memories[:limit]

        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            raise QueryError(f"Failed to retrieve memories: {e}")

    async def search_memories(
        self, query: str, limit: int = 10, min_importance: float = 0.0
    ) -> list[tuple[MemoryEntry, float]]:
        """Search for semantically similar memories."""
        self._ensure_connected()

        try:
            # Query collection
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self._executor,
                lambda: self._collection.query(
                    query_texts=[query], n_results=limit, where={"type": "memory"}
                ),
            )

            matches = []
            if results and results["documents"] and results["documents"][0]:
                for doc, meta, distance in zip(
                    results["documents"][0], results["metadatas"][0], results["distances"][0]
                ):
                    # Filter by importance
                    if meta.get("importance", 0.0) < min_importance:
                        continue

                    # Convert distance to similarity score
                    score = 1.0 - distance

                    memory = MemoryEntry(
                        content=doc,
                        memory_type=MemoryType(meta.get("memory_type", "fact")),
                        user_id=meta.get("user_id", "default"),
                        created_at=datetime.fromisoformat(meta["timestamp"]),
                    )
                    matches.append((memory, score))

            logger.debug(f"Found {len(matches)} similar memories")
            return matches

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            raise QueryError(f"Memory search failed: {e}")

    async def delete_session(self, session_id: str) -> bool:
        """Delete all messages in a session."""
        self._ensure_connected()

        try:
            # Get all message IDs for the session
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self._executor,
                lambda: self._collection.get(where={"session_id": session_id, "type": "message"}),
            )

            if results and results["ids"]:
                # Delete all messages
                await loop.run_in_executor(
                    self._executor, lambda: self._collection.delete(ids=results["ids"])
                )
                logger.info(f"Deleted session {session_id} ({len(results['ids'])} messages)")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            raise MemoryError(f"Failed to delete session: {e}")

    async def clear_all(self) -> None:
        """Clear all data from the collection."""
        self._ensure_connected()

        try:
            # Delete and recreate collection
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor, lambda: self._client.delete_collection(self.config.collection_name)
            )

            # Recreate collection
            await self._get_or_create_collection()

            logger.info("ChromaDB collection cleared")

        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise MemoryError(f"Failed to clear collection: {e}")

    def _ensure_connected(self) -> None:
        """Ensure connection is established."""
        if not self._is_connected or not self._client or not self._collection:
            raise ConnectionError("ChromaDB not connected. Call initialize() first.")

    # MemoryInterface abstract methods (not fully implemented for vector backend)
    async def create_session(self, session_id: str, user_id: str) -> None:
        """Create session (no-op for vector backend)."""
        pass

    async def end_session(self, session_id: str) -> None:
        """End session (no-op for vector backend)."""
        pass

    async def get_session(self, session_id: str) -> dict[str, Any]:
        """Get session info."""
        return {"session_id": session_id, "backend": "chromadb"}

    async def get_context(self, session_id: str, limit: int = 10) -> list[Message]:
        """Get conversation context (alias for retrieve_messages)."""
        return await self.retrieve_messages(session_id, limit=limit)

    async def search_messages(
        self, query: str, session_id: str | None = None, limit: int = 10
    ) -> list[Message]:
        """Search messages (returns only messages from search_similar)."""
        results = await self.search_similar(query, limit=limit, session_id=session_id)
        return [msg for msg, score in results]

    async def get_statistics(self) -> dict[str, Any]:
        """Get backend statistics."""
        try:
            loop = asyncio.get_event_loop()
            count_result = await loop.run_in_executor(
                self._executor, lambda: self._collection.count()
            )
            return {
                "backend": "chromadb",
                "collection": self.config.collection_name,
                "total_entries": count_result,
                "connected": self._is_connected,
            }
        except Exception:
            return {"backend": "chromadb", "connected": self._is_connected}

    async def clear_history(self, session_id: str) -> None:
        """Clear session history (alias for delete_session)."""
        await self.delete_session(session_id)

    async def delete_memory(self, memory_id: str) -> None:
        """Delete a specific memory."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor, lambda: self._collection.delete(ids=[memory_id])
            )
            logger.debug(f"Deleted memory {memory_id}")
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            raise MemoryError(f"Failed to delete memory: {e}")
