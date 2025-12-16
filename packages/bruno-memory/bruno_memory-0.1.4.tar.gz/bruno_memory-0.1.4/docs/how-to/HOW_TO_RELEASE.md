# How to Create a Release

This guide walks you through creating a new release of bruno-memory from start to finish.

## Prerequisites

Before creating a release, ensure you have:

- [ ] All changes merged to `main` branch
- [ ] All tests passing locally
- [ ] Git repository clean (no uncommitted changes)
- [ ] Access to push tags to GitHub
- [ ] PyPI account configured (for maintainers)

## Release Types

Choose the appropriate version bump based on your changes:

- **Patch (0.1.X)**: Bug fixes, documentation updates, minor improvements
- **Minor (0.X.0)**: New features, backwards-compatible changes
- **Major (X.0.0)**: Breaking changes, major architecture updates

## Step-by-Step Release Process

### 1. Prepare the Release

#### a. Update the Changelog

Edit `CHANGELOG.md` to document all changes since the last release:

```bash
# Open CHANGELOG.md in your editor
code CHANGELOG.md
```

Move items from `[Unreleased]` to a new version section:

```markdown
## [Unreleased]

<!-- Leave empty for next release -->

## [0.2.0] - 2025-12-11

### Added
- New memory prioritization feature
- Performance monitoring utilities

### Changed
- Improved caching performance

### Fixed
- Fixed SQLite backend connection leak
```

#### b. Run Pre-Release Checks

```bash
# Run full test suite
make test
# Or on Windows: pytest tests/ -v --cov=bruno_memory --cov-report=html --cov-report=term

# Check code quality
make lint
# Or on Windows: black --check bruno_memory/ tests/; ruff check bruno_memory/ tests/

# Type checking
make type-check
# Or on Windows: mypy bruno_memory/

# Security audit
pip install pip-audit
pip-audit
```

**Windows PowerShell users**: If `make` is not available, use the expanded commands shown after "Or on Windows".

All checks should pass before proceeding.

### 2. Bump the Version

Use the automated version bumping script:

```bash
# For patch release (0.1.0 -> 0.1.1)
make bump-patch
# Or on Windows: python scripts/bump_version.py patch

# For minor release (0.1.0 -> 0.2.0)
make bump-minor
# Or on Windows: python scripts/bump_version.py minor

# For major release (0.1.0 -> 1.0.0)
make bump-major
# Or on Windows: python scripts/bump_version.py major
```

Use the script directly with more options:

```bash
# Dry run to see what will change
python scripts/bump_version.py minor --dry-run

# Bump version and create commit + tag
python scripts/bump_version.py minor

# Bump version without creating git commit
python scripts/bump_version.py minor --no-commit

# Bump version without creating git tag
python scripts/bump_version.py minor --no-tag
```

**What this does:**
- Updates version in `pyproject.toml`
- Updates `__version__` in `bruno_memory/__init__.py`
- Creates a git commit with message "Bump version to X.Y.Z"
- Creates an annotated git tag `vX.Y.Z`

### 3. Review the Changes

```bash
# Check the version bump commit
git log -1

# View the tag
git tag -l -n1 v*

# Verify the version
python -c "import bruno_memory; print(bruno_memory.__version__)"
```

### 4. Push to GitHub

Push both the commit and the tag:

```bash
# Push the commit
git push origin main

# Push the tag (this triggers the release workflow)
git push origin v0.2.0
```

**Important**: Pushing the tag will automatically trigger:
1. GitHub Actions release workflow
2. Build of distribution packages
3. Creation of GitHub Release
4. Publishing to PyPI
5. Documentation deployment to GitHub Pages

### 5. Monitor the Release

#### a. Check GitHub Actions

