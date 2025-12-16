# Testing Guide for bruno-memory

## Overview

Bruno-memory has a comprehensive testing infrastructure that supports multiple backends with Docker-based testing environments.

## Quick Start

```bash
# Run all tests with Docker
make test-docker

# Test specific backend
make test-postgresql
```

## Test Structure

```
tests/
├── unit/                  # Unit tests (no external dependencies)
│   ├── test_factory.py
│   ├── test_sqlite_backend.py
│   └── ...
├── integration/           # Integration tests (require services)
│   ├── test_postgresql_integration.py
│   ├── test_redis_integration.py
│   └── ...
└── conftest.py           # Shared fixtures
```

## Test Markers

Tests are organized using pytest markers for selective execution:

### Available Markers

- `postgresql` - Tests requiring PostgreSQL
- `redis` - Tests requiring Redis
- `chromadb` - Tests requiring ChromaDB
- `qdrant` - Tests requiring Qdrant
- `vector` - Tests requiring any vector database
- `requires_docker` - Tests requiring Docker services
- `slow` - Long-running tests
- `benchmark` - Performance benchmarks

### Usage Examples

```bash
# Run only PostgreSQL tests
pytest -m postgresql

# Run all vector database tests
pytest -m vector

# Run multiple markers
pytest -m "postgresql or redis"

# Exclude specific tests
pytest -m "not slow"

# Run integration tests
pytest -m requires_docker
```

## Docker Testing

### Why Docker Testing?

- **Consistent environments**: Everyone tests against the same service versions
- **Isolated testing**: No conflicts with local services
- **Complete coverage**: Test all backends without manual setup
- **CI/CD ready**: Same environment locally and in CI

### Docker Profiles

#### 1. Minimal Profile
Fastest startup with essential services only.

**Services:** PostgreSQL, Redis

```bash
# PowerShell
.\scripts\setup-test-env.ps1 -Profile minimal

# Bash
bash scripts/setup-test-env.sh --profile minimal

# Makefile
make test-docker-minimal
```

**Use cases:**
- Quick development iterations
- Testing core functionality
- CI for non-vector features

#### 2. Full Profile (Default)
Complete testing environment with all backends.

**Services:** PostgreSQL, Redis, ChromaDB, Qdrant

```bash
# PowerShell
.\scripts\setup-test-env.ps1 -Profile full

# Bash
bash scripts/setup-test-env.sh --profile full

# Makefile
make test-docker
```

**Use cases:**
- Comprehensive testing
- Vector database development
- Pre-release validation

#### 3. CI Profile
Optimized for CI/CD pipelines.

**Services:** All services with tmpfs for speed

```bash
# PowerShell
.\scripts\setup-test-env.ps1 -Profile ci

# Bash
bash scripts/setup-test-env.sh --profile ci
```

**Features:**
- Uses tmpfs for faster I/O
- No persistent volumes
- Optimized health checks

### Service Management

#### Starting Services

```bash
# Using Makefile
make docker-up

# Using scripts (with options)
.\scripts\setup-test-env.ps1 -Profile full -Pull -Build
bash scripts/setup-test-env.sh --profile full --pull --build

# Options:
#   -Pull / --pull   : Pull latest images
#   -Build / --build : Rebuild custom images
#   -Clean / --clean : Remove existing containers first
```

#### Checking Service Status

```bash
# Quick status
make docker-status

# Detailed status
docker-compose ps

# Check individual service
docker logs bruno-memory-postgres
```

#### Stopping Services

```bash
# Stop services (preserve data)
make docker-down

# Stop and remove data
make docker-down-volumes

# Complete cleanup
make docker-teardown
```

### Running Tests with Docker

#### Automated Test Runs

The test runner handles the complete lifecycle:

```bash
# PowerShell
.\scripts\run-tests-docker.ps1 `
    -Profile full `
    -Verbose `
    -NoCoverage

# Bash
bash scripts/run-tests-docker.sh \
    --profile full \
    --verbose \
    --no-coverage
```

**Options:**
- `-Profile` / `--profile`: Environment profile (minimal/full/ci)
- `-Markers` / `--markers`: Pytest markers to run
- `-TestPath` / `--test-path`: Specific test path
- `-Verbose` / `--verbose`: Verbose output
- `-NoCoverage` / `--no-coverage`: Skip coverage
- `-KeepEnv` / `--keep-env`: Keep services running after tests
- `-SetupOnly` / `--setup-only`: Only setup, don't run tests

#### Manual Test Runs

For iterative development, start services once and run tests multiple times:

```bash
# 1. Start services
.\scripts\setup-test-env.ps1 -Profile full

# 2. Run tests as needed
pytest tests/unit/test_postgresql_backend.py -v
pytest tests/ -m postgresql
pytest tests/integration/ -v

