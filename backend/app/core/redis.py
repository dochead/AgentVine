"""Redis connection and queue configuration."""

from redis import Redis
from rq import Queue

from app.core.config import settings

# Create Redis connection
redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_keepalive=True,
    health_check_interval=30,
)

# Create RQ queues
high_priority_queue = Queue("high_priority", connection=redis_client)
default_queue = Queue("default", connection=redis_client)
low_priority_queue = Queue("low_priority", connection=redis_client)
worker_requests_queue = Queue("worker_requests", connection=redis_client)
controller_responses_queue = Queue("controller_responses", connection=redis_client)


def get_redis() -> Redis:
    """Get Redis client instance.

    Returns:
        Redis: Redis client.
    """
    return redis_client


def get_queue(name: str) -> Queue:
    """Get RQ queue by name.

    Args:
        name: Queue name.

    Returns:
        Queue: RQ queue instance.

    Raises:
        ValueError: If queue name is invalid.
    """
    queues = {
        "high_priority": high_priority_queue,
        "default": default_queue,
        "low_priority": low_priority_queue,
        "worker_requests": worker_requests_queue,
        "controller_responses": controller_responses_queue,
    }

    if name not in queues:
        raise ValueError(f"Invalid queue name: {name}")

    return queues[name]
