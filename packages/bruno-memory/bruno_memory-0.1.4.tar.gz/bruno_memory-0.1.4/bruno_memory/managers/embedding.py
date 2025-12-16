"""
Embedding management for bruno-memory.

Handles embedding generation, caching, and retrieval for semantic search.
Integrates with bruno-llm for flexible embedding provider support.
"""

import hashlib
from datetime import datetime, timedelta
from typing import Any

from bruno_llm.base import BaseEmbeddingProvider

from ..base import BaseMemoryBackend
from ..exceptions import EmbeddingError


class EmbeddingManager:
    """
    Manager for embedding generation and caching.

    Features:
    - Automatic embedding generation for messages and memories
    - Embedding caching to avoid redundant API calls
    - Batch embedding for efficiency
    - Multiple embedding provider support via bruno-llm
    """

    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,
        backend: BaseMemoryBackend | None = None,
        cache_ttl: int = 86400,  # 24 hours
        batch_size: int = 32,
    ):
        """Initialize embedding manager.

        Args:
            embedding_provider: Embedding provider from bruno-llm
            backend: Optional backend for embedding storage
            cache_ttl: Cache TTL in seconds
            batch_size: Batch size for embedding generation
        """
        self.embedding_provider = embedding_provider
        self.backend = backend
        self.cache_ttl = cache_ttl
        self.batch_size = batch_size
        self._cache: dict[str, tuple[list[float], datetime]] = {}

    def _get_cache_key(self, text: str, model: str | None = None) -> str:
        """Generate cache key for text.

        Args:
            text: Text to embed
            model: Optional model name

        Returns:
            str: Cache key
        """
        content = f"{model or 'default'}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def embed_text(
        self,
        text: str,
        use_cache: bool = True,
    ) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed
            use_cache: Whether to use cache

        Returns:
            List[float]: Embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not text or len(text.strip()) == 0:
            raise EmbeddingError("Cannot embed empty text")

        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                embedding, cached_at = self._cache[cache_key]
                if datetime.now() - cached_at < timedelta(seconds=self.cache_ttl):
                    return embedding
                else:
                    # Expired, remove from cache
                    del self._cache[cache_key]

        try:
            # Generate embedding
            embedding = await self.embedding_provider.embed_text(text)

            # Cache result
            if use_cache:
                cache_key = self._get_cache_key(text)
                self._cache[cache_key] = (embedding, datetime.now())

            return embedding

        except Exception as e:
            raise EmbeddingError(f"Failed to generate embedding: {e}") from e

    async def embed_batch(
        self,
        texts: list[str],
        use_cache: bool = True,
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            use_cache: Whether to use cache

        Returns:
            List[List[float]]: List of embedding vectors

        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not texts:
            return []

        embeddings = []
        texts_to_embed = []
        text_indices = []

        # Check cache for each text
        for idx, text in enumerate(texts):
            if not text or len(text.strip()) == 0:
                embeddings.append([])
                continue

            if use_cache:
                cache_key = self._get_cache_key(text)
                if cache_key in self._cache:
                    embedding, cached_at = self._cache[cache_key]
                    if datetime.now() - cached_at < timedelta(seconds=self.cache_ttl):
                        embeddings.append(embedding)
                        continue
                    else:
                        del self._cache[cache_key]

            # Need to generate embedding
            texts_to_embed.append(text)
            text_indices.append(idx)
            embeddings.append(None)  # Placeholder

        # Generate embeddings for uncached texts
        if texts_to_embed:
            try:
                # Process in batches
                batch_embeddings = []
                for i in range(0, len(texts_to_embed), self.batch_size):
                    batch = texts_to_embed[i : i + self.batch_size]
                    batch_result = await self.embedding_provider.embed_batch(batch)
                    batch_embeddings.extend(batch_result)

                # Insert embeddings at correct indices and cache
                for idx, embedding in zip(text_indices, batch_embeddings):
                    embeddings[idx] = embedding

                    if use_cache:
                        cache_key = self._get_cache_key(texts[idx])
                        self._cache[cache_key] = (embedding, datetime.now())

            except Exception as e:
                raise EmbeddingError(f"Failed to generate batch embeddings: {e}") from e

        return embeddings

    async def embed_message(
        self,
        message_content: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[float]:
        """Generate embedding for a message.

        Args:
            message_content: Message content
            metadata: Optional metadata to include

        Returns:
            List[float]: Embedding vector
        """
        # Optionally include metadata in embedding
        text = message_content
        if metadata and metadata.get("include_in_embedding"):
            # Add relevant metadata to text
            if "context" in metadata:
                text = f"{metadata['context']}\n{text}"

        return await self.embed_text(text)

    async def embed_memory(
        self,
        memory_content: str,
        memory_type: str,
    ) -> list[float]:
        """Generate embedding for a memory entry.

        Args:
            memory_content: Memory content
            memory_type: Type of memory

        Returns:
            List[float]: Embedding vector
        """
        # Prefix with memory type for better semantic grouping
        text = f"[{memory_type}] {memory_content}"
        return await self.embed_text(text)

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict[str, Any]: Cache statistics
        """
        now = datetime.now()
        expired = sum(
            1
            for _, (_, cached_at) in self._cache.items()
            if now - cached_at >= timedelta(seconds=self.cache_ttl)
        )

        return {
            "total_cached": len(self._cache),
            "expired": expired,
            "active": len(self._cache) - expired,
            "cache_ttl_seconds": self.cache_ttl,
        }

    async def find_similar(
        self,
        query_text: str,
        candidates: list[tuple[str, Any]],
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> list[tuple[Any, float]]:
        """Find similar texts using embeddings.

        Args:
            query_text: Query text
            candidates: List of (text, metadata) tuples
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score

        Returns:
            List[Tuple[Any, float]]: List of (metadata, similarity) tuples
        """
        if not candidates:
            return []

        try:
            # Generate query embedding
            query_embedding = await self.embed_text(query_text)

            # Generate candidate embeddings
            candidate_texts = [text for text, _ in candidates]
            candidate_embeddings = await self.embed_batch(candidate_texts)

            # Calculate similarities
            similarities = []
            for idx, embedding in enumerate(candidate_embeddings):
                if embedding:  # Skip empty embeddings
                    similarity = self._cosine_similarity(query_embedding, embedding)
                    if similarity >= similarity_threshold:
                        _, metadata = candidates[idx]
                        similarities.append((metadata, similarity))

            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]

        except Exception as e:
            raise EmbeddingError(f"Failed to find similar texts: {e}") from e

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            float: Cosine similarity (0-1)
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


class EmbeddingCache:
    """
    Persistent embedding cache using backend storage.

    Stores embeddings in the backend to avoid regeneration across sessions.
    """

    def __init__(self, backend: BaseMemoryBackend, ttl_seconds: int = 604800):
        """Initialize embedding cache.

        Args:
            backend: Backend for storage
            ttl_seconds: TTL in seconds (default 7 days)
        """
        self.backend = backend
        self.ttl_seconds = ttl_seconds

    async def get(self, key: str) -> list[float] | None:
        """Get embedding from cache.

        Args:
            key: Cache key

        Returns:
            Optional[List[float]]: Embedding vector if found
        """
        # Implementation would use backend to retrieve cached embedding
        # This is a placeholder for the actual implementation
        pass

    async def set(self, key: str, embedding: list[float]) -> None:
        """Store embedding in cache.

        Args:
            key: Cache key
            embedding: Embedding vector
        """
        # Implementation would use backend to store embedding
        # This is a placeholder for the actual implementation
        pass

    async def delete(self, key: str) -> None:
        """Delete embedding from cache.

        Args:
            key: Cache key
        """
        # Implementation would use backend to delete embedding
        pass

    async def clear_expired(self) -> int:
        """Clear expired embeddings.

        Returns:
            int: Number of embeddings cleared
        """
        # Implementation would use backend to clear expired entries
        return 0
