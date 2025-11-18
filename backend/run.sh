#!/bin/bash
# Quick start script for AgentVine backend

set -e

echo "Starting AgentVine Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "No virtual environment found. Creating one..."
    python -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the application
echo "Starting FastAPI server on port 8000..."
python -m app.main
