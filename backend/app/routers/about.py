"""About endpoint router.

Provides information about the AgentVine application.
"""

from fastapi import APIRouter

from app import __version__
from app.models.responses import AboutResponse

router = APIRouter(tags=["Info"])


@router.get(
    "/about",
    response_model=AboutResponse,
    summary="Get application information",
    description="Returns basic information about the AgentVine application",
    status_code=200,
)
async def about() -> AboutResponse:
    """Get information about the AgentVine application.

    Returns:
        AboutResponse: Application name, version, and description

    Example:
        ```python
        response = await about()
        # {
        #     "name": "AgentVine",
        #     "version": "0.01",
        #     "description": "Event-driven autonomous development system"
        # }
        ```
    """
    return AboutResponse(
        name="AgentVine",
        version=__version__,
        description="Event-driven autonomous development system"
    )
