"""Response models for API endpoints.

All response models use Pydantic for validation and serialization,
providing complete type safety and automatic OpenAPI documentation.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model.

    Attributes:
        status: Health status indicator, always "healthy" for successful responses
        timestamp: ISO 8601 formatted timestamp of the health check
    """

    status: Literal["healthy"] = Field(
        description="Health status of the service"
    )
    timestamp: datetime = Field(
        description="Current server timestamp in ISO 8601 format"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-11-18T12:00:00.000Z"
            }
        }


class AboutResponse(BaseModel):
    """About endpoint response model.

    Attributes:
        name: Application name
        version: Current version following semantic versioning
        description: Brief description of the application's purpose
    """

    name: str = Field(
        description="Application name"
    )
    version: str = Field(
        description="Application version (semantic versioning)"
    )
    description: str = Field(
        description="Application description"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "name": "AgentVine",
                "version": "0.01",
                "description": "Event-driven autonomous development system"
            }
        }
