"""Queue API endpoints."""

from fastapi import APIRouter

from app.schemas.queue import QueueStatsResponse, WorkOrderClaim
from app.services.queue_manager import QueueManager

router = APIRouter(prefix="/queue", tags=["queue"])


@router.get("/status", response_model=QueueStatsResponse)
async def get_queue_status() -> QueueStatsResponse:
    """Get queue statistics.

    Returns:
        QueueStatsResponse: Statistics for all queues.
    """
    queue_manager = QueueManager()
    stats = queue_manager.get_queue_stats()

    return QueueStatsResponse(
        high_priority=stats["high_priority"],
        default=stats["default"],
        low_priority=stats["low_priority"],
        worker_requests=stats["worker_requests"],
        controller_responses=stats["controller_responses"],
    )


@router.post("/claim", response_model=WorkOrderClaim | None)
async def claim_work(
    queue_names: list[str] | None = None,
) -> WorkOrderClaim | None:
    """Claim next available work order.

    Args:
        queue_names: Optional list of queue names to check.

    Returns:
        WorkOrderClaim | None: Work order data or None if no work available.
    """
    queue_manager = QueueManager()
    work = queue_manager.claim_work(queue_names)

    if work:
        return WorkOrderClaim(**work)

    return None
