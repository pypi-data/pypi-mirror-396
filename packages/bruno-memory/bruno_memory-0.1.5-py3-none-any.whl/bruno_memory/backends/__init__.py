"""
Memory backend implementations for bruno-memory.

Provides concrete implementations of the BaseMemoryBackend
for different storage systems.
"""

from ..base import ChromaDBConfig, PostgreSQLConfig, QdrantConfig, RedisConfig, SQLiteConfig

# Import and register backends with factory
from ..factory import register_backend
from .postgresql import PostgreSQLMemoryBackend
from .redis import RedisMemoryBackend
from .sqlite import SQLiteMemoryBackend
from .vector import ChromaDBBackend, QdrantBackend

# Auto-register backends
register_backend("sqlite", SQLiteMemoryBackend, SQLiteConfig)
register_backend("postgresql", PostgreSQLMemoryBackend, PostgreSQLConfig)
register_backend("redis", RedisMemoryBackend, RedisConfig)
register_backend("chromadb", ChromaDBBackend, ChromaDBConfig)
register_backend("qdrant", QdrantBackend, QdrantConfig)

__all__ = [
    "SQLiteMemoryBackend",
    "PostgreSQLMemoryBackend",
    "RedisMemoryBackend",
    "ChromaDBBackend",
    "QdrantBackend",
]
