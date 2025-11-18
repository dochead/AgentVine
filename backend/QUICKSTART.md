# AgentVine Backend - Quick Start Guide

## Fastest Way to Get Started

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# Option 1: Using the run script
./run.sh

# Option 2: Using Python directly
python -m app.main

# Option 3: Using uvicorn
uvicorn app.main:app --reload
```

### 3. Test the API

Open your browser and visit:
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **About**: http://localhost:8000/about

### 4. Run Tests

```bash
pytest
```

## Common Commands

```bash
# Using Makefile
make install      # Install dependencies
make run         # Run server
make test        # Run tests
make format      # Format code
make lint        # Check code quality

# Manual commands
python -m pytest                    # Run tests
black app/ tests/                   # Format code
ruff check app/ tests/              # Lint code
mypy app/                           # Type check
bandit -r app/                      # Security scan
```

## API Endpoints

### GET /health
Returns health status and timestamp.

**cURL:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T12:00:00.000Z"
}
```

### GET /about
Returns application information.

**cURL:**
```bash
curl http://localhost:8000/about
```

**Response:**
```json
{
  "name": "AgentVine",
  "version": "0.01",
  "description": "Event-driven autonomous development system"
}
```

## Project Structure at a Glance

```
backend/
├── app/                    # Application code
│   ├── main.py            # FastAPI app entry point
│   ├── models/            # Pydantic models
│   │   └── responses.py   # Response schemas
│   └── routers/           # API endpoints
│       ├── health.py      # Health check
│       └── about.py       # About info
├── tests/                 # Test suite
│   ├── test_health.py     # Health endpoint tests
│   └── test_about.py      # About endpoint tests
├── requirements.txt       # Dependencies
└── pyproject.toml        # Project configuration
```

## Next Steps

1. Explore the interactive API docs at http://localhost:8000/docs
2. Add your own endpoints in `app/routers/`
3. Create Pydantic models in `app/models/`
4. Write tests in `tests/`
5. Run `make test` to ensure everything passes

## Troubleshooting

**Port 8000 already in use?**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --port 8001
```

**Module not found errors?**
```bash
# Make sure you're in the backend directory and venv is activated
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Import errors?**
```bash
# Run from the backend directory, not from app/
cd backend
python -m app.main  # Correct
# python app/main.py  # Incorrect
```
