# Queue System Design

## Overview

The AgentVine queue system uses RQ (Redis Queue) with Redis as the backend to manage work distribution, message passing between workers and controllers, and asynchronous task execution.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Queue Manager Service                      │  │
│  │  - enqueue_task()                                     │  │
│  │  - claim_work()                                       │  │
│  │  - complete_work()                                    │  │
│  │  - fail_work()                                        │  │
│  └────────────────┬─────────────────────────────────────┘  │
└───────────────────┼─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   Redis + RQ System                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ high_priority│  │   default    │  │ low_priority │     │
│  │    Queue     │  │    Queue     │  │    Queue     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────────────────────────┐   │
│  │worker_requests│  │  controller_responses          │   │
│  │    Queue     │  │       Queue                     │   │
│  └──────────────┘  └──────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Dead Letter Queue (DLQ)                   │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────┬──────────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│  Worker Pool 1   │  │  Worker Pool N   │
│  (Consumers)     │  │  (Consumers)     │
└──────────────────┘  └──────────────────┘
```

## Queue Types

### 1. Task Queues

#### high_priority
- **Purpose**: Critical tasks requiring immediate execution
- **TTL**: 1 hour
- **Max retries**: 3
- **Examples**: Production bugs, security fixes, deployment issues

#### default
- **Purpose**: Normal development tasks
- **TTL**: 2 hours
- **Max retries**: 3
- **Examples**: Feature implementation, refactoring, documentation

#### low_priority
- **Purpose**: Background tasks, non-urgent work
- **TTL**: 4 hours
- **Max retries**: 2
- **Examples**: Code cleanup, optimization, batch updates

### 2. Communication Queues

#### worker_requests
- **Purpose**: Worker questions and clarification requests
- **TTL**: 30 minutes
- **Max retries**: 1
- **Flow**: Worker → Queue → Controller

#### controller_responses
- **Purpose**: Controller responses to workers
- **TTL**: 30 minutes
- **Max retries**: 1
- **Flow**: Controller → Queue → Worker

### 3. Special Queues

#### dead_letter_queue
- **Purpose**: Failed tasks after max retries
- **TTL**: 7 days
- **Retention**: Permanent until manually cleared
- **Monitoring**: Alert on new entries

## Message Structure

### Work Order Message

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

class TaskType(str, Enum):
    FEATURE = "feature"
    BUGFIX = "bugfix"
    TEST = "test"
    DOCS = "docs"
    REFACTOR = "refactor"
    REVIEW = "review"

class PermissionLevel(str, Enum):
    AUTONOMOUS = "autonomous"
    SUPERVISED = "supervised"
    HUMAN_REQUIRED = "human_required"

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class WorkOrderMessage:
    """Work order message structure."""

    # Identity
    id: str  # UUID
    task_id: str  # UUID
    work_order_id: str  # UUID

    # Classification
    task_type: TaskType
    permission_level: PermissionLevel
    priority: Priority

    # Context
    repository_url: str
    branch_name: str
    issue_number: Optional[int] = None
    pr_number: Optional[int] = None
    files: List[str] = []

    # Instructions
    title: str
    description: str
    requirements: List[str] = []

    # Metadata
    created_at: datetime
    timeout_seconds: int = 3600
    max_retries: int = 3
    retry_count: int = 0

    # Additional data
    payload: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for Redis."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "work_order_id": self.work_order_id,
            "task_type": self.task_type.value,
            "permission_level": self.permission_level.value,
            "priority": self.priority.value,
            "repository_url": self.repository_url,
            "branch_name": self.branch_name,
            "issue_number": self.issue_number,
            "pr_number": self.pr_number,
            "files": self.files,
            "title": self.title,
            "description": self.description,
            "requirements": self.requirements,
            "created_at": self.created_at.isoformat(),
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "payload": self.payload,
            "metadata": self.metadata,
        }
```

### Worker Request Message

```python
@dataclass
class WorkerRequestMessage:
    """Worker request/question message."""

    id: str  # UUID
    worker_id: str  # UUID
    work_order_id: str  # UUID
    task_id: str  # UUID

    request_type: str  # "clarification", "approval", "question"
    message: str
    context: Dict[str, Any]

    created_at: datetime
    expires_at: datetime

    # For threaded conversations
    conversation_id: str
    parent_message_id: Optional[str] = None
```

### Controller Response Message

```python
@dataclass
class ControllerResponseMessage:
    """Controller response to worker request."""

    id: str  # UUID
    request_id: str  # UUID (original worker request)
    worker_id: str  # UUID
    work_order_id: str  # UUID

    response_type: str  # "answer", "instruction", "approval", "rejection"
    message: str
    instructions: List[str] = []

    # Response metadata
    generated_by: str  # "human" or "automated"
    responder_id: Optional[str] = None  # User ID if human

    created_at: datetime
```

## Queue Operations

### Enqueueing Tasks

