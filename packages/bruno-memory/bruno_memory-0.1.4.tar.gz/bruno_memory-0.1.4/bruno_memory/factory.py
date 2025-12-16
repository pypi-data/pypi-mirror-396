"""
Memory backend factory for creating and managing backend instances.

Provides a centralized factory pattern for creating memory backends
with proper configuration validation and type safety.
"""

import inspect
import logging
import os
from importlib.metadata import entry_points

try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

from .base import CONFIG_CLASSES, BaseMemoryBackend, MemoryConfig
from .exceptions import BackendNotFoundError, ConfigurationError, ValidationError

logger = logging.getLogger(__name__)


class MemoryBackendFactory:
    """Factory for creating memory backend instances."""

    def __init__(self, auto_discover: bool = True, load_env: bool = True):
        """Initialize the factory with empty backend registry.

        Args:
            auto_discover: Automatically discover backends via entry points
            load_env: Load environment variables from .env file
        """
        self._backends: dict[str, type[BaseMemoryBackend]] = {}
        self._config_types: dict[str, type[MemoryConfig]] = CONFIG_CLASSES.copy()

        if load_env and DOTENV_AVAILABLE:
            load_dotenv()
            logger.info("Loaded environment variables from .env")

        if auto_discover:
            self.discover_backends()

    def register_backend(
        self,
        name: str,
        backend_class: type[BaseMemoryBackend],
        config_class: type[MemoryConfig] | None = None,
    ) -> None:
        """Register a memory backend implementation.

        Args:
            name: Backend name (e.g., 'sqlite', 'postgresql')
            backend_class: Backend implementation class
            config_class: Optional configuration class override

        Raises:
            ValidationError: If backend class is invalid
        """
        if not inspect.isclass(backend_class):
            raise ValidationError(f"Backend must be a class, got {type(backend_class)}")

        if not issubclass(backend_class, BaseMemoryBackend):
            raise ValidationError(
                f"Backend class must inherit from BaseMemoryBackend, "
                f"got {backend_class.__name__}"
            )

        self._backends[name] = backend_class

        if config_class:
            if not issubclass(config_class, MemoryConfig):
                raise ValidationError(
                    f"Config class must inherit from MemoryConfig, " f"got {config_class.__name__}"
                )
            self._config_types[name] = config_class

    def unregister_backend(self, name: str) -> None:
        """Unregister a memory backend implementation.

        Args:
            name: Backend name to unregister
        """
        self._backends.pop(name, None)
        self._config_types.pop(name, None)

    def discover_backends(self) -> None:
        """Discover and register backends via entry points.

        Looks for entry points in the 'bruno_memory.backends' group.
        Each entry point should provide a backend class.
        """
        try:
            eps = entry_points()
            # Handle both old and new entry_points() API
            if hasattr(eps, "select"):
                # Python 3.10+ API
                backend_entries = eps.select(group="bruno_memory.backends")
            else:
                # Python 3.9 API
                backend_entries = eps.get("bruno_memory.backends", [])

            for ep in backend_entries:
                try:
                    backend_class = ep.load()
                    # Entry point name is the backend name
                    self.register_backend(ep.name, backend_class)
                    logger.info(f"Discovered backend via entry point: {ep.name}")
                except Exception as e:
                    logger.warning(f"Failed to load backend entry point {ep.name}: {e}")
        except Exception as e:
            logger.warning(f"Backend discovery failed: {e}")

    def unregister_backend(self, name: str) -> None:
        """Unregister a memory backend implementation.

        Args:
            name: Backend name to unregister
        """
        self._backends.pop(name, None)
        self._config_types.pop(name, None)

    def list_backends(self) -> dict[str, str]:
        """List all registered backend implementations.

        Returns:
            Dictionary mapping backend names to class names
        """
        return {name: cls.__name__ for name, cls in self._backends.items()}

    def create_config(self, backend_type: str, **kwargs) -> MemoryConfig:
        """Create a configuration instance for the specified backend type.

        Args:
            backend_type: Backend type name
            **kwargs: Configuration parameters

        Returns:
            Configuration instance for the backend

        Raises:
            BackendNotFoundError: If backend type is not registered
            ConfigurationError: If configuration creation fails
        """
        if backend_type not in self._config_types:
            available = list(self._config_types.keys())
            raise BackendNotFoundError(
                f"Backend type '{backend_type}' not found. " f"Available backends: {available}"
            )

        config_class = self._config_types[backend_type]

        try:
            return config_class(**kwargs)
        except Exception as e:
            raise ConfigurationError(f"Failed to create {backend_type} configuration: {e}")

    def create_backend(
        self, backend_type: str, config: MemoryConfig | None = None, **config_kwargs
    ) -> BaseMemoryBackend:
        """Create a memory backend instance.

        Args:
            backend_type: Backend type name (e.g., 'sqlite', 'postgresql')
            config: Optional pre-created configuration instance
            **config_kwargs: Configuration parameters (if config not provided)

        Returns:
            Configured backend instance

        Raises:
            BackendNotFoundError: If backend type is not registered
            ConfigurationError: If configuration is invalid
        """
        if backend_type not in self._backends:
            available = list(self._backends.keys())
            raise BackendNotFoundError(
                f"Backend type '{backend_type}' not found. " f"Available backends: {available}"
            )

        # Create or validate configuration
        if config is None:
            config = self.create_config(backend_type, **config_kwargs)
        else:
            expected_type = self._config_types.get(backend_type)
            if expected_type and not isinstance(config, expected_type):
                raise ConfigurationError(
                    f"Invalid config type for {backend_type}. "
                    f"Expected {expected_type.__name__}, got {type(config).__name__}"
                )

        backend_class = self._backends[backend_type]

        try:
            return backend_class(config)
        except Exception as e:
            raise ConfigurationError(f"Failed to create {backend_type} backend: {e}")

    def get_backend_class(self, backend_type: str) -> type[BaseMemoryBackend]:
        """Get the backend class for a given type.

        Args:
            backend_type: Backend type name

        Returns:
            Backend class

        Raises:
            BackendNotFoundError: If backend type is not registered
        """
        if backend_type not in self._backends:
            available = list(self._backends.keys())
            raise BackendNotFoundError(
                f"Backend type '{backend_type}' not found. " f"Available backends: {available}"
            )

        return self._backends[backend_type]

    def get_config_class(self, backend_type: str) -> type[MemoryConfig]:
        """Get the configuration class for a given backend type.

        Args:
            backend_type: Backend type name

        Returns:
            Configuration class

        Raises:
            BackendNotFoundError: If backend type is not registered
        """
        if backend_type not in self._config_types:
            available = list(self._config_types.keys())
            raise BackendNotFoundError(
                f"Backend type '{backend_type}' not found. " f"Available backends: {available}"
            )

        return self._config_types[backend_type]

    def create_from_env(
        self, backend_type_env: str = "BRUNO_MEMORY_BACKEND", **config_overrides
    ) -> BaseMemoryBackend:
        """Create a backend from environment variables.

        Args:
            backend_type_env: Environment variable name for backend type
            **config_overrides: Override specific configuration values

        Returns:
            Configured backend instance

        Raises:
            ConfigurationError: If environment configuration is invalid
        """
        backend_type = os.getenv(backend_type_env)
        if not backend_type:
            raise ConfigurationError(
                f"Environment variable {backend_type_env} not set. "
                f"Available backends: {list(self._backends.keys())}"
            )

        # Get configuration class and extract env-based config
        config_class = self.get_config_class(backend_type)

        # Build config from environment
        config_dict = {}
        for field_name in config_class.model_fields.keys():
            env_key = f"BRUNO_MEMORY_{backend_type.upper()}_{field_name.upper()}"
            env_value = os.getenv(env_key)
            if env_value is not None:
                config_dict[field_name] = env_value

        # Apply overrides
        config_dict.update(config_overrides)

        logger.info(f"Creating {backend_type} backend from environment")
        return self.create_backend(backend_type, **config_dict)

    def create_with_fallback(
        self,
        backend_types: list[str],
        configs: list[MemoryConfig] | None = None,
        **common_config,
    ) -> BaseMemoryBackend:
        """Create a backend with fallback chain.

        Tries each backend in order until one succeeds.

        Args:
            backend_types: List of backend types to try in order
            configs: Optional list of pre-created configs (same order)
            **common_config: Common config parameters for all backends

        Returns:
            First successfully created backend

        Raises:
            ConfigurationError: If all backends fail to create
        """
        errors = []

        for i, backend_type in enumerate(backend_types):
            try:
                config = configs[i] if configs and i < len(configs) else None
                backend = self.create_backend(backend_type, config=config, **common_config)
                logger.info(f"Successfully created {backend_type} backend")
                return backend
            except Exception as e:
                error_msg = f"{backend_type}: {e}"
                errors.append(error_msg)
                logger.warning(f"Failed to create {backend_type} backend: {e}")

        raise ConfigurationError(
            f"All backends failed to create. Tried: {backend_types}. "
            f"Errors: {'; '.join(errors)}"
        )


