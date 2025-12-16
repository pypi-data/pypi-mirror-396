# CI/CD Implementation Guide

This document describes the CI/CD infrastructure for bruno-memory.

## Overview

The project uses GitHub Actions for continuous integration, testing, and deployment. The workflow is designed to ensure code quality, security, and reliable releases.

## Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Trigger**: Push to main/develop, Pull Requests

**Jobs**:
- **Test Matrix**: 
  - Python versions: 3.10, 3.11, 3.12
  - Operating systems: Ubuntu, Windows, macOS
  - Runs full test suite with coverage reporting
  
- **Backend Integration Tests**:
  - PostgreSQL 16 + Redis 7 services
  - Tests backend-specific functionality
  
- **Documentation Build**:
  - Validates MkDocs can build successfully
  - Uploads docs artifact

**Coverage**: Uploads to Codecov for tracking

### 2. Lint Workflow (`.github/workflows/lint.yml`)

**Trigger**: Push to main/develop, Pull Requests

**Checks**:
- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **Mypy**: Type checking (continue on error)
- **Bandit**: Security scanning (continue on error)

### 3. Publish Workflow (`.github/workflows/publish.yml`)

**Trigger**: 
- Release published (automatic to PyPI)
- Manual dispatch (choose TestPyPI or PyPI)

**Process**:
1. Build distribution packages (wheel + sdist)
2. Validate with twine
3. Publish to PyPI using trusted publishing (OIDC)

**Requirements**:
- Configure PyPI trusted publisher
- Set up GitHub environments (testpypi, pypi)

### 4. Release Workflow (`.github/workflows/release.yml`)

**Trigger**: Git tag push (v*.*.*)

**Process**:
1. Generate changelog from commits
2. Build distribution packages
3. Create GitHub Release with artifacts
4. Deploy documentation to GitHub Pages
5. Announcement placeholder

### 5. Dependency Check (`.github/workflows/dependencies.yml`)

**Trigger**: 
- Weekly schedule (Monday 9 AM UTC)
- Pull requests touching dependencies
- Manual dispatch

**Checks**:
- **pip-audit**: Security vulnerabilities in dependencies
- **Dependency Review**: GitHub's dependency review action
- **Outdated Packages**: Creates issues for updates

## Configuration Files

### codecov.yml

**Coverage Targets**:
- Project: 60% (threshold: 1%)
- Patch: 70% (threshold: 5%)

**Components**:
- Backends
- Managers
- Utils

### .pre-commit-config.yaml

**Pre-commit Hooks**:
- Trailing whitespace, EOF fixes
- YAML/JSON/TOML validation
- Black formatting
- Ruff linting
- Mypy type checking
- Bandit security scanning
- Markdown formatting

**Setup**:
```bash
pip install pre-commit
pre-commit install
```

### pyproject.toml

**Tool Configurations**:
- **Black**: 100 char line length
- **Ruff**: E, W, F, I, B, C4, UP, ARG, SIM rules
- **Mypy**: Strict mode with third-party ignores
- **Pytest**: Coverage reporting, markers
- **Coverage**: Exclude patterns

## Makefile Commands

Quick access to common tasks:

```bash
make install-dev    # Install with dev dependencies
make test          # Run tests with coverage
make test-fast     # Skip slow backend tests
make lint          # Check code quality
make format        # Auto-format code
make type-check    # Run mypy
make docs          # Build documentation
make docs-serve    # Serve docs locally
make build         # Build distribution
make publish       # Publish to PyPI
make bump-patch    # Bump patch version
make bump-minor    # Bump minor version
make bump-major    # Bump major version
```

## Version Bumping

### Automated Script (`scripts/bump_version.py`)

```bash
# Bump version and create git tag
python scripts/bump_version.py patch  # 0.1.0 -> 0.1.1
python scripts/bump_version.py minor  # 0.1.0 -> 0.2.0
python scripts/bump_version.py major  # 0.1.0 -> 1.0.0

# Options
--dry-run       # Show what would happen
--no-commit     # Don't create git commit
--no-tag        # Don't create git tag
```

**Updates**:
- `pyproject.toml` version
- `bruno_memory/__init__.py` __version__
- Creates git commit and tag

## GitHub Setup Requirements

### 1. Repository Settings

**Secrets** (not needed with OIDC):
- None required for trusted publishing

**Environments**:
- `testpypi`: For testing releases
- `pypi`: For production releases

**Branch Protection**:
- Require status checks to pass
- Require pull request reviews
- Restrict push to main

### 2. PyPI Trusted Publishing

**Setup on PyPI**:
1. Go to PyPI project settings
2. Publishing -> Add publisher
3. Configure:
   - Owner: meggy-ai
   - Repository: bruno-memory
   - Workflow: publish.yml
   - Environment: pypi

**Setup on TestPyPI** (optional):
- Same process on test.pypi.org

### 3. Codecov Integration

1. Sign up at codecov.io
2. Connect GitHub repository
3. Copy upload token
4. Add as repository secret: `CODECOV_TOKEN`

### 4. GitHub Pages

**Enable in Settings**:
- Source: GitHub Actions
- Custom domain (optional)

## Release Process

### Standard Release

```bash
# 1. Update version and changelog
python scripts/bump_version.py minor
# Edit CHANGELOG.md

# 2. Commit and push
git add .
git commit -m "Release v0.2.0"
git push origin main

# 3. Push tag (triggers release)
git push origin v0.2.0
```

### Hotfix Release

```bash
# 1. Create hotfix branch
git checkout -b hotfix/v0.1.1 v0.1.0

# 2. Fix issue and bump patch
python scripts/bump_version.py patch

# 3. Merge and release
git checkout main
git merge hotfix/v0.1.1
git push origin main v0.1.1
```

## Monitoring

### GitHub Actions
- Check workflow runs: github.com/meggy-ai/bruno-memory/actions
- Review failed builds immediately
- Check for security advisories

### Codecov Dashboard
- Monitor coverage trends
- Review coverage reports on PRs
- Ensure coverage doesn't decrease

### PyPI Stats
- Monitor download statistics
- Check for reported issues
- Review dependency status

## Security

### Dependency Scanning
- Weekly automated scans
- pip-audit for vulnerabilities
- Dependabot alerts enabled

### Code Scanning
- Bandit for Python security issues
- Pre-commit hooks prevent commits
- Manual review for security PRs

### Secret Management
- No secrets in code (gitignore)
- Use GitHub secrets for CI/CD
- Rotate secrets regularly

## Troubleshooting

### Failed Tests
```bash
# Run specific test
pytest tests/unit/test_factory.py -v

# Run with full output
pytest tests/ -vv --tb=long

# Skip slow tests
pytest tests/ -m "not slow"
```

### Failed Builds
```bash
# Check linting locally
make lint

# Fix formatting
make format

# Type check
make type-check
```

### Failed Deployments
- Check PyPI trusted publishing config
- Verify environment permissions
- Review workflow logs
- Check package build: `python -m build`

## Continuous Improvement

### Metrics to Track
- Test coverage percentage
- Build success rate
- Time to release
- Security vulnerabilities found
- Code quality scores

### Regular Maintenance
- Update GitHub Actions versions
- Update Python versions tested
- Review and update dependencies
- Improve test coverage
- Optimize build times

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Codecov Documentation](https://docs.codecov.com/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Semantic Versioning](https://semver.org/)