```python
from rq import Queue
from redis import Redis
import json

class QueueManager:
    """Manage queue operations."""

    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)
        self.high_priority = Queue("high_priority", connection=self.redis)
        self.default = Queue("default", connection=self.redis)
        self.low_priority = Queue("low_priority", connection=self.redis)
        self.worker_requests = Queue("worker_requests", connection=self.redis)
        self.controller_responses = Queue("controller_responses", connection=self.redis)

    def enqueue_task(
        self,
        work_order: WorkOrderMessage,
        priority: Priority = Priority.NORMAL
    ) -> str:
        """Enqueue a work order."""

        # Select queue based on priority
        if priority == Priority.CRITICAL or priority == Priority.HIGH:
            queue = self.high_priority
        elif priority == Priority.LOW:
            queue = self.low_priority
        else:
            queue = self.default

        # Enqueue with metadata
        job = queue.enqueue(
            "worker.execute_task",
            work_order.to_dict(),
            job_timeout=work_order.timeout_seconds,
            result_ttl=86400,  # Keep results for 24 hours
            failure_ttl=604800,  # Keep failures for 7 days
            job_id=work_order.work_order_id,
            meta={
                "task_id": work_order.task_id,
                "task_type": work_order.task_type.value,
                "permission_level": work_order.permission_level.value,
            }
        )

        return job.id

    def enqueue_worker_request(
        self,
        request: WorkerRequestMessage
    ) -> str:
        """Enqueue worker request for controller."""

        job = self.worker_requests.enqueue(
            "controller.process_request",
            request.to_dict(),
            job_timeout=1800,  # 30 minutes
            result_ttl=3600,
            job_id=request.id,
        )

        return job.id

    def enqueue_controller_response(
        self,
        response: ControllerResponseMessage
    ) -> str:
        """Enqueue controller response for worker."""

        job = self.controller_responses.enqueue(
            "worker.receive_response",
            response.to_dict(),
            job_timeout=300,  # 5 minutes
            result_ttl=3600,
            job_id=response.id,
        )

        return job.id
```

### Claiming Work (Worker Side)

```python
from rq import Worker
from rq.job import Job

class AgentVineWorker:
    """Worker that claims and executes tasks."""

    def __init__(self, worker_id: str, redis_url: str):
        self.worker_id = worker_id
        self.redis = Redis.from_url(redis_url)
        self.queues = [
            Queue("high_priority", connection=self.redis),
            Queue("default", connection=self.redis),
            Queue("low_priority", connection=self.redis),
        ]

    def claim_work(self) -> Optional[Job]:
        """Claim next available work order."""

        # Check queues in priority order
        for queue in self.queues:
            job = queue.dequeue()
            if job:
                # Atomically claim the job
                self.redis.hset(
                    f"worker:{self.worker_id}:current_job",
                    "job_id", job.id
                )
                return job

        return None

    def execute_task(self, work_order_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Execute work order."""

        work_order = WorkOrderMessage.from_dict(work_order_dict)

        # Execute task logic here
        # ...

        result = {
            "status": "success",
            "output": "Task completed",
            "files_modified": [],
        }

        return result
```

### Monitoring Queue Status

```python
class QueueMonitor:
    """Monitor queue health and statistics."""

    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics for all queues."""

        stats = {}

        for queue_name in ["high_priority", "default", "low_priority"]:
            queue = Queue(queue_name, connection=self.redis)

            stats[queue_name] = {
                "pending": len(queue),
                "started": queue.started_job_registry.count,
                "finished": queue.finished_job_registry.count,
                "failed": queue.failed_job_registry.count,
                "deferred": queue.deferred_job_registry.count,
                "scheduled": queue.scheduled_job_registry.count,
            }

        return stats

    def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""

        workers = Worker.all(connection=self.redis)

        return {
            "total": len(workers),
            "idle": len([w for w in workers if w.state == "idle"]),
            "busy": len([w for w in workers if w.state == "busy"]),
            "suspended": len([w for w in workers if w.state == "suspended"]),
        }
```

## Queue Configuration

### Redis Configuration

```python
# config/redis.py

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": None,  # Set in production
    "socket_timeout": 5,
    "socket_connect_timeout": 5,
    "socket_keepalive": True,
    "health_check_interval": 30,
}

# Connection pooling
REDIS_POOL_CONFIG = {
    "max_connections": 50,
    "decode_responses": True,
}
```

### Queue Configuration

```python
# config/queue.py

QUEUE_CONFIG = {
    "high_priority": {
        "default_timeout": 3600,
        "result_ttl": 86400,
        "failure_ttl": 604800,
    },
    "default": {
        "default_timeout": 7200,
        "result_ttl": 86400,
        "failure_ttl": 604800,
    },
    "low_priority": {
        "default_timeout": 14400,
        "result_ttl": 43200,
        "failure_ttl": 604800,
    },
}
```

### Worker Configuration

```python
# config/worker.py

WORKER_CONFIG = {
    "max_jobs": None,  # Unlimited
    "burst": False,  # Continuous processing
    "logging_level": "INFO",
    "job_monitoring_interval": 30,
    "disable_default_exception_handler": False,
    "max_idle_time": None,  # Never stop
}
```

## Error Handling

### Retry Strategy

