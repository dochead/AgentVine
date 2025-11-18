"""Chat message Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models import MessageType, SenderType


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""

    conversation_id: uuid.UUID
    sender_type: SenderType
    sender_id: uuid.UUID
    message: str = Field(..., min_length=1)
    message_type: MessageType = Field(default=MessageType.REQUEST)
    parent_message_id: uuid.UUID | None = None


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_type: SenderType
    sender_id: uuid.UUID
    message: str
    message_type: MessageType
    parent_message_id: uuid.UUID | None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
