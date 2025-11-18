"""Work order model for queue management."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.worker import Worker


class WorkOrderStatus(str, enum.Enum):
    """Status of a work order."""

    QUEUED = "queued"
    CLAIMED = "claimed"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkOrderPriority(str, enum.Enum):
    """Priority level of a work order."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class WorkOrder(Base):
    """Work order representing queued task execution."""

    __tablename__ = "work_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    worker_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[WorkOrderStatus] = mapped_column(
        Enum(WorkOrderStatus),
        nullable=False,
        default=WorkOrderStatus.QUEUED,
        index=True,
    )
    priority: Mapped[WorkOrderPriority] = mapped_column(
        Enum(WorkOrderPriority),
        nullable=False,
        default=WorkOrderPriority.NORMAL,
        index=True,
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Timestamps
    enqueued_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="work_orders")
    worker: Mapped["Worker | None"] = relationship(back_populates="work_orders")

    def __repr__(self) -> str:
        """Return string representation of WorkOrder."""
        return (
            f"<WorkOrder(id={self.id}, task_id={self.task_id}, "
            f"status={self.status}, priority={self.priority})>"
        )
