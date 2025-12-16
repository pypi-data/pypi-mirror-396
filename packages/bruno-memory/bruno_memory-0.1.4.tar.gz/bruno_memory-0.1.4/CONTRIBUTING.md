# Contributing to bruno-memory

Thank you for your interest in contributing to bruno-memory! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- (Optional) Docker for testing PostgreSQL/Redis/Vector databases

### Initial Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/bruno-memory.git
cd bruno-memory
```

2. **Create a virtual environment**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Unix/MacOS
source .venv/bin/activate
```

3. **Install development dependencies**

```bash
pip install -e ".[dev,all]"
```

This installs:
- bruno-memory in editable mode
- All backend dependencies
- Development tools (pytest, black, ruff, mypy)
- Documentation tools (mkdocs, mkdocs-material)

## Project Structure

```
bruno-memory/
├── bruno_memory/          # Main package
│   ├── __init__.py       # Package initialization
│   ├── factory.py        # Backend factory
│   ├── exceptions.py     # Custom exceptions
│   ├── base/            # Base classes
│   ├── backends/        # Backend implementations
│   │   ├── sqlite/
│   │   ├── postgresql/
│   │   ├── redis/
│   │   └── vector/
│   ├── managers/        # Manager classes
│   └── utils/           # Utility modules
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── docs/               # Documentation
├── examples/           # Usage examples
└── scripts/            # Development scripts
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Follow the coding standards (see below).

### 3. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_factory.py

# Run with coverage
pytest --cov=bruno_memory --cov-report=html

# Run fast tests only (skip slow integration tests)
pytest -m "not slow"
```

### 4. Format and Lint

```bash
# Format code with black
black bruno_memory tests

# Lint with ruff
ruff check bruno_memory tests

# Type check with mypy
mypy bruno_memory
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature"
```

**Commit Message Format:**

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Build/tooling changes

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Style Guide

We follow **PEP 8** with some modifications:

- Line length: 100 characters
- Use double quotes for strings
- Use type hints for all functions
- Use Google-style docstrings

### Type Hints

All functions should have complete type hints:

```python
async def store_message(
    self,
    message: Message,
    conversation_id: Optional[str] = None
) -> str:
    """Store a message in the backend.
    
    Args:
        message: The message to store
        conversation_id: Optional conversation identifier
        
    Returns:
        The stored message ID
        
    Raises:
        StorageError: If storage fails
    """
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def function_name(arg1: str, arg2: int) -> bool:
    """Short description.
    
    Longer description if needed. Can span multiple lines.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When arg1 is empty
        TypeError: When arg2 is negative
        
    Example:
        >>> result = function_name("hello", 5)
        >>> print(result)
        True
    """
```

### Error Handling

Use custom exceptions from `bruno_memory.exceptions`:

```python
from bruno_memory.exceptions import StorageError, ValidationError

if not valid:
    raise ValidationError("Invalid input")

try:
    await backend.connect()
except Exception as e:
    raise StorageError(f"Failed to connect: {e}") from e
```

## Testing

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use pytest fixtures for common setup
- Use async tests for async code
- Aim for >90% code coverage

**Example Test:**

```python
import pytest
from bruno_memory import create_backend

@pytest.fixture
async def backend():
    """Create a test backend."""
    backend = create_backend("sqlite", database_path=":memory:")
    await backend.connect()
    yield backend
    await backend.disconnect()

@pytest.mark.asyncio
async def test_store_message(backend):
    """Test storing a message."""
    message = Message(
        content="Test message",
        role=MessageRole.USER,
        message_type=MessageType.TEXT
    )
    
    message_id = await backend.store_message(message)
    assert message_id is not None
    
    retrieved = await backend.retrieve_messages(limit=1)
    assert len(retrieved) == 1
    assert retrieved[0].content == "Test message"
```

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.slow  # Slow tests (integration, database)
@pytest.mark.unit  # Fast unit tests
@pytest.mark.asyncio  # Async tests
```

### Fixtures

Common fixtures are in `tests/conftest.py`:

- `temp_db_path`: Temporary database path
- `sample_messages`: Sample message list
- `sample_memories`: Sample memory list

## Backend Development

### Creating a New Backend

1. **Create backend directory:**

```bash
mkdir -p bruno_memory/backends/mybackend
touch bruno_memory/backends/mybackend/__init__.py
touch bruno_memory/backends/mybackend/backend.py
```

2. **Implement the backend:**

```python
from bruno_memory.base import BaseMemoryBackend, MemoryConfig

class MyBackendConfig(MemoryConfig):
    """Configuration for MyBackend."""
    backend_type: str = "mybackend"
    connection_url: str

class MyBackend(BaseMemoryBackend):
    """Implementation of MyBackend."""
    
    async def connect(self) -> None:
        """Connect to the backend."""
        ...
    
    async def disconnect(self) -> None:
        """Disconnect from the backend."""
        ...
    
    async def store_message(self, message: Message) -> str:
        """Store a message."""
        ...
    
    # Implement other required methods...
```

3. **Register the backend:**

```python
# bruno_memory/backends/mybackend/__init__.py
from .backend import MyBackend, MyBackendConfig
from bruno_memory.factory import register_backend

register_backend("mybackend", MyBackend, MyBackendConfig)
```

4. **Add tests:**

Create `tests/unit/test_mybackend.py` following existing backend tests.

### Backend Requirements

All backends must:

- Inherit from `BaseMemoryBackend`
- Implement all abstract methods
- Handle errors gracefully
- Support async operations
- Include comprehensive tests
- Document configuration options

## Documentation

### Building Docs Locally

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

Visit http://localhost:8000 to view the documentation.

### Writing Documentation

- Main docs are in `docs/` directory
- Use Markdown with Material for MkDocs extensions
- Include code examples
- Add diagrams where helpful (using Mermaid)

**Example:**

````markdown
# Feature Name

Brief description.

## Usage

```python
from bruno_memory import feature

# Example code
result = feature.do_something()
```

## Advanced

More detailed information...
````

## Release Process

Releases are handled by maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a GitHub release
4. CI automatically publishes to PyPI

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/meggy-ai/bruno-memory/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/meggy-ai/bruno-memory/issues)
- **Chat**: Join our Discord (link in README)

## Code of Conduct

Be respectful and inclusive. We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Annual contributor spotlight

Thank you for contributing to bruno-memory! 🎉
