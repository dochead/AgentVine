"""Worker model for Claude Code instances."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.execution import Execution
    from app.models.session import Session
    from app.models.work_order import WorkOrder


class WorkerStatus(str, enum.Enum):
    """Status of a worker."""

    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    ERROR = "error"
    OFFLINE = "offline"


class Worker(Base):
    """Claude Code worker instance."""

    __tablename__ = "workers"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[WorkerStatus] = mapped_column(
        Enum(WorkerStatus),
        nullable=False,
        default=WorkerStatus.IDLE,
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    # Relationships
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="worker",
        cascade="all, delete-orphan",
    )
    work_orders: Mapped[list["WorkOrder"]] = relationship(
        back_populates="worker",
    )
    executions: Mapped[list["Execution"]] = relationship(
        back_populates="worker",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of Worker."""
        return f"<Worker(id={self.id}, name={self.name!r}, status={self.status})>"