# Global factory instance
factory = MemoryBackendFactory()


# Convenience functions that use the global factory
def register_backend(
    name: str,
    backend_class: type[BaseMemoryBackend],
    config_class: type[MemoryConfig] | None = None,
) -> None:
    """Register a memory backend implementation in the global factory.

    Args:
        name: Backend name
        backend_class: Backend implementation class
        config_class: Optional configuration class override
    """
    factory.register_backend(name, backend_class, config_class)


def create_backend(
    backend_type: str, config: MemoryConfig | None = None, **config_kwargs
) -> BaseMemoryBackend:
    """Create a memory backend instance using the global factory.

    Args:
        backend_type: Backend type name
        config: Optional pre-created configuration instance
        **config_kwargs: Configuration parameters

    Returns:
        Configured backend instance
    """
    return factory.create_backend(backend_type, config, **config_kwargs)


def create_config(backend_type: str, **kwargs) -> MemoryConfig:
    """Create a configuration instance using the global factory.

    Args:
        backend_type: Backend type name
        **kwargs: Configuration parameters

    Returns:
        Configuration instance
    """
    return factory.create_config(backend_type, **kwargs)


def list_backends() -> dict[str, str]:
    """List all registered backend implementations.

    Returns:
        Dictionary mapping backend names to class names
    """
    return factory.list_backends()


def create_from_env(
    backend_type_env: str = "BRUNO_MEMORY_BACKEND", **config_overrides
) -> BaseMemoryBackend:
    """Create a backend from environment variables using the global factory.

    Args:
        backend_type_env: Environment variable name for backend type
        **config_overrides: Override specific configuration values

    Returns:
        Configured backend instance
    """
    return factory.create_from_env(backend_type_env, **config_overrides)


def create_with_fallback(
    backend_types: list[str], configs: list[MemoryConfig] | None = None, **common_config
) -> BaseMemoryBackend:
    """Create a backend with fallback chain using the global factory.

    Args:
        backend_types: List of backend types to try in order
        configs: Optional list of pre-created configs
        **common_config: Common config parameters

    Returns:
        First successfully created backend
    """
    return factory.create_with_fallback(backend_types, configs, **common_config)


__all__ = [
    "MemoryBackendFactory",
    "factory",
    "register_backend",
    "create_backend",
    "create_config",
    "list_backends",
]
