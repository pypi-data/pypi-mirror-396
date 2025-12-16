"""
Example demonstrating bruno-memory factory features.

Shows how to use:
- Backend creation with auto-discovery
- Environment variable configuration  
- Fallback chain support
- Multiple backend instances
"""

import os
import asyncio
from bruno_memory import (
    create_backend,
    create_from_env,
    create_with_fallback,
    list_backends,
)


async def example_basic_creation():
    """Example 1: Basic backend creation."""
    print("=== Example 1: Basic Backend Creation ===")
    
    # List available backends
    backends = list_backends()
    print(f"Available backends: {list(backends.keys())}")
    
    # Create SQLite backend with explicit config
    backend = create_backend(
        "sqlite",
        database_path=":memory:",
        enable_fts=True
    )
    
    await backend.connect()
    print(f"Created {backend.__class__.__name__}")
    await backend.disconnect()


async def example_env_configuration():
    """Example 2: Configuration from environment variables."""
    print("\n=== Example 2: Environment Configuration ===")
    
    # Set environment variables
    os.environ["BRUNO_MEMORY_BACKEND"] = "sqlite"
    os.environ["BRUNO_MEMORY_SQLITE_DATABASE_PATH"] = ":memory:"
    os.environ["BRUNO_MEMORY_SQLITE_ENABLE_FTS"] = "true"
    
    # Create backend from environment
    backend = create_from_env()
    
    await backend.connect()
    print(f"Created {backend.__class__.__name__} from environment")
    print(f"Database: {backend.config.database_path}")
    await backend.disconnect()


async def example_fallback_chain():
    """Example 3: Fallback chain for resilience."""
    print("\n=== Example 3: Fallback Chain ===")
    
    # Try backends in order: redis -> sqlite (fallback)
    # Redis will fail (not configured), SQLite will succeed
    backend = create_with_fallback(
        ["redis", "sqlite"],
        database_path=":memory:"  # Used by SQLite fallback
    )
    
    await backend.connect()
    print(f"Created {backend.__class__.__name__} using fallback chain")
    await backend.disconnect()


async def example_multiple_backends():
    """Example 4: Using multiple backends simultaneously."""
    print("\n=== Example 4: Multiple Backends ===")
    
    # Create different backends for different purposes
    persistent = create_backend(
        "sqlite",
        database_path="./memory.db"
    )
    
    in_memory = create_backend(
        "sqlite", 
        database_path=":memory:"
    )
    
    await persistent.connect()
    await in_memory.connect()
    
    print(f"Persistent: {persistent.__class__.__name__}")
    print(f"In-memory: {in_memory.__class__.__name__}")
    
    await persistent.disconnect()
    await in_memory.disconnect()


async def example_dotenv_integration():
    """Example 5: Using .env file for configuration."""
    print("\n=== Example 5: .env File Integration ===")
    
    # Create .env file example
    env_content = """
# bruno-memory configuration
BRUNO_MEMORY_BACKEND=sqlite
BRUNO_MEMORY_SQLITE_DATABASE_PATH=./app.db
BRUNO_MEMORY_SQLITE_ENABLE_FTS=true
BRUNO_MEMORY_SQLITE_POOL_SIZE=10
"""
    
    print("Example .env file content:")
    print(env_content)
    
    # Factory automatically loads .env on initialization
    # python-dotenv library is used for this
    print("\nFactory will automatically load these settings!")


async def main():
    """Run all examples."""
    print("bruno-memory Factory Examples\n")
    print("=" * 60)
    
    await example_basic_creation()
    await example_env_configuration()
    await example_fallback_chain()
    await example_multiple_backends()
    await example_dotenv_integration()
    
    print("\n" + "=" * 60)
    print("Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
