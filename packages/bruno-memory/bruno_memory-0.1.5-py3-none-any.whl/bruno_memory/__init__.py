"""
bruno-memory: Advanced memory management for bruno-ai

A high-performance, multi-backend memory system providing persistent storage
and intelligent retrieval for AI conversations and context management.
"""

import importlib.metadata
from typing import Optional

# Import backends to trigger auto-registration
from . import backends
from .base import (
    CONFIG_CLASSES,
    BaseMemoryBackend,
    ChromaDBConfig,
    MemoryConfig,
    PostgreSQLConfig,
    QdrantConfig,
    RedisConfig,
    SQLiteConfig,
)
from .exceptions import (
    BackendNotFoundError,
    ConfigurationError,
    ConnectionError,
    DuplicateError,
    IntegrationError,
    MemoryError,
    NotFoundError,
    PermissionError,
    QueryError,
    SerializationError,
    StorageError,
    ValidationError,
)
from .factory import (
    MemoryBackendFactory,
    create_backend,
    create_config,
    create_from_env,
    create_with_fallback,
    factory,
    list_backends,
    register_backend,
)

# Import managers
from .managers import ContextBuilder, ConversationManager, MemoryRetriever

# Version handling with fallback
try:
    __version__ = importlib.metadata.version("bruno-memory")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0"  # Fallback version

__all__ = [
    # Core classes
    "BaseMemoryBackend",
    "MemoryBackendFactory",
    "factory",
    # Configuration classes
    "MemoryConfig",
    "SQLiteConfig",
    "PostgreSQLConfig",
    "RedisConfig",
    "ChromaDBConfig",
    "QdrantConfig",
    "CONFIG_CLASSES",
    # Factory functions
    "create_backend",
    "create_config",
    "list_backends",
    "register_backend",
    # Manager classes
    "ConversationManager",
    "ContextBuilder",
    "MemoryRetriever",
    # Exception classes
    "MemoryError",
    "ConnectionError",
    "ConfigurationError",
    "ValidationError",
    "NotFoundError",
    "DuplicateError",
    "PermissionError",
    "StorageError",
    "QueryError",
    "SerializationError",
    "BackendNotFoundError",
    "IntegrationError",
    # Version
    "__version__",
]
