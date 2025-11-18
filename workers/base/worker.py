"""Base worker implementation."""

import logging
import time
import uuid
from datetime import datetime
from typing import Any

from workers.base.api_client import APIClient
from workers.base.config import WorkerConfig

logger = logging.getLogger(__name__)


class Worker:
    """Base worker for executing tasks from the queue."""

    def __init__(self, config: WorkerConfig) -> None:
        """Initialize worker.

        Args:
            config: Worker configuration.
        """
        self.config = config
        self.worker_id: uuid.UUID | None = None
        self.session_id: str | None = None
        self.session_db_id: uuid.UUID | None = None
        self.current_task_id: uuid.UUID | None = None
        self.status = "idle"
        self.running = False

        # Initialize API client
        self.api_client = APIClient(config.api_url)

        # Timestamps
        self.last_heartbeat: datetime | None = None
        self.start_time = datetime.utcnow()

    def register(self) -> None:
        """Register worker with backend."""
        try:
            logger.info(f"Registering worker: {self.config.name}")
            data = self.api_client.register_worker(self.config.name)
            self.worker_id = uuid.UUID(data["id"])
            logger.info(f"Worker registered with ID: {self.worker_id}")
        except Exception as e:
            logger.error(f"Failed to register worker: {e}")
            raise

    def send_heartbeat(self) -> None:
        """Send heartbeat to backend."""
        if not self.worker_id:
            return

        try:
            self.api_client.send_heartbeat(self.worker_id, self.status)
            self.last_heartbeat = datetime.utcnow()
            logger.debug(f"Heartbeat sent: status={self.status}")
        except Exception as e:
            logger.warning(f"Failed to send heartbeat: {e}")

    def claim_work(self) -> dict[str, Any] | None:
        """Claim next available work order.

        Returns:
            dict | None: Work order data or None if no work available.
        """
        try:
            work = self.api_client.claim_work(self.config.queue_names or [])
            if work:
                logger.info(f"Claimed work: job_id={work['job_id']}, queue={work['queue']}")
            return work
        except Exception as e:
            logger.error(f"Failed to claim work: {e}")
            return None

    def execute_task(self, work_order: dict[str, Any]) -> None:
        """Execute a task.

        Args:
            work_order: Work order data from queue.
        """
        self.status = "busy"
        task_data = work_order["data"]
        task_id = uuid.UUID(task_data["task_id"])
        self.current_task_id = task_id

        logger.info(f"Executing task {task_id}: {task_data.get('title')}")

        try:
            # Update task status to in_progress
            self.api_client.update_task_status(task_id, "in_progress")

            # Create or reuse session
            if not self.session_id:
                # For now, use a simple session ID (will be replaced with actual Claude Code session)
                self.session_id = f"session-{self.worker_id}-{int(time.time())}"

            # Create session mapping in database
            try:
                session_data = self.api_client.create_session(
                    session_id=self.session_id,
                    worker_id=self.worker_id,
                    task_id=task_id,
                )
                self.session_db_id = uuid.UUID(session_data["id"])
                logger.info(f"Session created: {self.session_id}")
            except Exception as e:
                logger.warning(f"Session may already exist: {e}")

            # Execute the actual task
            # For Phase 1, this is a stub - will integrate Claude Code later
            logger.info(f"Task execution stub for: {task_data.get('title')}")
            logger.info(f"  Repository: {task_data.get('repository_url')}")
            logger.info(f"  Branch: {task_data.get('branch_name')}")
            logger.info(f"  Type: {task_data.get('task_type')}")

            # Simulate work
            time.sleep(5)

            # Mark task as completed
            self.api_client.update_task_status(task_id, "completed")
            logger.info(f"Task {task_id} completed successfully")

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            try:
                self.api_client.update_task_status(task_id, "failed")
            except Exception as update_error:
                logger.error(f"Failed to update task status: {update_error}")

        finally:
            self.status = "idle"
            self.current_task_id = None

    def run(self) -> None:
        """Main worker loop."""
        self.running = True
        logger.info(f"Worker {self.config.name} starting main loop")

        try:
            # Register with backend
            self.register()

            # Send initial heartbeat
            self.send_heartbeat()

            last_heartbeat_time = time.time()

            while self.running:
                try:
                    # Send heartbeat if needed
                    current_time = time.time()
                    if current_time - last_heartbeat_time >= self.config.heartbeat_interval:
                        self.send_heartbeat()
                        last_heartbeat_time = current_time

                    # Try to claim work
                    work = self.claim_work()

                    if work:
                        # Execute the task
                        self.execute_task(work)
                    else:
                        # No work available, wait before polling again
                        logger.debug(f"No work available, sleeping for {self.config.poll_interval}s")
                        time.sleep(self.config.poll_interval)

                except KeyboardInterrupt:
                    logger.info("Received shutdown signal")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    self.status = "error"
                    time.sleep(60)  # Back off on error

        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Gracefully shutdown worker."""
        logger.info("Shutting down worker")
        self.running = False

        # Wait for current task to complete if any
        if self.current_task_id:
            logger.info("Waiting for current task to complete...")
            # In a real implementation, we'd wait with a timeout

        # Deregister from backend
        if self.worker_id:
            try:
                self.api_client.deregister_worker(self.worker_id)
                logger.info("Worker deregistered")
            except Exception as e:
                logger.error(f"Failed to deregister worker: {e}")

        # Close API client
        self.api_client.close()

        logger.info("Worker shutdown complete")
