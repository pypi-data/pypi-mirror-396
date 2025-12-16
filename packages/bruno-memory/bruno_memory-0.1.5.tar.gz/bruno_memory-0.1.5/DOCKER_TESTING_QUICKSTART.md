# Docker Testing Infrastructure - Quick Start Guide

## Overview

Complete Docker-based testing infrastructure for bruno-memory with support for PostgreSQL, Redis, ChromaDB, and Qdrant backends.

## Quick Start

### 1. Start All Services

```bash
# PowerShell
.\scripts\setup-test-env.ps1

# Bash
bash scripts/setup-test-env.sh
```

### 2. Run Tests

```bash
# Using Makefile
make test-docker

# Using script directly (PowerShell)
.\scripts\run-tests-docker.ps1

# Using script directly (Bash)
bash scripts/run-tests-docker.sh
```

### 3. Stop Services

```bash
# PowerShell
.\scripts\teardown-test-env.ps1

# Bash
bash scripts/teardown-test-env.sh
```

## Available Profiles

### Minimal Profile
- PostgreSQL + Redis only
- Fastest startup
- For basic backend testing

```bash
.\scripts\setup-test-env.ps1 -Profile minimal
make test-docker-minimal
```

### Full Profile (Default)
- All services: PostgreSQL, Redis, ChromaDB, Qdrant
- Complete testing environment
- Recommended for comprehensive testing

```bash
.\scripts\setup-test-env.ps1 -Profile full
make test-docker
```

### CI Profile
- Optimized for CI/CD
- Uses tmpfs for faster I/O
- No persistent volumes

```bash
.\scripts\setup-test-env.ps1 -Profile ci
```

## Makefile Targets

### Service Management
- `make docker-up` - Start all services
- `make docker-down` - Stop services (preserve data)
- `make docker-down-volumes` - Stop and remove data
- `make docker-logs` - View service logs
- `make docker-status` - Show container status

### Running Tests
- `make test-docker` - Run all tests with full environment
- `make test-docker-minimal` - Run with minimal services
- `make test-docker-keep` - Run tests but keep environment running

### Backend-Specific Tests
- `make test-postgresql` - Test PostgreSQL backend only
- `make test-redis` - Test Redis backend only
- `make test-chromadb` - Test ChromaDB backend only
- `make test-qdrant` - Test Qdrant backend only
- `make test-vector` - Test all vector backends

### Environment Management
- `make docker-setup` - Setup environment manually
- `make docker-teardown` - Complete cleanup with volumes

## Script Options

### setup-test-env

```powershell
# PowerShell
.\scripts\setup-test-env.ps1 `
    -Profile <minimal|full|ci> `
    -Pull `           # Pull latest images
    -Build `          # Rebuild custom images
    -Clean            # Remove existing containers first
```

```bash
# Bash
bash scripts/setup-test-env.sh \
    --profile <minimal|full|ci> \
    --pull \          # Pull latest images
    --build \         # Rebuild custom images
    --clean           # Remove existing containers first
```

### run-tests-docker

```powershell
# PowerShell
.\scripts\run-tests-docker.ps1 `
    -Profile <minimal|full|ci> `
    -Markers @("postgresql", "redis") `
    -TestPath "tests/unit/" `
    -Verbose `
    -NoCoverage `
    -KeepEnv `        # Don't stop containers after tests
    -SetupOnly        # Only setup, don't run tests
```

```bash
# Bash
bash scripts/run-tests-docker.sh \
    --profile <minimal|full|ci> \
    --markers "postgresql,redis" \
    --test-path "tests/unit/" \
    --verbose \
    --no-coverage \
    --keep-env \      # Don't stop containers after tests
    --setup-only      # Only setup, don't run tests
```

### teardown-test-env

```powershell
# PowerShell
.\scripts\teardown-test-env.ps1 `
    -Profile <minimal|full|ci|all> `
    -Volumes `        # Remove data volumes
    -Force            # Force remove containers
```

```bash
# Bash
bash scripts/teardown-test-env.sh \
    --profile <minimal|full|ci|all> \
    --volumes \       # Remove data volumes
    --force           # Force remove containers
```

## Service Configuration

### Environment Variables

All services use environment variables from `.env` file or defaults:

```env
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
REDIS_PASSWORD=

# ChromaDB
CHROMA_HOST=localhost
CHROMA_HTTP_PORT=8000

# Qdrant
QDRANT_HOST=localhost
QDRANT_HTTP_PORT=6333
QDRANT_GRPC_PORT=6334
```

### Service Ports

- PostgreSQL: `5432`
- Redis: `6379`
- ChromaDB: `8000`
- Qdrant HTTP: `6333`
- Qdrant gRPC: `6334`

