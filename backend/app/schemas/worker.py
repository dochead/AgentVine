"""Worker Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models import WorkerStatus


class WorkerCreate(BaseModel):
    """Schema for worker registration."""

    name: str = Field(..., min_length=1, max_length=255)


class WorkerHeartbeat(BaseModel):
    """Schema for worker heartbeat."""

    status: WorkerStatus


class WorkerResponse(BaseModel):
    """Schema for worker response."""

    id: uuid.UUID
    name: str
    status: WorkerStatus
    created_at: datetime
    updated_at: datetime
    last_heartbeat_at: datetime | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True
