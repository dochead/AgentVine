"""Chat message Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.chat_message import MessageDirection


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""

    session_id: uuid.UUID
    direction: MessageDirection
    content: str = Field(..., min_length=1)
    sender_worker_id: uuid.UUID | None = None
    in_reply_to_id: uuid.UUID | None = None


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""

    id: uuid.UUID
    session_id: uuid.UUID
    direction: MessageDirection
    content: str
    sender_worker_id: uuid.UUID | None
    in_reply_to_id: uuid.UUID | None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class WorkerMessageRequest(BaseModel):
    """Schema for worker sending a message to human."""

    session_id: str = Field(..., description="Claude Code session ID")
    worker_id: uuid.UUID = Field(..., description="Worker UUID")
    message: str = Field(..., min_length=1, description="Message content")
    task_id: uuid.UUID | None = Field(None, description="Optional task ID")


class HumanResponseCreate(BaseModel):
    """Schema for human responding to a worker message."""

    message_id: uuid.UUID = Field(..., description="Original message ID")
    response: str = Field(..., min_length=1, description="Human's response")


class ConversationResponse(BaseModel):
    """Schema for conversation history."""

    message_id: str
    direction: str
    content: str
    in_reply_to: str | None
    created_at: str
