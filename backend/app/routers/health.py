"""Health check endpoint router.

Provides a simple health check endpoint for monitoring and load balancers.
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.models.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the health status of the service with a timestamp",
    status_code=200,
)
async def health_check() -> HealthResponse:
    """Check the health status of the API.

    Returns:
        HealthResponse: Health status and current timestamp

    Example:
        ```python
        response = await health_check()
        # {"status": "healthy", "timestamp": "2025-11-18T12:00:00.000Z"}
        ```
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc)
    )
