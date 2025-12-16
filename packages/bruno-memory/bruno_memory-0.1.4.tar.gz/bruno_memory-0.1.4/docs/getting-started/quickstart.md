# Quick Start

Get started with bruno-memory in just a few minutes!

## Installation

=== "Basic"
    ```bash
    pip install bruno-memory
    ```

=== "With PostgreSQL"
    ```bash
    pip install bruno-memory[postgresql]
    ```

=== "With Vector Search"
    ```bash
    pip install bruno-memory[chromadb]
    # or
    pip install bruno-memory[qdrant]
    ```

=== "All Backends"
    ```bash
    pip install bruno-memory[all]
    ```

## Basic Usage

### 1. Create a Backend

```python
from bruno_memory import create_backend

# In-memory SQLite (development)
backend = create_backend("sqlite", database_path=":memory:")

# File-based SQLite (production)
backend = create_backend("sqlite", database_path="./memory.db")

# PostgreSQL (enterprise)
backend = create_backend(
    "postgresql",
    connection_string="postgresql://user:pass@localhost/db"
)
```

### 2. Store Messages

```python
import asyncio
from bruno_core.models import Message, MessageRole, MessageType

async def store_conversation():
    backend = create_backend("sqlite", database_path="chat.db")
    await backend.connect()
    
    # Create messages
    messages = [
        Message(
            content="Hello! I need help with Python.",
            role=MessageRole.USER,
            message_type=MessageType.TEXT
        ),
        Message(
            content="I'd be happy to help! What would you like to know?",
            role=MessageRole.ASSISTANT,
            message_type=MessageType.TEXT
        )
    ]
    
    # Store them
    for msg in messages:
        await backend.store_message(msg)
    
    print(f"Stored {len(messages)} messages")
    await backend.disconnect()

asyncio.run(store_conversation())
```

### 3. Retrieve Conversation History

```python
async def get_history():
    backend = create_backend("sqlite", database_path="chat.db")
    await backend.connect()
    
    # Get last 10 messages
    messages = await backend.retrieve_messages(limit=10)
    
    for msg in messages:
        print(f"{msg.role.value}: {msg.content}")
    
    # Get messages from specific conversation
    messages = await backend.retrieve_messages(
        conversation_id="conv-123",
        limit=50
    )
    
    await backend.disconnect()

asyncio.run(get_history())
```

## Environment Configuration

Create a `.env` file:

```env
# Backend selection
BRUNO_MEMORY_BACKEND=sqlite

# SQLite configuration
BRUNO_MEMORY_SQLITE_DATABASE_PATH=./memory.db
BRUNO_MEMORY_SQLITE_ENABLE_FTS=true

# PostgreSQL configuration (if using PostgreSQL)
# BRUNO_MEMORY_POSTGRESQL_CONNECTION_STRING=postgresql://user:pass@localhost/db
```

Then load from environment:

```python
from bruno_memory import create_from_env

# Automatically loads from .env
backend = create_from_env()
await backend.connect()
```

## Using with bruno-core

bruno-memory integrates seamlessly with bruno-core:

```python
from bruno_core import BaseAssistant
from bruno_memory import create_backend

class MyAssistant(BaseAssistant):
    def __init__(self):
        super().__init__(
            name="my-assistant",
            model="gpt-4"
        )
        # Initialize memory backend
        self.memory = create_backend("sqlite", database_path="assistant.db")
    
    async def process_message(self, content: str) -> str:
        # Store user message
        user_msg = Message(
            content=content,
            role=MessageRole.USER,
            message_type=MessageType.TEXT
        )
        await self.memory.store_message(user_msg)
        
        # Get conversation context
        history = await self.memory.retrieve_messages(limit=10)
        
        # Generate response (using LLM)
        response = await self.generate_response(history)
        
        # Store assistant message
        assistant_msg = Message(
            content=response,
            role=MessageRole.ASSISTANT,
            message_type=MessageType.TEXT
        )
        await self.memory.store_message(assistant_msg)
        
        return response
```

## Next Steps

- **[Backend Selection](../guide/backends.md)**: Choose the right backend for your needs
- **[Context Management](../guide/context.md)**: Build intelligent conversation context
- **[Semantic Search](../guide/semantic-search.md)**: Add vector search for RAG
- **[Caching](../guide/caching.md)**: Optimize performance with caching
- **[Examples](../examples/basic.md)**: More detailed examples

## Common Patterns

### Fallback Chain

Try backends in order until one succeeds:

```python
from bruno_memory import create_with_fallback

# Try Redis first, fallback to SQLite
backend = create_with_fallback(
    ["redis", "sqlite"],
    database_path="fallback.db"  # Used by SQLite
)
```

### Multi-Level Caching

```python
from bruno_memory.utils import MultiLevelCache, InMemoryCache, RedisCache

# L1: In-memory, L2: Redis
cache = MultiLevelCache(
    l1_cache=InMemoryCache(max_size=100),
    l2_cache=RedisCache(host="localhost")
)

await cache.set("key", "value", ttl=300)
value = await cache.get("key")  # Checks L1 first, then L2
```

### Backup and Export

```python
from bruno_memory.utils import BackupExporter

exporter = BackupExporter(output_dir="./backups")

# Export to JSON
messages = await backend.retrieve_messages(limit=1000)
exporter.export_messages_to_json(messages)

# Export to Excel
exporter.export_messages_to_excel(messages)
```

## Troubleshooting

### Connection Issues

If you encounter connection issues:

```python
# Check backend health
healthy = await backend.health_check()
if not healthy:
    print("Backend not healthy!")

# Get connection statistics
stats = await backend.get_statistics()
print(f"Active connections: {stats.get('connections', 0)}")
```

### Performance

For production workloads:

```python
# Enable connection pooling
backend = create_backend(
    "postgresql",
    connection_string="postgresql://...",
    pool_size=20,
    max_overflow=10
)

# Use batch operations
await backend.store_messages_batch(messages)  # Faster than individual stores
```

## Need Help?

- 📖 [User Guide](../guide/backends.md) - Comprehensive guides
- 🔍 [API Reference](../api/factory.md) - Detailed API docs
- 💬 [GitHub Issues](https://github.com/meggy-ai/bruno-memory/issues) - Report bugs or ask questions
- 🤝 [Contributing](../development/contributing.md) - Help improve bruno-memory
