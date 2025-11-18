"""Queue Pydantic schemas."""

from typing import Any

from pydantic import BaseModel


class QueueStats(BaseModel):
    """Queue statistics."""

    pending: int
    started: int
    finished: int
    failed: int
    deferred: int
    scheduled: int


class QueueStatsResponse(BaseModel):
    """Response for queue statistics."""

    high_priority: QueueStats
    default: QueueStats
    low_priority: QueueStats
    worker_requests: QueueStats
    controller_responses: QueueStats


class WorkOrderClaim(BaseModel):
    """Response for claiming work order."""

    job_id: str
    queue: str
    data: dict[str, Any]
    meta: dict[str, Any]
