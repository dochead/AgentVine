"""Queue management service for RQ operations."""

import uuid
from datetime import datetime
from typing import Any

from rq import Queue
from rq.job import Job

from app.core.redis import (
    controller_responses_queue,
    default_queue,
    get_queue,
    high_priority_queue,
    low_priority_queue,
    worker_requests_queue,
)
from app.models import WorkOrderPriority


class QueueManager:
    """Manager for Redis queue operations."""

    def __init__(self) -> None:
        """Initialize queue manager."""
        self.high_priority = high_priority_queue
        self.default = default_queue
        self.low_priority = low_priority_queue
        self.worker_requests = worker_requests_queue
        self.controller_responses = controller_responses_queue

    def enqueue_work_order(
        self,
        work_order_id: uuid.UUID,
        task_data: dict[str, Any],
        priority: WorkOrderPriority = WorkOrderPriority.NORMAL,
        timeout: int = 3600,
    ) -> str:
        """Enqueue a work order for worker execution.

        Args:
            work_order_id: Work order UUID.
            task_data: Task data dictionary.
            priority: Priority level.
            timeout: Job timeout in seconds.

        Returns:
            str: Job ID.
        """
        # Select queue based on priority
        if priority in (WorkOrderPriority.HIGH,):
            queue = self.high_priority
        elif priority == WorkOrderPriority.LOW:
            queue = self.low_priority
        else:
            queue = self.default

        # Enqueue work (placeholder function, will be replaced with actual worker execution)
        job = queue.enqueue(
            "worker.execute_task",  # Placeholder
            task_data,
            job_id=str(work_order_id),
            job_timeout=timeout,
            result_ttl=86400,  # Keep results for 24 hours
            failure_ttl=604800,  # Keep failures for 7 days
            meta={
                "work_order_id": str(work_order_id),
                "task_id": task_data.get("task_id"),
                "enqueued_at": datetime.utcnow().isoformat(),
            },
        )

        return job.id

    def enqueue_worker_request(
        self,
        request_id: uuid.UUID,
        worker_id: uuid.UUID,
        work_order_id: uuid.UUID,
        task_id: uuid.UUID,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Enqueue a worker clarification request.

        Args:
            request_id: Request UUID.
            worker_id: Worker UUID.
            work_order_id: Work order UUID.
            task_id: Task UUID.
            message: Request message.
            context: Additional context.

        Returns:
            str: Job ID.
        """
        request_data = {
            "request_id": str(request_id),
            "worker_id": str(worker_id),
            "work_order_id": str(work_order_id),
            "task_id": str(task_id),
            "message": message,
            "context": context or {},
            "created_at": datetime.utcnow().isoformat(),
        }

        job = self.worker_requests.enqueue(
            "controller.process_request",  # Placeholder
            request_data,
            job_id=str(request_id),
            job_timeout=1800,  # 30 minutes
            result_ttl=3600,
        )

        return job.id

    def enqueue_controller_response(
        self,
        response_id: uuid.UUID,
        request_id: uuid.UUID,
        worker_id: uuid.UUID,
        message: str,
        generated_by: str = "human",
    ) -> str:
        """Enqueue a controller response to worker.

        Args:
            response_id: Response UUID.
            request_id: Original request UUID.
            worker_id: Worker UUID.
            message: Response message.
            generated_by: Source of response (human or automated).

        Returns:
            str: Job ID.
        """
        response_data = {
            "response_id": str(response_id),
            "request_id": str(request_id),
            "worker_id": str(worker_id),
            "message": message,
            "generated_by": generated_by,
            "created_at": datetime.utcnow().isoformat(),
        }

        job = self.controller_responses.enqueue(
            "worker.receive_response",  # Placeholder
            response_data,
            job_id=str(response_id),
            job_timeout=300,
            result_ttl=3600,
        )

        return job.id

    def get_queue_stats(self) -> dict[str, dict[str, int]]:
        """Get statistics for all queues.

        Returns:
            dict: Queue statistics.
        """
        queues = [
            ("high_priority", self.high_priority),
            ("default", self.default),
            ("low_priority", self.low_priority),
            ("worker_requests", self.worker_requests),
            ("controller_responses", self.controller_responses),
        ]

        stats = {}
        for name, queue in queues:
            stats[name] = {
                "pending": len(queue),
                "started": queue.started_job_registry.count,
                "finished": queue.finished_job_registry.count,
                "failed": queue.failed_job_registry.count,
                "deferred": queue.deferred_job_registry.count,
                "scheduled": queue.scheduled_job_registry.count,
            }

        return stats

    def claim_work(self, queue_names: list[str] | None = None) -> dict[str, Any] | None:
        """Claim next available work order from queues.

        Args:
            queue_names: List of queue names to check (in priority order).

        Returns:
            dict | None: Work order data or None if no work available.
        """
        if queue_names is None:
            queue_names = ["high_priority", "default", "low_priority"]

        for queue_name in queue_names:
            try:
                queue = get_queue(queue_name)
                job = queue.dequeue()

                if job:
                    # Return job data
                    return {
                        "job_id": job.id,
                        "queue": queue_name,
                        "data": job.args[0] if job.args else {},
                        "meta": job.meta,
                    }
            except Exception:
                continue

        return None
