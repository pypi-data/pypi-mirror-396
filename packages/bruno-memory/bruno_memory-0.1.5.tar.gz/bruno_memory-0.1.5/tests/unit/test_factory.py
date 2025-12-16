"""Tests for MemoryBackendFactory."""

import pytest

from bruno_memory.backends.sqlite import SQLiteMemoryBackend
from bruno_memory.exceptions import BackendNotFoundError, ConfigurationError
from bruno_memory.factory import MemoryBackendFactory, create_backend, list_backends


class TestMemoryBackendFactory:
    """Test cases for MemoryBackendFactory."""

    def test_get_backend_names(self):
        """Test getting available backend names."""
        names = list_backends()
        assert "sqlite" in names
        assert isinstance(names, dict)

    def test_create_sqlite_backend(self, temp_db_path):
        """Test creating SQLite backend."""
        backend = create_backend("sqlite", database_path=temp_db_path)

        assert isinstance(backend, SQLiteMemoryBackend)
        assert backend.config.database_path == temp_db_path

    def test_create_backend_with_config_dict(self, temp_db_path):
        """Test creating backend with config dictionary."""
        backend = create_backend("sqlite", database_path=temp_db_path)

        assert isinstance(backend, SQLiteMemoryBackend)
        assert backend.config.database_path == temp_db_path

    def test_create_backend_with_kwargs(self, temp_db_path):
        """Test creating backend with kwargs."""
        backend = create_backend("sqlite", database_path=temp_db_path, enable_fts=False)

        assert isinstance(backend, SQLiteMemoryBackend)
        assert backend.config.database_path == temp_db_path
        assert backend.config.enable_fts is False

    def test_create_unknown_backend(self):
        """Test creating unknown backend type."""
        with pytest.raises(BackendNotFoundError):
            create_backend("unknown_backend")

    def test_create_backend_invalid_config(self):
        """Test creating backend with invalid configuration."""
        with pytest.raises((ConfigurationError, TypeError)):
            create_backend("sqlite", invalid_param="value")

    def test_register_backend(self):
        """Test registering a new backend."""
        from bruno_memory.base import BaseMemoryBackend, MemoryConfig
        from bruno_memory.factory import factory

        class DummyConfig(MemoryConfig):
            backend_type: str = "dummy"

        class DummyBackend(BaseMemoryBackend):
            async def connect(self):
                pass

            async def disconnect(self):
                pass

            async def health_check(self):
                return True

        factory.register_backend("dummy", DummyBackend, DummyConfig)

        assert "dummy" in list_backends()

        # Clean up
        if "dummy" in factory._backends:
            del factory._backends["dummy"]
        if "dummy" in factory._config_types:
            del factory._config_types["dummy"]

    def test_create_from_env(self, temp_db_path, monkeypatch):
        """Test creating backend from environment variables."""
        monkeypatch.setenv("BRUNO_MEMORY_BACKEND", "sqlite")
        monkeypatch.setenv("BRUNO_MEMORY_SQLITE_DATABASE_PATH", temp_db_path)

        from bruno_memory.factory import factory

        backend = factory.create_from_env()

        assert isinstance(backend, SQLiteMemoryBackend)
        assert backend.config.database_path == temp_db_path

    def test_create_from_env_missing_var(self, monkeypatch):
        """Test creating backend without required env var."""
        # Ensure the env var is not set
        monkeypatch.delenv("BRUNO_MEMORY_BACKEND", raising=False)

        from bruno_memory.factory import factory

        with pytest.raises(ConfigurationError):
            factory.create_from_env()

    def test_create_from_env_with_override(self, temp_db_path, monkeypatch):
        """Test creating backend from env with config override."""
        monkeypatch.setenv("BRUNO_MEMORY_BACKEND", "sqlite")
        monkeypatch.setenv("BRUNO_MEMORY_SQLITE_DATABASE_PATH", "/wrong/path")

        from bruno_memory.factory import factory

        backend = factory.create_from_env(database_path=temp_db_path)

        assert isinstance(backend, SQLiteMemoryBackend)
        assert backend.config.database_path == temp_db_path  # Override takes precedence

    def test_create_with_fallback_first_succeeds(self, temp_db_path):
        """Test fallback chain when first backend succeeds."""
        from bruno_memory.factory import factory

        backend = factory.create_with_fallback(["sqlite", "redis"], database_path=temp_db_path)

        assert isinstance(backend, SQLiteMemoryBackend)

    def test_create_with_fallback_second_succeeds(self):
        """Test fallback chain when first fails and second succeeds."""
        import tempfile

        from bruno_memory.factory import factory

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = f"{temp_dir}/test.db"

            # First will fail (invalid backend), second will succeed
            backend = factory.create_with_fallback(
                ["nonexistent", "sqlite"], database_path=temp_path
            )

            assert isinstance(backend, SQLiteMemoryBackend)

    def test_create_with_fallback_all_fail(self):
        """Test fallback chain when all backends fail."""
        from bruno_memory.factory import factory

        with pytest.raises(ConfigurationError) as exc_info:
            factory.create_with_fallback(["nonexistent1", "nonexistent2"], database_path=":memory:")

        assert "All backends failed" in str(exc_info.value)

    def test_discover_backends(self):
        """Test backend discovery via entry points."""
        from bruno_memory.factory import factory

        # Discovery runs on init, check that built-in backends are registered
        backends = factory.list_backends()
        assert len(backends) > 0
        assert "sqlite" in backends

    def test_list_backends(self):
        """Test listing registered backends."""
        backends = list_backends()

        assert isinstance(backends, dict)
        assert "sqlite" in backends
        assert backends["sqlite"] == "SQLiteMemoryBackend"

    def test_get_backend_class(self):
        """Test getting backend class."""
        from bruno_memory.factory import factory

        backend_class = factory.get_backend_class("sqlite")
        assert backend_class == SQLiteMemoryBackend

    def test_get_backend_class_not_found(self):
        """Test getting non-existent backend class."""
        from bruno_memory.factory import factory

        with pytest.raises(BackendNotFoundError):
            factory.get_backend_class("nonexistent")

    def test_get_config_class(self):
        """Test getting config class."""
        from bruno_memory.base import SQLiteConfig
        from bruno_memory.factory import factory

        config_class = factory.get_config_class("sqlite")
        assert config_class == SQLiteConfig

    def test_get_config_class_not_found(self):
        """Test getting non-existent config class."""
        from bruno_memory.factory import factory

        with pytest.raises(BackendNotFoundError):
            factory.get_config_class("nonexistent")

    def test_unregister_backend(self):
        """Test unregistering a backend."""
        from bruno_memory.base import BaseMemoryBackend, MemoryConfig
        from bruno_memory.factory import factory

        class TestConfig(MemoryConfig):
            backend_type: str = "test"

        class TestBackend(BaseMemoryBackend):
            async def connect(self):
                pass

            async def disconnect(self):
                pass

            async def health_check(self):
                return True

        # Register
        factory.register_backend("test_temp", TestBackend, TestConfig)
        assert "test_temp" in factory.list_backends()

        # Unregister
        factory.unregister_backend("test_temp")
        assert "test_temp" not in factory.list_backends()

    def test_create_config(self, temp_db_path):
        """Test creating a config instance."""
        from bruno_memory.factory import create_config, factory

        config = create_config("sqlite", database_path=temp_db_path)

        assert config.backend_type == "sqlite"
        assert config.database_path == temp_db_path

    def test_create_config_not_found(self):
        """Test creating config for non-existent backend."""
        from bruno_memory.factory import create_config

        with pytest.raises(BackendNotFoundError):
            create_config("nonexistent")
