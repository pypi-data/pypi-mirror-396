# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5] - 2025-12-12

### Added
- Docker Compose infrastructure for local development and testing
  - PostgreSQL 16 with pgvector extension
  - Redis 7.4.7 for caching
  - ChromaDB for vector storage
  - Qdrant v1.16.2 for vector search
- Docker profiles (main, minimal, ci, dev) for different use cases
- Comprehensive testing documentation (TESTING.md, DOCKER_TESTING_QUICKSTART.md)
- GitHub Actions workflow for CI/CD with Docker service containers
- Matrix testing across Python 3.10-3.12 with all backend services

### Fixed
- **PostgreSQL Backend**:
  - JSONB column data parsing - added json.loads() for metadata, state, and context fields
  - UUID to string conversions for conversation_id and session_id in MemoryEntry and SessionContext
  - ConversationContext now properly returns UserContext and SessionContext objects
  - Memory expires_at field now correctly stored and retrieved as top-level field
  - Message and memory retrieval metadata parsing for JSON string format
- **Redis Backend**:
  - SessionContext UUID validation - now correctly returns string UUIDs
  - ConversationContext object creation with proper UserContext and SessionContext instances
- **Test Suite**:
  - Float precision comparisons for PostgreSQL REAL type (importance/confidence fields)
  - Foreign key constraint violations - added user_contexts creation in 5 tests
  - UUID fixture in sample_memory_entry to use string format
  - Conversation context assertions to access nested user object
  - Memory expiration test to use timezone-aware datetimes and correct field placement
  - SQLite memory query filtering test ID assertions

### Changed
- Test coverage improved from 73% to 74%
- All 269 tests now pass successfully (down from 35 failures)
- PostgreSQL backend retrieve_memories and search_memories methods enhanced with proper JSON parsing
- Test fixtures updated to respect database foreign key constraints

### Documentation
- Added detailed Docker testing guide with quickstart instructions
- Updated CONTRIBUTING.md with Docker testing workflow
- Enhanced README.md with Docker Compose usage examples
- Added troubleshooting section for Docker-related issues

## [0.1.4] - 2025-12-11

### Fixed
- Re-release to fix PyPI publication after accidental deletion of v0.1.2

## [0.1.3] - 2025-12-11

### Changed
- Simplified CI/CD workflows for easier maintenance
- Removed complex release and dependency monitoring workflows
- Streamlined CI to test on Ubuntu + Windows with Python 3.11-3.12 only
- Consolidated lint workflow to single job
- Moved documentation deployment to publish workflow

### Removed
- macOS testing from CI (can be added back later)
- Python 3.10 support (minimum now 3.11)
- Backend integration tests with PostgreSQL and Redis services
- Separate documentation build job in CI
- Dependency monitoring workflow
- Complex release workflow with automatic changelog generation

## [0.1.1] - 2025-12-11

### Changed
- Simplified publish workflow to single job triggered by GitHub releases
- Removed separate TestPyPI and manual workflow dispatch options
- Updated to Python 3.11 for publishing
- Streamlined workflow from 88 lines to 35 lines

### Added
- Initial project structure
- SQLite backend implementation
- PostgreSQL backend with vector support
- Redis backend for caching
- ChromaDB and Qdrant vector database backends
- Embedding management system
- Context building and retrieval
- Memory compression utilities
- Analytics and reporting
- Backup and restore functionality
- Caching layer with TTL and LRU
- Advanced memory prioritization with multi-factor scoring
- Privacy and security features (encryption, anonymization, GDPR)
- Performance monitoring and optimization tools
- Comprehensive documentation with MkDocs
- CI/CD pipeline with GitHub Actions
- Automated testing across Python 3.10, 3.11, 3.12
- Code quality tools (black, ruff, mypy)
- Security scanning and dependency auditing
- Git-based version management with bump_version.py script

### Changed

### Deprecated

### Removed

### Fixed

### Security