# 3. Stop services when done
.\scripts\teardown-test-env.ps1
```

#### Backend-Specific Testing

```bash
# Test single backend
make test-postgresql
make test-redis
make test-chromadb
make test-qdrant

# Test all vector backends
make test-vector

# Using markers directly
pytest -m postgresql -v
pytest -m "chromadb or qdrant" -v
```

### Test Fixtures

Docker fixtures are available in `tests/conftest.py`:

#### Available Fixtures

```python
# Configuration fixture
docker_services_config  # Service connection details

# Backend fixtures (auto-cleanup)
postgresql_backend      # PostgreSQL backend
redis_backend          # Redis backend
chromadb_backend       # ChromaDB backend
qdrant_backend         # Qdrant backend

# Utility fixtures
skip_if_no_docker      # Skip if Docker not available
```

#### Using Fixtures in Tests

```python
import pytest


async def test_postgresql_storage(postgresql_backend):
    """Test PostgreSQL backend storage."""
    # Backend is already connected and cleaned
    message = create_test_message()
    
    # Store message
    msg_id = await postgresql_backend.store_message(message)
    
    # Retrieve message
    retrieved = await postgresql_backend.get_message(msg_id)
    assert retrieved.content == message.content
    
    # Cleanup happens automatically


async def test_redis_caching(redis_backend):
    """Test Redis caching."""
    # Set value
    await redis_backend.cache_set("key", "value")
    
    # Get value
    result = await redis_backend.cache_get("key")
    assert result == "value"


async def test_vector_search(chromadb_backend):
    """Test vector similarity search."""
    # Add vectors
    await chromadb_backend.add_vectors(vectors, metadata)
    
    # Search
    results = await chromadb_backend.search(query_vector, limit=5)
    assert len(results) <= 5
```

#### Fixture Configuration

Fixtures read configuration from environment variables:

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bruno_memory
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=15

# ChromaDB
CHROMA_HOST=localhost
CHROMA_HTTP_PORT=8000

# Qdrant
QDRANT_HOST=localhost
QDRANT_HTTP_PORT=6333
```

### Connection Testing

Individual connection test scripts verify service functionality:

```bash
# PostgreSQL
.\scripts\test-postgres-connection.ps1

# Redis
.\scripts\test-redis-connection.ps1

# ChromaDB
.\scripts\test-chromadb-connection.ps1

# Qdrant
.\scripts\test-qdrant-connection.ps1
```

These scripts:
- Check service availability
- Verify health endpoints
- Test basic operations
- Display configuration

## Writing Tests

### Test Structure

```python
"""Test module for feature X."""

import pytest
from bruno_memory import MemoryFactory


class TestFeatureX:
    """Test suite for feature X."""
    
    async def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        memory = MemoryFactory.create("sqlite")
        
        # Act
        result = await memory.some_operation()
        
        # Assert
        assert result is not None
    
    @pytest.mark.postgresql
    async def test_with_postgresql(self, postgresql_backend):
        """Test with PostgreSQL backend."""
        # Backend is ready to use
        result = await postgresql_backend.some_operation()
        assert result is not None
    
    @pytest.mark.slow
    async def test_performance(self):
        """Test performance with large dataset."""
        # Long-running test
        pass
```

### Test Best Practices

#### 1. Use Descriptive Names

```python
# Good
async def test_store_message_returns_valid_id():
    ...

# Bad
async def test_store():
    ...
```

#### 2. Follow AAA Pattern

```python
async def test_retrieve_messages():
    # Arrange
    memory = MemoryFactory.create("sqlite")
    message = create_test_message()
    
    # Act
    await memory.store_message(message)
    messages = await memory.retrieve_messages(limit=10)
    
    # Assert
    assert len(messages) == 1
    assert messages[0].content == message.content
```

#### 3. Test One Thing

```python
# Good - tests one aspect
async def test_store_message_generates_id():
    memory = MemoryFactory.create("sqlite")
    msg_id = await memory.store_message(message)
    assert msg_id is not None

async def test_store_message_persists_content():
    memory = MemoryFactory.create("sqlite")
    await memory.store_message(message)
    retrieved = await memory.get_message(message.id)
    assert retrieved.content == message.content

# Bad - tests multiple things
async def test_store_message():
    memory = MemoryFactory.create("sqlite")
    msg_id = await memory.store_message(message)
    assert msg_id is not None
    retrieved = await memory.get_message(msg_id)
    assert retrieved.content == message.content
    assert retrieved.timestamp is not None
    # ... more assertions
```

#### 4. Use Fixtures for Setup

```python
@pytest.fixture
async def memory_with_messages():
    """Fixture providing memory backend with test messages."""
    memory = MemoryFactory.create("sqlite")
    messages = [create_test_message() for _ in range(10)]
    for msg in messages:
        await memory.store_message(msg)
    return memory, messages


async def test_retrieve_limit(memory_with_messages):
    """Test message retrieval with limit."""
    memory, messages = memory_with_messages
    
    retrieved = await memory.retrieve_messages(limit=5)
    assert len(retrieved) == 5
```

