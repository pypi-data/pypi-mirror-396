# Factory API

The factory provides a centralized way to create and manage memory backend instances.

::: bruno_memory.factory.MemoryBackendFactory
    options:
      show_root_heading: true
      show_source: true
      members:
        - __init__
        - register_backend
        - unregister_backend
        - discover_backends
        - create_backend
        - create_config
        - create_from_env
        - create_with_fallback
        - list_backends
        - get_backend_class
        - get_config_class

## Convenience Functions

::: bruno_memory.factory.create_backend
    options:
      show_root_heading: true

::: bruno_memory.factory.create_config
    options:
      show_root_heading: true

::: bruno_memory.factory.create_from_env
    options:
      show_root_heading: true

::: bruno_memory.factory.create_with_fallback
    options:
      show_root_heading: true

::: bruno_memory.factory.list_backends
    options:
      show_root_heading: true

::: bruno_memory.factory.register_backend
    options:
      show_root_heading: true

## Global Factory Instance

The package provides a pre-configured global factory instance:

```python
from bruno_memory import factory

# Use the global factory
backends = factory.list_backends()
backend = factory.create_backend("sqlite", database_path=":memory:")
```

## Examples

### Basic Usage

```python
from bruno_memory import create_backend

# Create SQLite backend
backend = create_backend("sqlite", database_path="memory.db")
await backend.connect()
```

### Environment Configuration

```python
from bruno_memory import create_from_env
import os

# Set environment variables
os.environ["BRUNO_MEMORY_BACKEND"] = "postgresql"
os.environ["BRUNO_MEMORY_POSTGRESQL_CONNECTION_STRING"] = "postgresql://..."

# Create from environment
backend = create_from_env()
```

### Fallback Chain

```python
from bruno_memory import create_with_fallback

# Try Redis first, fallback to SQLite
backend = create_with_fallback(
    ["redis", "sqlite"],
    database_path="fallback.db"
)
```

### Custom Backend Registration

```python
from bruno_memory import register_backend
from bruno_memory.base import BaseMemoryBackend, MemoryConfig

class MyConfig(MemoryConfig):
    backend_type: str = "custom"
    api_key: str

class MyBackend(BaseMemoryBackend):
    async def connect(self):
        ...
    # Implement other methods...

# Register custom backend
register_backend("custom", MyBackend, MyConfig)

# Now it can be created via factory
backend = create_backend("custom", api_key="secret")
```

### Backend Discovery

The factory automatically discovers backends via:

1. **Built-in backends**: Registered when importing `bruno_memory.backends`
2. **Entry points**: Third-party backends can register via entry points

```toml
# pyproject.toml for a plugin
[project.entry-points."bruno_memory.backends"]
mybackend = "mypackage.backend:MyBackend"
```
