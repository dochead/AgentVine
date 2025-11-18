"""AgentVine FastAPI Backend Application.

This module provides the main FastAPI application with CORS middleware,
router configuration, and API documentation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.routers import about_router, health_router

# Create FastAPI application instance
app = FastAPI(
    title="AgentVine API",
    description="Event-driven autonomous development system backend",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS middleware for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default dev server
        "http://localhost:5173",  # Vite default dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(about_router)


@app.on_event("startup")
async def startup_event() -> None:
    """Execute on application startup.

    Perform any necessary initialization tasks such as:
    - Database connection pool setup
    - Cache warming
    - External service health checks
    """
    pass


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Execute on application shutdown.

    Perform cleanup tasks such as:
    - Database connection pool closure
    - Background task cancellation
    - Resource cleanup
    """
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
