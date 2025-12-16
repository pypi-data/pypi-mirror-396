# Docker Directory Structure
# This directory contains Docker configuration files for bruno-memory services

## Structure

```
docker/
├── postgresql/         # PostgreSQL with pgvector extension
│   ├── Dockerfile      # Custom PostgreSQL image
│   ├── init.sql        # Database initialization
│   ├── setup-schema.sh # Schema creation script
│   ├── postgresql.dev.conf  # Dev PostgreSQL config
│   ├── servers.json    # pgAdmin server definitions
│   └── dev-queries.sql # Useful development queries
│
├── redis/              # Redis configuration
│   └── redis.conf      # Redis server configuration
│
└── qdrant/             # Qdrant configuration
    └── config.dev.yaml # Qdrant development config
```

## Services

### PostgreSQL
- Base image: `postgres:16-alpine`
- Extensions: `pgvector` for vector operations
- Port: 5432
- Database: `bruno_memory_test` (or `bruno_memory_dev` for dev)

### Redis
- Base image: `redis:7-alpine`
- Port: 6379
- Persistence: AOF (optional)

### ChromaDB
- Base image: `chromadb/chroma:latest`
- Port: 8000
- Persistence: Configured via volumes

### Qdrant
- Base image: `qdrant/qdrant:latest`
- Ports: 6333 (HTTP), 6334 (gRPC)
- Persistence: Configured via volumes

## Configuration Files

All configuration files in this directory are used by Docker Compose to set up the testing environment. See individual subdirectories for service-specific documentation.
