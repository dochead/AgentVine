# AgentVine Backend

Event-driven autonomous development system backend built with FastAPI.

## Features

- **FastAPI**: Modern, fast, async web framework
- **Type Safety**: Complete type hints with Pydantic models
- **API-First**: OpenAPI specification generated automatically
- **CORS Enabled**: Frontend connectivity configured
- **Production Ready**: Structured for scalability and maintainability

## Project Structure

```
backend/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application entry point
│   ├── models/               # Pydantic models
│   │   ├── __init__.py
│   │   └── responses.py      # Response models
│   └── routers/              # API endpoint routers
│       ├── __init__.py
│       ├── about.py          # About endpoint
│       └── health.py         # Health check endpoint
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Modern Python project config
└── README.md                # This file
```

## Requirements

- Python 3.11+
- pip or uv for package management

## Setup

### Option 1: Using pip and venv

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development dependencies
pip install -r requirements.txt
```

### Option 2: Using uv (recommended)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Linux/Mac
# .venv\Scripts\activate  # On Windows

# Install dependencies
uv pip install -r requirements.txt
```

## Running the Application

### Development Mode

```bash
# From the backend directory with activated virtual environment
python -m app.main
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check
**GET** `/health`

Returns the health status of the service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T12:00:00.000Z"
}
```

### About
**GET** `/about`

Returns information about the application.

**Response:**
```json
{
  "name": "AgentVine",
  "version": "0.01",
  "description": "Event-driven autonomous development system"
}
```

## Development

### Code Quality

Format code with Black:
```bash
black app/
```

Lint with Ruff:
```bash
ruff check app/
```

Type check with mypy:
```bash
mypy app/
```

Security scan with Bandit:
```bash
bandit -r app/
```

### Testing

Run tests with pytest:
```bash
pytest
```

With coverage report:
```bash
pytest --cov=app --cov-report=html
```

## Environment Configuration

The application uses sensible defaults but can be configured via environment variables:

```bash
# Example .env file (create this for local development)
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
RELOAD=true
```

## CORS Configuration

CORS is pre-configured for common frontend development ports:
- http://localhost:3000 (React default)
- http://localhost:5173 (Vite default)

To modify CORS settings, edit the `CORSMiddleware` configuration in `app/main.py`.

## Next Steps

1. Add database integration (SQLAlchemy with async support)
2. Implement authentication and authorization
3. Add request/response logging middleware
4. Set up environment-based configuration (pydantic-settings)
5. Add comprehensive test suite
6. Set up CI/CD pipeline
7. Add API rate limiting
8. Implement caching layer (Redis)

## License

See the main project LICENSE file.