#### 5. Mark Tests Appropriately

```python
@pytest.mark.postgresql
@pytest.mark.slow
async def test_large_dataset_postgresql(postgresql_backend):
    """Test PostgreSQL with large dataset."""
    # This test:
    # - Requires PostgreSQL (marked with postgresql)
    # - Takes long time (marked with slow)
    # - Can be skipped with: pytest -m "not slow"
    pass
```

#### 6. Clean Up Resources

```python
async def test_with_cleanup():
    """Test with proper cleanup."""
    memory = MemoryFactory.create("sqlite", database_path="test.db")
    
    try:
        # Test code
        await memory.store_message(message)
    finally:
        # Cleanup
        await memory.disconnect()
        Path("test.db").unlink(missing_ok=True)
```

### Parameterized Tests

Test multiple scenarios with `pytest.mark.parametrize`:

```python
@pytest.mark.parametrize("backend_type", ["sqlite", "postgresql", "redis"])
async def test_all_backends(backend_type):
    """Test operation across all backends."""
    memory = MemoryFactory.create(backend_type)
    result = await memory.some_operation()
    assert result is not None


@pytest.mark.parametrize("limit,expected", [
    (5, 5),
    (10, 10),
    (100, 50),  # Max available
])
async def test_retrieve_limits(limit, expected):
    """Test different retrieval limits."""
    messages = await memory.retrieve_messages(limit=limit)
    assert len(messages) == expected
```

## Coverage

### Running with Coverage

```bash
# HTML report
pytest --cov=bruno_memory --cov-report=html

# Terminal report
pytest --cov=bruno_memory --cov-report=term-missing

# XML report (for CI)
pytest --cov=bruno_memory --cov-report=xml

# Multiple reports
pytest --cov=bruno_memory --cov-report=html --cov-report=term-missing
```

### Viewing Coverage

```bash
# Open HTML report
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals

- **Overall**: > 80%
- **Core modules**: > 90%
- **Utilities**: > 70%

## CI/CD Integration

### GitHub Actions

The `.github/workflows/docker-tests.yml` workflow:

1. **Matrix Testing**: Tests across Python 3.10, 3.11, 3.12
2. **Service Setup**: Starts all Docker services
3. **Backend Tests**: Runs backend-specific test suites
4. **Coverage**: Uploads to Codecov
5. **Artifacts**: Saves coverage reports

### Local CI Simulation

Test like CI will:

```bash
# Use CI profile
.\scripts\run-tests-docker.ps1 -Profile ci

# Or manually
docker-compose -f docker-compose.ci.yml up -d
pytest tests/ -v --cov=bruno_memory
docker-compose -f docker-compose.ci.yml down -v
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker ps

# Check port conflicts
netstat -an | findstr "5432 6379 8000 6333"

# View service logs
docker-compose logs <service>

# Restart services
docker-compose restart <service>
```

### Tests Fail to Connect

```bash
# Verify services are ready
.\scripts\wait-for-services.ps1

# Check environment variables
echo $env:POSTGRES_HOST
echo $env:REDIS_HOST

# Test connections manually
.\scripts\test-postgres-connection.ps1
.\scripts\test-redis-connection.ps1
```

### Slow Tests

```bash
# Skip slow tests
pytest -m "not slow"

# Run parallel tests (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto

# Profile tests
pytest --durations=10
```

### Port Conflicts

```bash
# Change ports in .env
POSTGRES_PORT=5433
REDIS_PORT=6380

# Or use docker-compose override
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```

## Performance Testing

### Benchmarks

```bash
# Run benchmark tests
pytest -m benchmark

# With timing details
pytest --durations=0 -m benchmark
```

### Load Testing

```python
@pytest.mark.benchmark
async def test_bulk_insert_performance():
    """Benchmark bulk message insertion."""
    memory = MemoryFactory.create("postgresql")
    messages = [create_test_message() for _ in range(1000)]
    
    start = time.time()
    for msg in messages:
        await memory.store_message(msg)
    duration = time.time() - start
    
    # Should complete in under 5 seconds
    assert duration < 5.0
```

## Additional Resources

- [DOCKER_TESTING_QUICKSTART.md](DOCKER_TESTING_QUICKSTART.md) - Quick reference
- [DOCKER_TESTING_PLAN.md](DOCKER_TESTING_PLAN.md) - Implementation plan
- [pytest documentation](https://docs.pytest.org/)
- [Docker Compose documentation](https://docs.docker.com/compose/)

## Getting Help

- Check existing tests for examples
- Review fixture implementations in `conftest.py`
- Ask in GitHub Discussions
- Report issues on GitHub Issues
