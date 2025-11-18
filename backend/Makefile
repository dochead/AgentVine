.PHONY: help install dev test lint format type-check security clean run

help:
	@echo "AgentVine Backend - Available Commands"
	@echo "======================================="
	@echo "install      - Install production dependencies"
	@echo "dev          - Install development dependencies"
	@echo "run          - Run the development server"
	@echo "test         - Run tests with coverage"
	@echo "lint         - Run ruff linter"
	@echo "format       - Format code with black"
	@echo "type-check   - Run mypy type checker"
	@echo "security     - Run bandit security scanner"
	@echo "clean        - Remove cache and build files"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt

run:
	python -m app.main

test:
	pytest --cov=app --cov-report=term-missing --cov-report=html

lint:
	ruff check app/ tests/

format:
	black app/ tests/

type-check:
	mypy app/

security:
	bandit -r app/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
