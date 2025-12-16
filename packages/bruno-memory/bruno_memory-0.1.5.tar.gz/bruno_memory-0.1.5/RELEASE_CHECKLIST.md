# Release Checklist

Use this checklist when preparing a new release of bruno-memory.

## Pre-Release

### Code Quality
- [ ] All tests passing locally (`pytest tests/`)
- [ ] Code coverage above 60% (`pytest --cov`)
- [ ] No linting errors (`make lint`)
- [ ] Type checking clean (`mypy bruno_memory/`)
- [ ] Security audit clean (`bandit -r bruno_memory/`)
- [ ] Dependency audit clean (`pip-audit`)

### Documentation
- [ ] README.md updated with new features
- [ ] CHANGELOG.md updated with version and changes
- [ ] API documentation built successfully (`mkdocs build`)
- [ ] All code examples tested and working
- [ ] Migration guide written (if breaking changes)

### Version Management
- [ ] Version bumped in `pyproject.toml`
- [ ] Version bumped in `bruno_memory/__init__.py`
- [ ] Git status clean (all changes committed)
- [ ] All branches merged to main

### Testing
- [ ] Unit tests passing (all backends)
- [ ] Integration tests passing
- [ ] Manual smoke tests completed
- [ ] Tested on Python 3.10, 3.11, 3.12
- [ ] Tested on Windows, macOS, Linux

## Release Process

### 1. Prepare Release
```bash
# Update version
python scripts/bump_version.py minor  # or major/patch

# Review changes
git diff

# Commit version bump
git commit -am "Bump version to X.Y.Z"
```

### 2. Create Git Tag
```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release version X.Y.Z"

# Push to GitHub
git push origin main
git push origin vX.Y.Z
```

### 3. GitHub Actions
- [ ] CI workflow passes
- [ ] Lint workflow passes
- [ ] Release workflow creates GitHub release
- [ ] PyPI publishing succeeds
- [ ] Documentation deployed to GitHub Pages

### 4. Verify Release
```bash
# Wait a few minutes for PyPI
pip install --upgrade bruno-memory==X.Y.Z

# Test installation
python -c "import bruno_memory; print(bruno_memory.__version__)"
```

### 5. Post-Release

#### Update Documentation Site
- [ ] Visit https://meggy-ai.github.io/bruno-memory/
- [ ] Verify new version in docs
- [ ] Test all documentation links

#### Create Release Notes
- [ ] Edit GitHub release with detailed notes
- [ ] Highlight breaking changes
- [ ] Include migration guide link
- [ ] Add contributor acknowledgments

#### Announce Release
- [ ] Post to GitHub Discussions
- [ ] Tweet/post on social media
- [ ] Update project website (if applicable)
- [ ] Notify users in Discord/Slack

#### Archive
- [ ] Move completed CHANGELOG items to version section
- [ ] Start new [Unreleased] section
- [ ] Close related GitHub issues
- [ ] Update project roadmap

## Rollback Procedure

If a critical issue is found:

```bash
# Delete the tag
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z

# Revert version bump
git revert HEAD

# Contact PyPI support to yank the release if necessary
```

## Hotfix Process

For urgent fixes:

1. Create hotfix branch from main
2. Make minimal fix
3. Bump patch version
4. Fast-track testing
5. Release immediately
6. Follow normal release process

## Version Strategy

- **Major (X.0.0)**: Breaking API changes, major features
- **Minor (0.X.0)**: New features, backwards compatible
- **Patch (0.0.X)**: Bug fixes only

## Release Schedule

- **Major releases**: As needed
- **Minor releases**: Monthly or when features are ready
- **Patch releases**: As needed for critical bugs

## Support Policy

- **Latest version**: Full support
- **Previous minor**: Security fixes only
- **Older versions**: No support

## Emergency Contacts

- **PyPI Issues**: pypi.org/help
- **GitHub Issues**: github.com/meggy-ai/bruno-memory/issues
- **Security**: security@meggy-ai.com
