# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

## [0.1.0] - YYYY-MM-DD

### Added
- Initial release
- Core memory management functionality
- Multiple backend support
- Embedding integration
- Basic documentation

---

## Release Process

1. Update version in `pyproject.toml` and `bruno_memory/__init__.py`
2. Update this CHANGELOG with release date and changes
3. Commit changes: `git commit -am "Release v0.1.0"`
4. Create tag: `git tag -a v0.1.0 -m "Release version 0.1.0"`
5. Push: `git push origin main --tags`
6. GitHub Actions will automatically publish to PyPI

## Version Policy

- **Major** (X.0.0): Breaking API changes
- **Minor** (0.X.0): New features, backwards compatible
- **Patch** (0.0.X): Bug fixes, backwards compatible

## Migration Guides

### Migrating from 0.0.x to 0.1.x

[Migration guide will be added here when releasing 0.1.0]
