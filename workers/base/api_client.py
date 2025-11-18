"""API client for worker-backend communication."""

import uuid
from typing import Any

import httpx


class APIClient:
    """Client for communicating with AgentVine backend API."""

    def __init__(self, base_url: str) -> None:
        """Initialize API client.

        Args:
            base_url: Base URL of the backend API.
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def register_worker(self, name: str) -> dict[str, Any]:
        """Register worker with backend.

        Args:
            name: Worker name.

        Returns:
            dict: Worker data including ID.

        Raises:
            httpx.HTTPError: If registration fails.
        """
        response = self.client.post(
            f"{self.base_url}/api/v1/workers",
            json={"name": name},
        )
        response.raise_for_status()
        return response.json()

    def send_heartbeat(self, worker_id: uuid.UUID, status: str) -> dict[str, Any]:
        """Send heartbeat to backend.

        Args:
            worker_id: Worker UUID.
            status: Worker status.

        Returns:
            dict: Updated worker data.

        Raises:
            httpx.HTTPError: If heartbeat fails.
        """
        response = self.client.post(
            f"{self.base_url}/api/v1/workers/{worker_id}/heartbeat",
            json={"status": status},
        )
        response.raise_for_status()
        return response.json()

    def claim_work(self, queue_names: list[str]) -> dict[str, Any] | None:
        """Claim work from queue.

        Args:
            queue_names: List of queue names to check.

        Returns:
            dict | None: Work order data or None if no work available.

        Raises:
            httpx.HTTPError: If claim request fails.
        """
        response = self.client.post(
            f"{self.base_url}/api/v1/queue/claim",
            params={"queue_names": queue_names},
        )
        response.raise_for_status()

        data = response.json()
        return data if data else None

    def update_task_status(
        self, task_id: uuid.UUID, status: str
    ) -> dict[str, Any]:
        """Update task status.

        Args:
            task_id: Task UUID.
            status: New status.

        Returns:
            dict: Updated task data.

        Raises:
            httpx.HTTPError: If update fails.
        """
        response = self.client.patch(
            f"{self.base_url}/api/v1/tasks/{task_id}",
            json={"status": status},
        )
        response.raise_for_status()
        return response.json()

    def create_session(
        self,
        session_id: str,
        worker_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Create session mapping.

        Args:
            session_id: Claude Code session ID.
            worker_id: Worker UUID.
            task_id: Task UUID.

        Returns:
            dict: Session data.

        Raises:
            httpx.HTTPError: If creation fails.
        """
        response = self.client.post(
            f"{self.base_url}/api/v1/sessions",
            json={
                "session_id": session_id,
                "worker_id": str(worker_id),
                "task_id": str(task_id),
            },
        )
        response.raise_for_status()
        return response.json()

    def session_heartbeat(self, session_id: uuid.UUID) -> dict[str, Any]:
        """Update session activity.

        Args:
            session_id: Session UUID (database ID, not Claude session ID).

        Returns:
            dict: Updated session data.

        Raises:
            httpx.HTTPError: If update fails.
        """
        response = self.client.post(
            f"{self.base_url}/api/v1/sessions/{session_id}/heartbeat"
        )
        response.raise_for_status()
        return response.json()

    def deregister_worker(self, worker_id: uuid.UUID) -> None:
        """Deregister worker from backend.

        Args:
            worker_id: Worker UUID.

        Raises:
            httpx.HTTPError: If deregistration fails.
        """
        response = self.client.delete(
            f"{self.base_url}/api/v1/workers/{worker_id}"
        )
        response.raise_for_status()

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()
