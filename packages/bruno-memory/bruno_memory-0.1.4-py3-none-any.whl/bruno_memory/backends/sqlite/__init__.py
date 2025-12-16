"""
SQLite backend for bruno-memory.

Provides a high-performance, file-based memory storage solution
with full-text search and ACID compliance.
"""

from .backend import SQLiteMemoryBackend
from .schema import SCHEMA_VERSION, get_full_schema_sql

__all__ = ["SQLiteMemoryBackend", "get_full_schema_sql", "SCHEMA_VERSION"]
