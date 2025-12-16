# Makefile for bruno-memory

.PHONY: help install install-dev test test-fast lint format type-check clean docs docs-serve build publish bump-patch bump-minor bump-major

help:
	@echo "bruno-memory development commands:"
	@echo ""
	@echo "Installation:"
	@echo "  make install        Install package and dependencies"
	@echo "  make install-dev    Install with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run all tests with coverage"
	@echo "  make test-fast     Run tests without slow backends"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          Run linting checks (ruff, black)"
	@echo "  make format        Auto-format code"
	@echo "  make type-check    Run type checking with mypy"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs          Build documentation"
	@echo "  make docs-serve    Serve docs locally"
	@echo ""
	@echo "Release:"
	@echo "  make build         Build distribution packages"
	@echo "  make publish       Publish to PyPI"
	@echo "  make bump-patch    Bump patch version (0.0.X)"
	@echo "  make bump-minor    Bump minor version (0.X.0)"
	@echo "  make bump-major    Bump major version (X.0.0)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         Remove build artifacts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test,docs]"

test:
	pytest tests/ -v --cov=bruno_memory --cov-report=html --cov-report=term

test-fast:
	pytest tests/ -v --ignore=tests/unit/test_postgresql_backend.py --ignore=tests/unit/test_redis_backend.py

lint:
	black --check bruno_memory/ tests/
	ruff check bruno_memory/ tests/

format:
	black bruno_memory/ tests/
	ruff check --fix bruno_memory/ tests/

type-check:
	mypy bruno_memory/

clean:
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	mkdocs build

docs-serve:
	mkdocs serve

build: clean
	python -m build

publish: build
	python -m twine upload dist/*

bump-patch:
	python scripts/bump_version.py patch

bump-minor:
	python scripts/bump_version.py minor

bump-major:
	python scripts/bump_version.py major
