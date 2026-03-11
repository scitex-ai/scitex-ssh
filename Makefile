# Makefile for SciTeX Tunnel
# Usage: make [target]

GREEN := \033[0;32m
CYAN := \033[0;36m
NC := \033[0m

VERSION := $(shell grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/' | head -1 | tr -d '"')

.PHONY: \
	install \
	develop \
	test \
	test-coverage \
	build \
	upload \
	upload-test \
	version \
	clean \
	docs \
	help

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Installation
# ============================================================================
install:
	@echo "Installing scitex-tunnel..."
	pip install .

develop:
	@echo "Installing scitex-tunnel in development mode..."
	pip install -e ".[dev]"

# ============================================================================
# Testing
# ============================================================================
test:
	@echo "Running tests..."
	pytest tests/ -v --tb=short

test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=scitex_tunnel --cov-report=term-missing

# ============================================================================
# Building and publishing
# ============================================================================
build:
	@echo "Building distribution packages..."
	python -m build

upload:
	@echo "Uploading to PyPI..."
	python -m twine upload dist/*

upload-test:
	@echo "Uploading to Test PyPI..."
	python -m twine upload --repository testpypi dist/*

# ============================================================================
# Documentation
# ============================================================================
docs:
	@echo "Building documentation..."
	cd docs/sphinx && sphinx-build -b html . _build/html

# ============================================================================
# Information
# ============================================================================
version:
	@echo "scitex-tunnel $(VERSION)"

# ============================================================================
# Cleaning
# ============================================================================
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf docs/sphinx/_build/
	rm -rf .pytest_cache/
	rm -rf .coverage htmlcov/

# ============================================================================
# Help
# ============================================================================
help:
	@echo ""
	@printf "$(GREEN)scitex-tunnel v$(VERSION)$(NC)\n"
	@echo ""
	@printf "$(CYAN)Installation:$(NC)\n"
	@echo "  make install              Install package"
	@echo "  make develop              Install in development mode"
	@echo ""
	@printf "$(CYAN)Testing:$(NC)\n"
	@echo "  make test                 Run tests"
	@echo "  make test-coverage        Run tests with coverage report"
	@echo ""
	@printf "$(CYAN)Building:$(NC)\n"
	@echo "  make build                Build distribution packages"
	@echo "  make upload               Upload to PyPI"
	@echo "  make upload-test          Upload to Test PyPI"
	@echo ""
	@printf "$(CYAN)Documentation:$(NC)\n"
	@echo "  make docs                 Build Sphinx documentation"
	@echo ""
	@printf "$(CYAN)Information:$(NC)\n"
	@echo "  make version              Show version"
	@echo "  make help                 Show this help message"
	@echo ""
	@printf "$(CYAN)Cleaning:$(NC)\n"
	@echo "  make clean                Remove build artifacts"