## Testing with Pytest Markers

The test infrastructure uses pytest markers for backend-specific tests:

```python
# Run only PostgreSQL tests
pytest -m postgresql

# Run only vector database tests
pytest -m vector

# Run multiple backends
pytest -m "postgresql or redis"

# Exclude specific backends
pytest -m "not chromadb"
```

Available markers:
- `postgresql` - PostgreSQL backend tests
- `redis` - Redis backend tests
- `chromadb` - ChromaDB vector backend tests
- `qdrant` - Qdrant vector backend tests
- `vector` - All vector database tests
- `requires_docker` - Tests requiring Docker services

## Test Fixtures

Docker backend fixtures are automatically available in tests:

```python
async def test_postgresql(postgresql_backend):
    """Test with PostgreSQL backend."""
    await postgresql_backend.store_message(message)
    # ...

async def test_redis(redis_backend):
    """Test with Redis backend."""
    await redis_backend.cache_set("key", "value")
    # ...

async def test_chromadb(chromadb_backend):
    """Test with ChromaDB vector backend."""
    await chromadb_backend.add_vectors(vectors)
    # ...

async def test_qdrant(qdrant_backend):
    """Test with Qdrant vector backend."""
    results = await qdrant_backend.search(query_vector)
    # ...
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker ps

# Check compose file syntax
docker-compose config

# View service logs
docker-compose logs <service>
```

### Services Not Ready

```bash
# Manually check service readiness
.\scripts\wait-for-services.ps1 -Services @("postgresql", "redis")

# Increase timeout
.\scripts\wait-for-services.ps1 -TimeoutSeconds 300
```

### Port Conflicts

```bash
# Check which ports are in use
netstat -an | findstr "5432 6379 8000 6333"

# Change ports in .env file
# Then restart services
docker-compose down
docker-compose up -d
```

### Clean Slate

```bash
# Complete cleanup
make docker-teardown

# Or manually
docker-compose down -v
docker volume prune -f
```

## Connection Testing

Individual connection test scripts are available:

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

## Development Workflow

### Typical Development Session

```bash
# 1. Start services
make docker-up

# 2. Develop and test iteratively
pytest tests/unit/test_my_feature.py -v

# 3. Run full test suite before commit
make test-docker

# 4. Cleanup
make docker-down
```

### Testing Specific Backend

```bash
# Test only PostgreSQL changes
make test-postgresql

# Keep environment running for multiple test runs
.\scripts\run-tests-docker.ps1 -KeepEnv -TestPath "tests/unit/test_postgresql_backend.py"

# Run tests again (services still running)
pytest tests/unit/test_postgresql_backend.py -v

# Cleanup when done
make docker-down
```

## CI/CD Integration

The infrastructure is CI/CD ready:

```yaml
# Example GitHub Actions workflow
- name: Setup Docker services
  run: bash scripts/setup-test-env.sh --profile ci

- name: Run tests
  run: bash scripts/run-tests-docker.sh --profile ci --no-coverage

- name: Cleanup
  run: bash scripts/teardown-test-env.sh --profile ci --volumes
```

## Files Created

### Scripts (PowerShell & Bash)
- `scripts/setup-test-env.ps1` / `.sh` - Environment setup
- `scripts/teardown-test-env.ps1` / `.sh` - Environment cleanup
- `scripts/run-tests-docker.ps1` / `.sh` - Test runner
- `scripts/wait-for-services.ps1` / `.sh` - Service readiness checker
- `scripts/test-postgres-connection.ps1` / `.sh` - PostgreSQL connection test
- `scripts/test-redis-connection.ps1` / `.sh` - Redis connection test
- `scripts/test-chromadb-connection.ps1` / `.sh` - ChromaDB connection test
- `scripts/test-qdrant-connection.ps1` / `.sh` - Qdrant connection test

### Docker Configuration
- `docker-compose.yml` - Main compose file (all services)
- `docker-compose.minimal.yml` - Minimal services (PostgreSQL + Redis)
- `docker-compose.ci.yml` - CI-optimized configuration
- `docker-compose.dev.yml` - Development with web UIs
- `docker/postgresql/Dockerfile` - Custom PostgreSQL with pgvector
- `docker/postgresql/init.sql` - Database schema
- `docker/redis/redis.conf` - Redis configuration
- `docker/qdrant/config.dev.yaml` - Qdrant configuration

### Test Configuration
- `tests/conftest.py` - Docker backend fixtures
- `pyproject.toml` - Updated with test markers
- `Makefile` - 14+ new Docker test targets

## Next Steps

See [DOCKER_TESTING_PLAN.md](DOCKER_TESTING_PLAN.md) for the complete implementation plan and Phase 6 (CI/CD & Documentation) details.
