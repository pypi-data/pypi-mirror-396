# Backend Selection Guide

Choose the right backend for your use case.

## Decision Tree

```mermaid
graph TD
    A[Start] --> B{What's your primary need?}
    B -->|Simple/Development| C[SQLite]
    B -->|Production Scale| D{Need Vector Search?}
    B -->|High Performance Cache| E[Redis]
    B -->|Semantic Search/RAG| F{Which Vector DB?}
    
    D -->|Yes| F
    D -->|No| G[PostgreSQL]
    
    F -->|Ease of Use| H[ChromaDB]
    F -->|Performance/Scale| I[Qdrant]
    
    C --> J[✅ SQLite Backend]
    E --> K[✅ Redis Backend]
    G --> L[✅ PostgreSQL Backend]
    H --> M[✅ ChromaDB Backend]
    I --> N[✅ Qdrant Backend]
```

## SQLite

**Best for:** Development, small applications, embedded systems

### Pros
- ✅ Zero configuration
- ✅ File-based or in-memory
- ✅ Full-text search support
- ✅ Perfect for development
- ✅ No separate server needed

### Cons
- ❌ Limited concurrency
- ❌ No distributed support
- ❌ No vector search
- ❌ Not ideal for high-traffic production

### Usage

```python
from bruno_memory import create_backend

# In-memory (fastest, for testing)
backend = create_backend("sqlite", database_path=":memory:")

# File-based (persistent)
backend = create_backend(
    "sqlite",
    database_path="./memory.db",
    enable_fts=True  # Enable full-text search
)
```

### When to Use
- Local development
- Single-user applications
- Embedded applications
- Testing
- POC/prototypes

## PostgreSQL

**Best for:** Production applications, multi-user systems, enterprise

### Pros
- ✅ Excellent performance at scale
- ✅ ACID compliance
- ✅ Connection pooling
- ✅ Full-text search
- ✅ Concurrent access
- ✅ Proven reliability

### Cons
- ❌ Requires separate server
- ❌ More complex setup
- ❌ No built-in vector search
- ❌ Higher resource usage

### Usage

```python
from bruno_memory import create_backend

backend = create_backend(
    "postgresql",
    connection_string="postgresql://user:pass@localhost:5432/memory",
    pool_size=20,  # Connection pool
    enable_fts=True
)
```

### When to Use
- Production applications
- Multi-user systems
- High-traffic scenarios
- When you need reliability
- Enterprise deployments

### Docker Setup

```bash
# Run PostgreSQL in Docker
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=memory \
  -p 5432:5432 \
  postgres:15
```

## Redis

**Best for:** High-performance caching, session storage, temporary data

### Pros
- ✅ Extremely fast (in-memory)
- ✅ TTL support
- ✅ Distributed caching
- ✅ Pub/sub capabilities
- ✅ Perfect for session data

### Cons
- ❌ Memory-only (ephemeral)
- ❌ Not for primary storage
- ❌ No complex queries
- ❌ Limited search capabilities

### Usage

```python
from bruno_memory import create_backend

backend = create_backend(
    "redis",
    host="localhost",
    port=6379,
    db=0,
    ttl=3600  # Default TTL: 1 hour
)
```

### When to Use
- Caching layer
- Session storage
- Temporary conversation state
- Rate limiting
- Real-time features

### Docker Setup

```bash
# Run Redis in Docker
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7
```

## ChromaDB

**Best for:** RAG applications, semantic search, local vector search

### Pros
- ✅ Easy setup
- ✅ Built for embeddings
- ✅ Excellent for RAG
- ✅ Local or client-server
- ✅ Good Python integration

### Cons
- ❌ Newer/less mature
- ❌ Limited at massive scale
- ❌ No full-text search
- ❌ Python-centric

### Usage

```python
from bruno_memory import create_backend

# Local mode
backend = create_backend(
    "chromadb",
    persist_directory="./chroma_db",
    embedding_function="text-embedding-3-small"
)

# Client-server mode
backend = create_backend(
    "chromadb",
    host="localhost",
    port=8000,
    embedding_function="text-embedding-3-small"
)
```

