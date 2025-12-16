"""
Redis backend for bruno-memory.

Provides high-performance caching and session management with TTL support.
"""

from .backend import RedisMemoryBackend

__all__ = ["RedisMemoryBackend"]
