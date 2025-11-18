"""Chat message model for worker-human communication."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SenderType(str, enum.Enum):
    """Type of message sender."""

    WORKER = "worker"
    HUMAN = "human"
    SYSTEM = "system"


class MessageType(str, enum.Enum):
    """Type of chat message."""

    REQUEST = "request"
    RESPONSE = "response"
    STATUS = "status"
    ERROR = "error"


class MessageDirection(str, enum.Enum):
    """Direction of message flow."""

    WORKER_TO_HUMAN = "worker_to_human"
    HUMAN_TO_WORKER = "human_to_worker"


class ChatMessage(Base):
    """Chat message for worker-human communication."""

    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
        index=True,
    )
    sender_type: Mapped[SenderType] = mapped_column(
        Enum(SenderType),
        nullable=False,
        index=True,
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType),
        nullable=False,
        default=MessageType.REQUEST,
        index=True,
    )
    parent_message_id: Mapped[uuid.UUID | None] = mapped_column(
        nullable=True,
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    def __repr__(self) -> str:
        """Return string representation of ChatMessage."""
        return (
            f"<ChatMessage(id={self.id}, sender_type={self.sender_type}, "
            f"message_type={self.message_type})>"
        )
