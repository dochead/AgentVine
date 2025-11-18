"""Session Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models import SessionStatus


class SessionCreate(BaseModel):
    """Schema for creating a session mapping."""

    session_id: str = Field(..., min_length=1, max_length=255)
    worker_id: uuid.UUID
    task_id: uuid.UUID | None = None


class SessionResponse(BaseModel):
    """Schema for session response."""

    id: uuid.UUID
    session_id: str
    worker_id: uuid.UUID
    task_id: uuid.UUID | None
    status: SessionStatus
    created_at: datetime
    last_activity_at: datetime
    terminated_at: datetime | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True
