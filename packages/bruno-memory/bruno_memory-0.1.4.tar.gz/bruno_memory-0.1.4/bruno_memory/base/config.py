"""
Configuration models for bruno-memory backends.

Uses Pydantic for validation and type safety with proper bruno-core alignment.
"""

from abc import ABC
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MemoryConfig(BaseModel, ABC):
    """Base configuration class for all memory backends."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    backend_type: str = Field(..., description="Type of the backend")
    debug: bool = Field(default=False, description="Enable debug logging")
    pool_size: int = Field(default=10, description="Connection pool size")
    timeout: int = Field(default=30, description="Operation timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")


class SQLiteConfig(MemoryConfig):
    """Configuration for SQLite backend."""

    backend_type: Literal["sqlite"] = Field(default="sqlite", description="Backend type")
    database_path: str | Path = Field(..., description="Path to SQLite database file")
    enable_fts: bool = Field(default=True, description="Enable full-text search")
    synchronous: str = Field(default="NORMAL", description="SQLite synchronous mode")
    journal_mode: str = Field(default="WAL", description="SQLite journal mode")
    cache_size: int = Field(default=2000, description="SQLite cache size in pages")
    foreign_keys: bool = Field(default=True, description="Enable foreign key constraints")
    connection_timeout: int = Field(default=30, description="Connection timeout in seconds")
    max_context_messages: int = Field(
        default=100, description="Maximum messages to include in context"
    )

    @field_validator("database_path")
    @classmethod
    def validate_database_path(cls, v):
        path = Path(v)
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    @field_validator("synchronous")
    @classmethod
    def validate_synchronous(cls, v):
        valid_modes = ["OFF", "NORMAL", "FULL", "EXTRA"]
        if v not in valid_modes:
            raise ValueError(f"synchronous must be one of {valid_modes}")
        return v

    @field_validator("journal_mode")
    @classmethod
    def validate_journal_mode(cls, v):
        valid_modes = ["DELETE", "TRUNCATE", "PERSIST", "MEMORY", "WAL", "OFF"]
        if v not in valid_modes:
            raise ValueError(f"journal_mode must be one of {valid_modes}")
        return v

    def get_connection_string(self) -> str:
        """Generate SQLite connection string."""
        return f"sqlite:///{self.database_path}"


class PostgreSQLConfig(MemoryConfig):
    """Configuration for PostgreSQL backend."""

    backend_type: Literal["postgresql"] = Field(default="postgresql", description="Backend type")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    ssl_mode: str = Field(default="prefer", description="SSL mode")
    pool_min_size: int = Field(default=1, description="Minimum pool size")
    pool_max_size: int = Field(default=20, description="Maximum pool size")

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("ssl_mode")
    @classmethod
    def validate_ssl_mode(cls, v):
        valid_modes = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
        if v not in valid_modes:
            raise ValueError(f"ssl_mode must be one of {valid_modes}")
        return v

    def get_connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return (
            f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        )


class RedisConfig(MemoryConfig):
    """Configuration for Redis backend."""

    backend_type: Literal["redis"] = Field(default="redis", description="Backend type")
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    password: str | None = Field(default=None, description="Redis password")
    database: int = Field(default=0, description="Redis database number")
    ssl: bool = Field(default=False, description="Use SSL connection")
    ttl_default: int = Field(default=86400, description="Default TTL in seconds (24 hours)")
    key_prefix: str = Field(default="bruno:memory", description="Key prefix for all Redis keys")
    max_connections: int = Field(default=50, description="Maximum number of connections in pool")
    socket_timeout: float | None = Field(default=5.0, description="Socket timeout in seconds")
    socket_connect_timeout: float | None = Field(
        default=5.0, description="Socket connect timeout in seconds"
    )
    retry_on_timeout: bool = Field(default=True, description="Retry commands on timeout")

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("database")
    @classmethod
    def validate_database(cls, v):
        if not 0 <= v <= 15:
            raise ValueError("Redis database must be between 0 and 15")
        return v

    def get_connection_string(self) -> str:
        """Generate Redis connection string."""
        scheme = "rediss" if self.ssl else "redis"
        auth = f":{self.password}@" if self.password else ""
        return f"{scheme}://{auth}{self.host}:{self.port}/{self.database}"


class ChromaDBConfig(MemoryConfig):
    """Configuration for ChromaDB backend."""

    backend_type: Literal["chromadb"] = Field(default="chromadb", description="Backend type")
    persist_directory: str | None = Field(
        default=None, description="Directory to persist ChromaDB data"
    )
    collection_name: str = Field(default="bruno_memories", description="ChromaDB collection name")
    distance_function: str = Field(default="cosine", description="Distance function for similarity")

    @field_validator("distance_function")
    @classmethod
    def validate_distance_function(cls, v):
        valid_functions = ["cosine", "euclidean", "manhattan"]
        if v not in valid_functions:
            raise ValueError(f"distance_function must be one of {valid_functions}")
        return v


class QdrantConfig(MemoryConfig):
    """Configuration for Qdrant backend."""

    backend_type: Literal["qdrant"] = Field(default="qdrant", description="Backend type")
    host: str = Field(default="localhost", description="Qdrant host")
    port: int = Field(default=6333, description="Qdrant port")
    api_key: str | None = Field(default=None, description="Qdrant API key")
    collection_name: str = Field(default="bruno_memories", description="Qdrant collection name")
    vector_size: int = Field(default=1536, description="Vector dimension size")
    distance_metric: str = Field(default="cosine", description="Distance metric for similarity")

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("distance_metric")
    @classmethod
    def validate_distance_metric(cls, v):
        valid_metrics = ["cosine", "euclidean", "dot"]
        if v not in valid_metrics:
            raise ValueError(f"distance_metric must be one of {valid_metrics}")
        return v

    def get_connection_string(self) -> str:
        """Generate Qdrant connection string."""
        return f"http://{self.host}:{self.port}"


# Configuration type mapping
CONFIG_CLASSES = {
    "sqlite": SQLiteConfig,
    "postgresql": PostgreSQLConfig,
    "redis": RedisConfig,
    "chromadb": ChromaDBConfig,
    "qdrant": QdrantConfig,
}