### When to Use
- RAG applications
- Semantic search
- Local vector search
- Development with vectors
- Quick prototyping

### Docker Setup

```bash
# Run ChromaDB in Docker
docker run -d \
  --name chromadb \
  -p 8000:8000 \
  -v ./chroma_data:/chroma/chroma \
  chromadb/chroma:latest
```

## Qdrant

**Best for:** Production vector search, large-scale RAG, high performance

### Pros
- ✅ Highly scalable
- ✅ Excellent performance
- ✅ Rich filtering
- ✅ Production-ready
- ✅ Cloud and self-hosted

### Cons
- ❌ More complex setup
- ❌ Requires separate server
- ❌ No full-text search
- ❌ Steeper learning curve

### Usage

```python
from bruno_memory import create_backend

backend = create_backend(
    "qdrant",
    host="localhost",
    port=6333,
    collection_name="bruno_memory",
    embedding_function="text-embedding-3-small"
)
```

### When to Use
- Production RAG systems
- Large-scale vector search
- High-performance requirements
- When you need advanced filtering
- Cloud-native deployments

### Docker Setup

```bash
# Run Qdrant in Docker
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v ./qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

## Hybrid Approaches

### SQLite + ChromaDB

```python
from bruno_memory import create_backend

# SQLite for structured data
structured = create_backend("sqlite", database_path="./data.db")

# ChromaDB for vectors
vectors = create_backend(
    "chromadb",
    persist_directory="./vectors",
    embedding_function="text-embedding-3-small"
)

# Use both together
await structured.store_message(message)
await vectors.store_memory(memory_with_embedding)
```

### PostgreSQL + Qdrant

```python
# PostgreSQL for primary storage
primary = create_backend(
    "postgresql",
    connection_string="postgresql://..."
)

# Qdrant for semantic search
semantic = create_backend(
    "qdrant",
    host="localhost",
    port=6333
)

# Store in both
await primary.store_message(message)
if message.embedding:
    await semantic.store_memory(memory_from_message)
```

### Redis + PostgreSQL (with Fallback)

```python
from bruno_memory import create_with_fallback

# Try Redis (fast), fallback to PostgreSQL
backend = create_with_fallback(
    ["redis", "postgresql"],
    host="localhost",  # Used by Redis
    connection_string="postgresql://..."  # Used by PostgreSQL
)
```

## Comparison Table

| Feature | SQLite | PostgreSQL | Redis | ChromaDB | Qdrant |
|---------|--------|------------|-------|----------|--------|
| **Setup Complexity** | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Scalability** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Concurrency** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Persistence** | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| **Vector Search** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Full-Text Search** | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| **Resource Usage** | Low | Medium | Medium | Medium | Medium-High |
| **Maintenance** | None | Medium | Low | Low | Medium |

Legend:
- ⭐ = Fewer stars = easier/lighter
- ✅ = Supported
- ❌ = Not supported
- ⚠️ = Limited support

## Migration Path

Typical progression:

```mermaid
graph LR
    A[SQLite<br/>Development] --> B[PostgreSQL<br/>Production]
    B --> C[+ Redis<br/>Caching]
    C --> D[+ Qdrant<br/>RAG/Semantic]
```

## Recommendations by Use Case

### Personal Assistant
- **Start:** SQLite
- **Scale:** PostgreSQL
- **+ Semantic:** ChromaDB

### Enterprise Chatbot
- **Primary:** PostgreSQL
- **Cache:** Redis
- **Semantic:** Qdrant

### RAG Application
- **Primary:** Qdrant or ChromaDB
- **Metadata:** PostgreSQL (optional)

### Multi-Tenant SaaS
- **Primary:** PostgreSQL (with tenant isolation)
- **Cache:** Redis (with tenant prefixes)
- **Semantic:** Qdrant (with tenant collections)

## Next Steps

- [Quick Start](../getting-started/quickstart.md) - Get started with your chosen backend
- [Configuration](../getting-started/configuration.md) - Configure your backend
- [Performance Tuning](performance.md) - Optimize for your use case
- [API Reference](../api/factory.md) - Detailed backend APIs
