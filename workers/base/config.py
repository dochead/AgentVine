"""Worker configuration."""

from dataclasses import dataclass


@dataclass
class WorkerConfig:
    """Configuration for a worker instance."""

    # Identity
    name: str
    worker_id: str | None = None  # Set after registration

    # Connection
    api_url: str = "http://localhost:8000"
    redis_url: str = "redis://localhost:6379/0"

    # Behavior
    poll_interval: int = 10  # seconds between polls
    heartbeat_interval: int = 30  # seconds between heartbeats
    task_timeout: int = 3600  # seconds (1 hour)

    # Queues to poll (in priority order)
    queue_names: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.queue_names is None:
            self.queue_names = ["high_priority", "default", "low_priority"]
