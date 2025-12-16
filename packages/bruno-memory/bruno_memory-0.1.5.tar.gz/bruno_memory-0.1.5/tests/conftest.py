"""Test configuration for pytest."""

import os
import shutil
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest

from bruno_memory.backends.sqlite import SQLiteMemoryBackend
from bruno_memory.factory import MemoryBackendFactory


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create a temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"

    yield str(db_path)

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
async def sqlite_backend(temp_db_path: str) -> Generator[SQLiteMemoryBackend, None, None]:
    """Create a SQLite backend for testing."""
    from bruno_memory.base.config import SQLiteConfig

    config = SQLiteConfig(database_path=temp_db_path)
    backend = SQLiteMemoryBackend(config)

    await backend.connect()

    yield backend

    await backend.disconnect()


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    from datetime import datetime
    from uuid import uuid4

    from bruno_core.models import Message, MessageRole

    return Message(
        id=str(uuid4()),
        conversation_id=str(uuid4()),
        role=MessageRole.USER,
        content="Hello, world!",
        timestamp=datetime.now(),
        user_id=str(uuid4()),
    )


@pytest.fixture
def sample_memory_entry():
    """Create a sample memory entry for testing."""
    from datetime import datetime
    from uuid import uuid4

    from bruno_core.models import MemoryEntry, MemoryMetadata, MemoryType

    return MemoryEntry(
        id=str(uuid4()),
        content="This is a test memory",
        memory_type=MemoryType.EPISODIC,
        importance=0.8,
        timestamp=datetime.now(),
        user_id=str(uuid4()),
        conversation_id=str(uuid4()),
        metadata=MemoryMetadata(),
        tags=["test", "memory"],
    )


# ============================================================================
# Docker Backend Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def docker_services_config():
    """Configuration for Docker services."""
    return {
        "postgresql": {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "bruno_memory"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        },
        "redis": {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "db": int(os.getenv("REDIS_DB", "15")),
            "password": os.getenv("REDIS_PASSWORD", None),
        },
        "chromadb": {
            "host": os.getenv("CHROMA_HOST", "localhost"),
            "port": int(os.getenv("CHROMA_HTTP_PORT", "8000")),
        },
        "qdrant": {
            "host": os.getenv("QDRANT_HOST", "localhost"),
            "port": int(os.getenv("QDRANT_HTTP_PORT", "6333")),
        },
    }


@pytest.fixture
async def postgresql_backend(
    docker_services_config,
) -> AsyncGenerator["PostgreSQLMemoryBackend", None]:
    """Create a PostgreSQL backend for testing.
    
    Requires Docker services to be running.
    Use: pytest -m postgresql
    """
    pytest.importorskip("asyncpg")
    from bruno_memory.backends.postgresql import PostgreSQLMemoryBackend
    from bruno_memory.base.config import PostgreSQLConfig

    config_dict = docker_services_config["postgresql"]
    config = PostgreSQLConfig(**config_dict)
    backend = PostgreSQLMemoryBackend(config)

    await backend.connect()
    
    # Clean up test data before test
    try:
        await backend._pool.execute("TRUNCATE TABLE messages, memory_entries CASCADE")
    except Exception:
        pass  # Tables might not exist yet

    yield backend

    # Clean up test data after test
    try:
        await backend._pool.execute("TRUNCATE TABLE messages, memory_entries CASCADE")
    except Exception:
        pass

    await backend.disconnect()


@pytest.fixture
async def redis_backend(docker_services_config) -> AsyncGenerator["RedisMemoryBackend", None]:
    """Create a Redis backend for testing.
    
    Requires Docker services to be running.
    Use: pytest -m redis
    """
    pytest.importorskip("redis")
    from bruno_memory.backends.redis import RedisMemoryBackend
    from bruno_memory.base.config import RedisConfig

    config_dict = docker_services_config["redis"]
    config = RedisConfig(**config_dict)
    backend = RedisMemoryBackend(config)

    await backend.connect()
    
    # Clean up test data before test
    try:
        await backend._client.flushdb()
    except Exception:
        pass

    yield backend

    # Clean up test data after test
    try:
        await backend._client.flushdb()
    except Exception:
        pass

    await backend.disconnect()


@pytest.fixture
async def chromadb_backend(
    docker_services_config,
) -> AsyncGenerator["ChromaDBMemoryBackend", None]:
    """Create a ChromaDB backend for testing.
    
    Requires Docker services to be running.
    Use: pytest -m chromadb
    """
    pytest.importorskip("chromadb")
    from bruno_memory.backends.vector.chromadb_backend import ChromaDBMemoryBackend
    from bruno_memory.backends.vector.schema import ChromaDBConfig

    config_dict = docker_services_config["chromadb"]
    config = ChromaDBConfig(**config_dict)
    backend = ChromaDBMemoryBackend(config)

    await backend.connect()
    
    # Clean up test collections before test
    try:
        collections = await backend._client.list_collections()
        for collection in collections:
            if collection.name.startswith("test_"):
                await backend._client.delete_collection(collection.name)
    except Exception:
        pass

    yield backend

    # Clean up test collections after test
    try:
        collections = await backend._client.list_collections()
        for collection in collections:
            if collection.name.startswith("test_"):
                await backend._client.delete_collection(collection.name)
    except Exception:
        pass

    await backend.disconnect()


@pytest.fixture
async def qdrant_backend(docker_services_config) -> AsyncGenerator["QdrantMemoryBackend", None]:
    """Create a Qdrant backend for testing.
    
    Requires Docker services to be running.
    Use: pytest -m qdrant
    """
    pytest.importorskip("qdrant_client")
    from bruno_memory.backends.vector.qdrant_backend import QdrantMemoryBackend
    from bruno_memory.backends.vector.schema import QdrantConfig

    config_dict = docker_services_config["qdrant"]
    config = QdrantConfig(**config_dict)
    backend = QdrantMemoryBackend(config)

    await backend.connect()
    
    # Clean up test collections before test
    try:
        collections = await backend._client.get_collections()
        for collection in collections.collections:
            if collection.name.startswith("test_"):
                await backend._client.delete_collection(collection.name)
    except Exception:
        pass

    yield backend

    # Clean up test collections after test
    try:
        collections = await backend._client.get_collections()
        for collection in collections.collections:
            if collection.name.startswith("test_"):
                await backend._client.delete_collection(collection.name)
    except Exception:
        pass

    await backend.disconnect()


@pytest.fixture
def skip_if_no_docker():
    """Skip test if Docker services are not available."""
    import socket

    def is_port_open(host: str, port: int) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    # Check if PostgreSQL is available (indicator that Docker services are running)
    if not is_port_open("localhost", 5432):
        pytest.skip("Docker services are not running. Run: ./scripts/setup-test-env.ps1")
