.PHONY: help install dev test lint format type-check security clean run

help:
	@echo "AgentVine Backend - Available Commands"
	@echo "======================================="
	@echo "install      - Install production dependencies (uv sync)"
	@echo "dev          - Install development dependencies (uv sync --all-extras)"
	@echo "run          - Run the development server"
	@echo "test         - Run tests with coverage"
	@echo "lint         - Run ruff linter"
	@echo "format       - Format code with black"
	@echo "type-check   - Run mypy type checker"
	@echo "security     - Run bandit security scanner"
	@echo "clean        - Remove cache and build files"

install:
	uv sync

dev:
	uv sync --all-extras

run:
	uv run python -m app.main

test:
	uv run pytest --cov=app --cov-report=term-missing --cov-report=html

lint:
	uv run ruff check app/ tests/

format:
	uv run black app/ tests/

type-check:
	uv run mypy app/

security:
	uv run bandit -r app/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".uv_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .venv dist *.egg-info