```python
from rq.job import Job
from rq import Retry

# Exponential backoff retry
retry = Retry(max=3, interval=[60, 180, 600])  # 1min, 3min, 10min

job = queue.enqueue(
    "worker.execute_task",
    work_order.to_dict(),
    retry=retry
)
```

### Dead Letter Queue

```python
def handle_failed_job(job: Job, exc_type, exc_value, traceback):
    """Move failed job to DLQ."""

    dlq = Queue("dead_letter_queue", connection=job.connection)

    dlq.enqueue(
        "admin.process_failed_job",
        {
            "original_job_id": job.id,
            "queue": job.origin,
            "exception": str(exc_value),
            "traceback": traceback,
            "work_order": job.args[0] if job.args else None,
        },
        job_timeout=3600,
        result_ttl=-1,  # Keep forever
    )
```

## Performance Optimization

### Connection Pooling

```python
from redis.connection import ConnectionPool

pool = ConnectionPool.from_url(
    REDIS_URL,
    max_connections=50,
    decode_responses=True
)

redis_conn = Redis(connection_pool=pool)
```

### Batch Operations

```python
def enqueue_batch(work_orders: List[WorkOrderMessage]):
    """Enqueue multiple work orders efficiently."""

    with queue.connection.pipeline() as pipe:
        for work_order in work_orders:
            queue.enqueue(
                "worker.execute_task",
                work_order.to_dict(),
                pipeline=pipe
            )
        pipe.execute()
```

### Queue Prioritization

```python
# Workers process queues in order
worker = Worker(
    ["high_priority", "default", "low_priority"],
    connection=redis_conn
)

# Always check high_priority first
worker.work()
```

## Monitoring & Alerts

### RQ Dashboard

```bash
# Install
pip install rq-dashboard

# Run
rq-dashboard --redis-url redis://localhost:6379/0
```

**Dashboard URL**: `http://localhost:9181`

### Custom Monitoring

```python
import logging

logger = logging.getLogger(__name__)

def monitor_queue_depth():
    """Alert on high queue depth."""

    monitor = QueueMonitor(REDIS_URL)
    stats = monitor.get_queue_stats()

    for queue_name, queue_stats in stats.items():
        if queue_stats["pending"] > 100:
            logger.warning(
                f"Queue {queue_name} has {queue_stats['pending']} pending jobs"
            )

        if queue_stats["failed"] > 10:
            logger.error(
                f"Queue {queue_name} has {queue_stats['failed']} failed jobs"
            )
```

### Metrics Collection

```python
from prometheus_client import Counter, Gauge, Histogram

# Metrics
jobs_enqueued = Counter("jobs_enqueued_total", "Total jobs enqueued", ["queue"])
jobs_completed = Counter("jobs_completed_total", "Total jobs completed", ["queue"])
jobs_failed = Counter("jobs_failed_total", "Total jobs failed", ["queue"])
queue_depth = Gauge("queue_depth", "Current queue depth", ["queue"])
job_duration = Histogram("job_duration_seconds", "Job execution time", ["queue"])
```

## Testing

### Unit Tests

```python
import pytest
from fakeredis import FakeRedis

@pytest.fixture
def mock_redis():
    return FakeRedis()

@pytest.fixture
def queue_manager(mock_redis):
    return QueueManager(redis_client=mock_redis)

def test_enqueue_task(queue_manager):
    work_order = WorkOrderMessage(
        id="test-id",
        task_id="task-1",
        work_order_id="order-1",
        task_type=TaskType.FEATURE,
        permission_level=PermissionLevel.AUTONOMOUS,
        priority=Priority.NORMAL,
        repository_url="https://github.com/test/repo",
        branch_name="main",
        title="Test task",
        description="Test description",
        created_at=datetime.now(),
    )

    job_id = queue_manager.enqueue_task(work_order)
    assert job_id == work_order.work_order_id
```

## Security

### Authentication
- Workers authenticate with API keys
- API keys stored in Redis with expiration
- Rotate keys regularly

### Authorization
- Workers can only claim appropriate tasks
- Permission levels enforced
- Audit log of all queue operations

### Data Protection
- Sensitive data encrypted before enqueueing
- Redis configured with AUTH password
- TLS for Redis connections in production

## Deployment

### Development
```bash
# Start Redis
redis-server

# Start RQ worker
rq worker high_priority default low_priority --url redis://localhost:6379/0

# Start RQ Dashboard
rq-dashboard --redis-url redis://localhost:6379/0
```

### Production

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  rq-worker:
    build: .
    command: rq worker high_priority default low_priority
    environment:
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - redis
    deploy:
      replicas: 5
```

## Future Enhancements

1. **Queue Sharding**: Distribute queues across multiple Redis instances
2. **Priority Queues**: More granular priority levels
3. **Scheduled Tasks**: Cron-like scheduling for recurring tasks
4. **Task Chaining**: Dependencies between tasks
5. **Dynamic Worker Scaling**: Auto-scale based on queue depth
6. **Advanced Monitoring**: Real-time dashboards with Grafana
7. **Queue Analytics**: Historical analysis of queue performance
