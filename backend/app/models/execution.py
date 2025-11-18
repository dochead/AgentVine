"""Execution model for task execution tracking."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.task import Task
    from app.models.worker import Worker


class ExecutionStatus(str, enum.Enum):
    """Status of a task execution."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Execution(Base):
    """Execution log for task execution by worker."""

    __tablename__ = "executions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus),
        nullable=False,
        default=ExecutionStatus.RUNNING,
        index=True,
    )
    output: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="executions")
    worker: Mapped["Worker"] = relationship(back_populates="executions")
    session: Mapped["Session"] = relationship(back_populates="executions")

    def __repr__(self) -> str:
        """Return string representation of Execution."""
        return (
            f"<Execution(id={self.id}, task_id={self.task_id}, "
            f"worker_id={self.worker_id}, status={self.status})>"
        )
