"""
Memory Retriever for bruno-memory.

Provides advanced memory retrieval with multiple search strategies including
exact match, full-text search, semantic similarity, and hybrid approaches.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from bruno_core.models import MemoryEntry, MemoryQuery, MemoryType, Message

from ..base import BaseMemoryBackend
from ..exceptions import QueryError, ValidationError


class SearchStrategy(str, Enum):
    """Memory search strategies."""

    EXACT = "exact"
    FULL_TEXT = "full_text"
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"
    HYBRID = "hybrid"


class MemoryRetriever:
    """
    Advanced memory retrieval with multiple search strategies.

    Provides:
    - Exact match search
    - Full-text search with ranking
    - Semantic similarity search (when embeddings available)
    - Temporal range queries
    - Hybrid retrieval combining multiple strategies
    - Result ranking and filtering
    - Query caching for performance
    """

    def __init__(
        self,
        backend: BaseMemoryBackend,
        default_strategy: SearchStrategy = SearchStrategy.HYBRID,
        cache_enabled: bool = True,
        cache_ttl_seconds: int = 300,
    ):
        """Initialize memory retriever.

        Args:
            backend: Memory backend for storage operations
            default_strategy: Default search strategy
            cache_enabled: Enable query caching
            cache_ttl_seconds: Cache TTL in seconds
        """
        self.backend = backend
        self.default_strategy = default_strategy
        self.cache_enabled = cache_enabled
        self.cache_ttl_seconds = cache_ttl_seconds

        # Simple cache: query -> (results, timestamp)
        self._cache: dict[str, tuple[list[MemoryEntry], datetime]] = {}

    async def search_messages(
        self,
        query: str,
        conversation_id: str | None = None,
        user_id: str | None = None,
        limit: int = 10,
        strategy: SearchStrategy | None = None,
    ) -> list[Message]:
        """Search messages with specified strategy.

        Args:
            query: Search query text
            conversation_id: Optional conversation filter
            user_id: Optional user filter
            limit: Maximum results to return
            strategy: Search strategy to use

        Returns:
            List[Message]: Matching messages
        """
        if not query:
            raise ValidationError("Query cannot be empty")

        strategy = strategy or self.default_strategy

        try:
            if strategy == SearchStrategy.EXACT:
                return await self._exact_search_messages(query, conversation_id, limit)
            elif strategy == SearchStrategy.FULL_TEXT:
                return await self._fulltext_search_messages(query, conversation_id, limit)
            elif strategy == SearchStrategy.TEMPORAL:
                # Temporal search needs additional parameters
                return await self._temporal_search_messages(conversation_id, limit)
            else:  # HYBRID or default
                return await self._hybrid_search_messages(query, conversation_id, limit)
        except Exception as e:
            raise QueryError(f"Message search failed: {e}")

    async def search_memories(
        self, query: MemoryQuery, strategy: SearchStrategy | None = None, use_cache: bool = True
    ) -> list[MemoryEntry]:
        """Search memory entries with advanced filtering.

        Args:
            query: Memory query with filters
            strategy: Search strategy to use
            use_cache: Use cached results if available

        Returns:
            List[MemoryEntry]: Matching memory entries
        """
        if not query.user_id:
            raise ValidationError("user_id is required in MemoryQuery")

        # Check cache
        cache_key = self._build_cache_key(query, strategy)
        if use_cache and self.cache_enabled:
            cached = self._get_cached_results(cache_key)
            if cached:
                return cached

        try:
            strategy = strategy or self.default_strategy

            if strategy == SearchStrategy.EXACT:
                results = await self._exact_search_memories(query)
            elif strategy == SearchStrategy.TEMPORAL:
                results = await self._temporal_search_memories(query)
            elif strategy == SearchStrategy.SEMANTIC:
                results = await self._semantic_search_memories(query)
            else:  # HYBRID
                results = await self._hybrid_search_memories(query)

            # Apply post-filtering
            results = self._apply_filters(results, query)

            # Rank results
            results = self._rank_results(results, query)

            # Cache results
            if self.cache_enabled:
                self._cache_results(cache_key, results)

            return results
        except Exception as e:
            raise QueryError(f"Memory search failed: {e}")

    async def find_similar_memories(
        self,
        reference_memory: MemoryEntry,
        user_id: str,
        limit: int = 5,
        min_similarity: float = 0.7,
    ) -> list[MemoryEntry]:
        """Find memories similar to a reference memory.

        Args:
            reference_memory: Reference memory to find similar to
            user_id: User ID to search within
            limit: Maximum number of similar memories
            min_similarity: Minimum similarity threshold

        Returns:
            List[MemoryEntry]: Similar memory entries
        """
        # For now, use content-based similarity
        # In future, use embedding-based similarity
        query = MemoryQuery(user_id=user_id, query_text=reference_memory.content, limit=limit)

        results = await self.search_memories(query, strategy=SearchStrategy.HYBRID)

        # Filter out the reference memory itself
        results = [m for m in results if str(m.id) != str(reference_memory.id)]

        return results[:limit]

    async def get_recent_memories(
        self,
        user_id: str,
        hours: int = 24,
        memory_types: list[MemoryType] | None = None,
        limit: int = 50,
    ) -> list[MemoryEntry]:
        """Get recent memories within time window.

        Args:
            user_id: User ID
            hours: Number of hours to look back
            memory_types: Optional filter by memory types
            limit: Maximum results

        Returns:
            List[MemoryEntry]: Recent memory entries
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        query = MemoryQuery(user_id=user_id, memory_types=memory_types, limit=limit)

        memories = await self.backend.retrieve_memories(user_id, limit=limit)

        # Filter by time
        recent = [m for m in memories if m.created_at >= cutoff_time]

        # Sort by recency
        recent.sort(key=lambda m: m.created_at, reverse=True)

        return recent[:limit]

    async def get_important_memories(
        self, user_id: str, min_importance: float = 0.7, limit: int = 20
    ) -> list[MemoryEntry]:
        """Get high-importance memories.

        Args:
            user_id: User ID
            min_importance: Minimum importance threshold
            limit: Maximum results

        Returns:
            List[MemoryEntry]: Important memory entries
        """
        query = MemoryQuery(user_id=user_id, min_importance=min_importance, limit=limit)

        try:
            memories = await self.backend.search_memories(query)

            # Sort by importance
            memories.sort(key=lambda m: m.metadata.importance, reverse=True)

            return memories[:limit]
        except Exception as e:
            raise QueryError(f"Failed to get important memories: {e}")

    def clear_cache(self) -> None:
        """Clear the query cache."""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache stats
        """
        # Remove expired entries
        self._cleanup_cache()

        return {
            "cached_queries": len(self._cache),
            "cache_enabled": self.cache_enabled,
            "cache_ttl_seconds": self.cache_ttl_seconds,
        }

    # Private helper methods

    async def _exact_search_messages(
        self, query: str, conversation_id: str | None, limit: int
    ) -> list[Message]:
        """Exact string match search."""
        results = await self.backend.search_messages(
            query, conversation_id=conversation_id, limit=limit
        )

        # Filter for exact matches
        exact_matches = [m for m in results if query.lower() in m.content.lower()]

        return exact_matches[:limit]

    async def _fulltext_search_messages(
        self, query: str, conversation_id: str | None, limit: int
    ) -> list[Message]:
        """Full-text search with ranking."""
        results = await self.backend.search_messages(
            query, conversation_id=conversation_id, limit=limit * 2  # Get more for ranking
        )

        # Rank by relevance (simple word matching)
        scored = []
        query_words = set(query.lower().split())

        for msg in results:
            content_words = set(msg.content.lower().split())
            overlap = len(query_words & content_words)
            scored.append((overlap, msg))

        # Sort by score
        scored.sort(key=lambda x: x[0], reverse=True)

        return [msg for _, msg in scored[:limit]]

    async def _temporal_search_messages(
        self, conversation_id: str | None, limit: int
    ) -> list[Message]:
        """Temporal search - most recent messages."""
        messages = await self.backend.retrieve_messages(
            conversation_id=conversation_id or "", limit=limit
        )

        # Sort by timestamp (most recent first)
        messages.sort(key=lambda m: m.timestamp, reverse=True)

        return messages[:limit]

    async def _hybrid_search_messages(
        self, query: str, conversation_id: str | None, limit: int
    ) -> list[Message]:
        """Hybrid search combining strategies."""
        # Get results from different strategies
        fulltext_results = await self._fulltext_search_messages(query, conversation_id, limit)

        temporal_results = await self._temporal_search_messages(conversation_id, limit // 2)

        # Combine and deduplicate
        seen_ids = set()
        combined = []

        for msg in fulltext_results + temporal_results:
            if str(msg.id) not in seen_ids:
                combined.append(msg)
                seen_ids.add(str(msg.id))

        return combined[:limit]

    async def _exact_search_memories(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Exact search in memory content."""
        memories = await self.backend.search_memories(query)

        if query.query_text:
            memories = [m for m in memories if query.query_text.lower() in m.content.lower()]

        return memories

    async def _temporal_search_memories(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Temporal search - recent memories."""
        memories = await self.backend.search_memories(query)

        # Sort by recency
        memories.sort(key=lambda m: m.updated_at, reverse=True)

        return memories

    async def _semantic_search_memories(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Semantic search using embeddings (if available)."""
        # For now, fall back to full-text search
        # In future, use embedding-based similarity
        return await self.backend.search_memories(query)

    async def _hybrid_search_memories(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Hybrid memory search combining strategies."""
        # Get results from backend
        memories = await self.backend.search_memories(query)

        # Apply multiple ranking factors
        scored = []
        for memory in memories:
            score = self._calculate_memory_score(memory, query)
            scored.append((score, memory))

        # Sort by score
        scored.sort(key=lambda x: x[0], reverse=True)

        return [m for _, m in scored]

    def _calculate_memory_score(self, memory: MemoryEntry, query: MemoryQuery) -> float:
        """Calculate relevance score for a memory."""
        score = 0.0

        # Importance score
        score += memory.metadata.importance * 10

        # Recency score
        age_hours = (datetime.now() - memory.updated_at).total_seconds() / 3600
        if age_hours < 24:
            score += 5.0
        elif age_hours < 168:  # 1 week
            score += 2.0

        # Query text matching
        if query.query_text:
            query_words = set(query.query_text.lower().split())
            content_words = set(memory.content.lower().split())
            overlap = len(query_words & content_words)
            score += overlap * 2.0

        # Access count (popular memories)
        score += min(memory.metadata.access_count * 0.5, 5.0)

        return score

    def _apply_filters(self, memories: list[MemoryEntry], query: MemoryQuery) -> list[MemoryEntry]:
        """Apply post-retrieval filters."""
        filtered = memories

        # Filter by memory type
        if query.memory_types:
            filtered = [m for m in filtered if m.memory_type in query.memory_types]

        # Filter by importance
        if query.min_importance is not None:
            filtered = [m for m in filtered if m.metadata.importance >= query.min_importance]

        # Filter by conversation
        if query.conversation_id:
            filtered = [m for m in filtered if m.conversation_id == query.conversation_id]

        return filtered

    def _rank_results(self, memories: list[MemoryEntry], query: MemoryQuery) -> list[MemoryEntry]:
        """Rank memory results."""
        # Already scored in hybrid search
        return memories

    def _build_cache_key(self, query: MemoryQuery, strategy: SearchStrategy | None) -> str:
        """Build cache key from query parameters."""
        parts = [
            query.user_id,
            query.query_text or "",
            str(query.memory_types) if query.memory_types else "",
            str(strategy or self.default_strategy),
            str(query.limit),
        ]
        return "|".join(parts)

    def _get_cached_results(self, cache_key: str) -> list[MemoryEntry] | None:
        """Get cached results if not expired."""
        if cache_key in self._cache:
            results, timestamp = self._cache[cache_key]
            age = (datetime.now() - timestamp).total_seconds()

            if age < self.cache_ttl_seconds:
                return results
            else:
                # Expired, remove from cache
                del self._cache[cache_key]

        return None

    def _cache_results(self, cache_key: str, results: list[MemoryEntry]) -> None:
        """Cache search results."""
        self._cache[cache_key] = (results, datetime.now())

    def _cleanup_cache(self) -> None:
        """Remove expired cache entries."""
        now = datetime.now()
        expired_keys = []

        for key, (_, timestamp) in self._cache.items():
            age = (now - timestamp).total_seconds()
            if age >= self.cache_ttl_seconds:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]
