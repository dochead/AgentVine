"""Task Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models import TaskPriority, TaskStatus, TaskType


class TaskBase(BaseModel):
    """Base task schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    task_type: TaskType = Field(default=TaskType.FEATURE)
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    repository_url: str = Field(..., min_length=1, max_length=500)
    branch_name: str = Field(..., min_length=1, max_length=255)


class TaskCreate(TaskBase):
    """Schema for creating a task."""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class TaskResponse(TaskBase):
    """Schema for task response."""

    id: uuid.UUID
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True
