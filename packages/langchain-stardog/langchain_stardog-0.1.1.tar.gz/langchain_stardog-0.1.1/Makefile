.PHONY: install install-dev format format-check lint type-check test test-cov ci clean help

# Configure uv to use 'venv' instead of '.venv'
export UV_PROJECT_ENVIRONMENT := venv

# Source directories for formatting, linting, etc.
SRC_DIRS := langchain_stardog tests examples

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync --no-dev

install-dev: ## Install development dependencies
	uv sync --all-extras

format: ## Format code with black and isort
	uv run black $(SRC_DIRS)
	uv run isort $(SRC_DIRS)

format-check: ## Check code formatting without making changes
	uv run black --check $(SRC_DIRS)
	uv run isort --check-only $(SRC_DIRS)

lint: ## Run flake8 linter
	uv run flake8 $(SRC_DIRS)

type-check: ## Run mypy type checker
	uv run mypy langchain_stardog

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov=langchain_stardog --cov-report=html --cov-report=term-missing --cov-fail-under=90

ci: format-check lint type-check test-cov ## Run all CI checks (format, lint, type-check, test with coverage)

clean: ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build distribution packages
	uv build

publish: build ## Publish to PyPI (requires API token)
	uv publish

publish-test: build ## Publish to TestPyPI (requires API token)
	uv publish --publish-url https://test.pypi.org/legacy/