1. Go to [Actions](https://github.com/meggy-ai/bruno-memory/actions)
2. Find the "Release" workflow run
3. Monitor progress of all jobs:
   - Create GitHub Release
   - Deploy Documentation
   - Announce

#### b. Verify the GitHub Release

1. Go to [Releases](https://github.com/meggy-ai/bruno-memory/releases)
2. Verify the new release is created
3. Check that distribution files are attached (.tar.gz and .whl)
4. Review the automatically generated changelog

#### c. Verify PyPI Publication

After the workflow completes (usually 5-10 minutes):

```bash
# Check PyPI page
# Visit: https://pypi.org/project/bruno-memory/

# Test installation
pip install --upgrade bruno-memory==0.2.0

# Verify version
python -c "import bruno_memory; print(bruno_memory.__version__)"
```

#### d. Verify Documentation

Visit the documentation site:
- **URL**: https://meggy-ai.github.io/bruno-memory/
- Verify the version in the footer
- Test navigation and links
- Check new features are documented

### 6. Post-Release Tasks

#### a. Update the GitHub Release Notes

The release is created automatically, but you should enhance it:

1. Go to the release page
2. Click "Edit release"
3. Add detailed release notes:

```markdown
## 🎉 What's New in v0.2.0

### New Features
- **Memory Prioritization**: Intelligent scoring system with 4 factors
- **Performance Monitoring**: Track and optimize operations
- **Security Enhancements**: Encryption and anonymization utilities

### Improvements
- Improved caching performance by 40%
- Better error messages across all backends
- Enhanced documentation with more examples

### Bug Fixes
- Fixed connection leak in SQLite backend
- Resolved race condition in Redis cache
- Corrected timestamp handling in PostgreSQL

### Breaking Changes
None in this release.

### Upgrade Instructions
```bash
pip install --upgrade bruno-memory
```

### Documentation
Full documentation: https://meggy-ai.github.io/bruno-memory/

### Contributors
Thank you to all contributors! 🙏
```

#### b. Announce the Release

Share the news with your community:

**GitHub Discussions** (if enabled):
1. Go to Discussions
2. Create new post in "Announcements"
3. Share release highlights and link

**Social Media**:
- Twitter/X: "Released bruno-memory v0.2.0 with memory prioritization and performance monitoring! 🚀"
- LinkedIn: Share with relevant groups
- Reddit: r/Python, r/MachineLearning (if relevant)

**Email** (if you have a mailing list):
- Send release announcement to subscribers
- Highlight breaking changes if any

#### c. Close Related Issues

Go through GitHub Issues and:
1. Close issues that were fixed in this release
2. Add comment: "Fixed in v0.2.0"
3. Add the release milestone (if using milestones)

#### d. Update Project Board

If using GitHub Projects:
1. Move completed items to "Done"
2. Close the release milestone
3. Create milestone for next release

### 7. Start Next Development Cycle

Prepare for the next release:

```bash
# Update CHANGELOG.md
code CHANGELOG.md
```

Add a new `[Unreleased]` section at the top:

```markdown
## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.2.0] - 2025-12-11
...
```

Commit the change:

```bash
git add CHANGELOG.md
git commit -m "Start v0.3.0 development cycle"
git push origin main
```

## Troubleshooting

### The workflow failed

**Check the logs:**
1. Go to Actions tab
2. Click on the failed workflow
3. Review error messages
**Build fails:**
```bash
# Test build locally
pip install build
python -m build
pip install twine
twine check dist/*
```

**Tests fail:**
```bash
# Run tests locally (Linux/Mac)
make test

# Run tests on Windows
pytest tests/ -v --cov=bruno_memory
```bash
# Run tests locally
make test
```

**PyPI publishing fails:**
- Verify PyPI trusted publishing is configured
- Check environment permissions in GitHub settings
- Ensure version doesn't already exist on PyPI

### Need to rollback a release

If you need to undo a release:

```bash
# Delete the tag locally
git tag -d v0.2.0

# Delete the tag remotely
git push origin :refs/tags/v0.2.0

# Revert the version bump commit
git revert HEAD
git push origin main
```

**On PyPI:**
- You cannot delete a release
- Contact PyPI support to "yank" the release
- Release a new patch version with fixes

### Version conflict on PyPI

If the version already exists:

```bash
# Delete the local tag
git tag -d v0.2.0

# Bump to next version
python scripts/bump_version.py patch

# Push again
git push origin main
git push origin v0.2.1
```

## Hotfix Release Process

For urgent bug fixes:

### 1. Create Hotfix Branch

```bash
# Create branch from the problematic release
git checkout -b hotfix/v0.2.1 v0.2.0

# Make your fix
# ... edit files ...

# Commit the fix
git add .
git commit -m "Fix critical bug in memory backend"
```

### 2. Bump Version

```bash
# Bump patch version
python scripts/bump_version.py patch
```

### 3. Merge and Release

```bash
# Switch to main
git checkout main

# Merge hotfix
git merge hotfix/v0.2.1

# Push
git push origin main
git push origin v0.2.1
```

### 4. Fast-track Testing

For hotfixes, you may skip some checks but **always**:
- [ ] Test the specific bug fix
- [ ] Run relevant unit tests
- [ ] Verify no new issues introduced

## Release Checklist Summary

Use this quick checklist for each release:

```markdown
## Pre-Release
- [ ] All tests passing
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Tag created and pushed

## During Release
- [ ] GitHub Actions workflow succeeds
- [ ] GitHub Release created
- [ ] PyPI package published
- [ ] Documentation deployed

## Post-Release
- [ ] Verify installation from PyPI
- [ ] Enhance release notes
- [ ] Close related issues
- [ ] Announce release
- [ ] Start next development cycle
```

## Best Practices

### Do's ✅
- Always update the changelog before releasing
- Test thoroughly before pushing tags
- Use semantic versioning consistently
- Write detailed release notes
- Announce breaking changes prominently
- Keep a regular release schedule

### Don'ts ❌
- Don't push tags without testing
- Don't skip changelog updates
## Automation Tips

### Create Release Script

**For Linux/Mac** - Save this as `scripts/release.sh`:

```bash
#!/bin/bash
set -e

VERSION=$1
TYPE=${2:-minor}

echo "🚀 Creating release $VERSION"

# Pre-checks
echo "📋 Running pre-release checks..."
make test
make lint

# Update changelog
echo "📝 Update CHANGELOG.md and press Enter"
read

# Bump version
echo "⬆️  Bumping version..."
python scripts/bump_version.py $TYPE

# Push
echo "🔼 Pushing to GitHub..."
git push origin main
git push origin v$VERSION

echo "✅ Release v$VERSION initiated!"
echo "Monitor: https://github.com/meggy-ai/bruno-memory/actions"
```

Use it:
```bash
chmod +x scripts/release.sh
./scripts/release.sh 0.2.0 minor
```

**For Windows PowerShell** - Save this as `scripts/release.ps1`:

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    [string]$Type = "minor"
)

Write-Host "🚀 Creating release $Version" -ForegroundColor Green

# Pre-checks
Write-Host "📋 Running pre-release checks..." -ForegroundColor Yellow
pytest tests/ -v --cov=bruno_memory
if ($LASTEXITCODE -ne 0) { exit 1 }

black --check bruno_memory/ tests/
if ($LASTEXITCODE -ne 0) { exit 1 }

ruff check bruno_memory/ tests/
if ($LASTEXITCODE -ne 0) { exit 1 }

# Update changelog
Write-Host "📝 Update CHANGELOG.md and press Enter" -ForegroundColor Yellow
Read-Host

# Bump version
Write-Host "⬆️  Bumping version..." -ForegroundColor Yellow
python scripts/bump_version.py $Type
if ($LASTEXITCODE -ne 0) { exit 1 }

# Push
Write-Host "🔼 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
git push origin "v$Version"

Write-Host "✅ Release v$Version initiated!" -ForegroundColor Green
Write-Host "Monitor: https://github.com/meggy-ai/bruno-memory/actions"
```

Use it:
```powershell
.\scripts\release.ps1 -Version "0.2.0" -Type "minor"
```
Use it:
```bash
chmod +x scripts/release.sh
./scripts/release.sh 0.2.0 minor
```

## Getting Help

If you encounter issues:

1. **Check documentation**: Review this guide and `CI_CD_GUIDE.md`
2. **GitHub Actions logs**: Review workflow runs for errors
3. **Ask for help**: Create an issue or discussion
4. **Contact maintainers**: Reach out via email or Slack

## Additional Resources

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Python Packaging Guide](https://packaging.python.org/)

---

**Ready to release?** Follow this guide step by step and you'll have a smooth release process! 🎉
