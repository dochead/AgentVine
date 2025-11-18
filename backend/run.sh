#!/bin/bash
# Quick start script for AgentVine backend

set -e

echo "Starting AgentVine Backend..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dependencies if needed
if [ ! -d ".venv" ] || ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    uv sync
fi

# Run the application
echo "Starting FastAPI server on port 8000..."
uv run python -m app.main
