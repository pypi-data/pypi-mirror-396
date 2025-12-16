# Changelog

All notable changes to bruno-memory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of bruno-memory
- Multi-backend support (SQLite, PostgreSQL, Redis, ChromaDB, Qdrant)
- Factory pattern for backend creation
- Environment-based configuration
- Fallback chain support
- Entry point discovery for plugin backends
- Multi-level caching system (InMemoryCache, RedisCache, MultiLevelCache)
- Backup and export utilities (JSON, CSV, Excel)
- Analytics and performance tracking
- Conversation management
- Context building
- Memory retrieval
- Semantic search with vector backends
- Comprehensive test suite (>90% coverage)
- Complete API documentation
- User guides and examples

### Features

#### Backends
- **SQLite**: Lightweight, file-based storage with FTS support
- **PostgreSQL**: Enterprise-grade relational storage
- **Redis**: High-performance caching and session storage
- **ChromaDB**: Vector search for semantic similarity
- **Qdrant**: Production-grade vector search at scale

#### Managers
- **ConversationManager**: Manage conversation threads
- **ContextBuilder**: Build intelligent conversation context
- **MemoryRetriever**: Retrieve and search memories
- **EmbeddingManager**: Generate and manage embeddings
- **MemoryCompressor**: Compress and summarize conversations

#### Utilities
- **Cache**: Multi-level caching with LRU and TTL
- **Backup**: Export to JSON, CSV, Excel formats
- **Analytics**: Conversation patterns and usage metrics

#### Developer Experience
- Type-safe with full type hints
- Pydantic validation
- Async/await support
- Comprehensive documentation
- Plugin architecture
- Testing utilities

## [0.1.0] - Initial Development

### Added
- Core architecture and base classes
- Initial backend implementations
- Basic documentation

---

## Release Notes Template

```markdown
## [VERSION] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements
```

---

[Unreleased]: https://github.com/meggy-ai/bruno-memory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/meggy-ai/bruno-memory/releases/tag/v0.1.0
