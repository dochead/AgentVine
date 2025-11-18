# Worker System Design

## Overview

Claude Code workers are autonomous agents that execute development tasks. Each worker runs in headless mode, polls the queue for work, executes tasks with full repository context, and communicates with the controller when clarification is needed.

## Worker Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Worker                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 Worker Manager                       │  │
│  │  - Lifecycle management                              │  │
│  │  - Health checks                                     │  │
│  │  - Configuration                                     │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                             │
│  ┌────────────▼─────────────────────────────────────────┐  │
│  │              Task Executor                           │  │
│  │  - Clone repository                                  │  │
│  │  - Execute task                                      │  │
│  │  - Run tests                                         │  │
│  │  - Create commits                                    │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                             │
│  ┌────────────▼─────────────────────────────────────────┐  │
│  │          Communication Layer                         │  │
│  │  - Queue polling                                     │  │
│  │  - Request clarification                             │  │
│  │  - Report status                                     │  │
│  └────────────┬─────────────────────────────────────────┘  │
└───────────────┼──────────────────────────────────────────────┘
                │
                ▼
         ┌────────────┐
         │   Redis    │
         │   Queue    │
         └────────────┘
```

## Worker Types

### 1. Feature Worker
**Purpose**: Implement new features and functionality

**Capabilities**:
- Write new code modules
- Integrate with existing codebase
- Add API endpoints
- Update database schemas
- Write tests for new features

**Configuration**:
```python
{
    "worker_type": "feature",
    "specializations": ["python", "typescript", "react", "fastapi"],
    "max_concurrent_tasks": 1,
    "permission_level": "supervised",
    "tools": ["code_write", "test_write", "db_migrate"]
}
```

### 2. Bugfix Worker
**Purpose**: Debug and fix issues

**Capabilities**:
- Analyze error logs
- Reproduce bugs
- Fix code issues
- Verify fixes with tests
- Update documentation

**Configuration**:
```python
{
    "worker_type": "bugfix",
    "specializations": ["debugging", "testing", "logging"],
    "max_concurrent_tasks": 1,
    "permission_level": "autonomous",
    "tools": ["code_write", "test_write", "log_analysis"]
}
```

### 3. Test Worker
**Purpose**: Write and execute tests

**Capabilities**:
- Write unit tests
- Write integration tests
- Execute test suites
- Analyze coverage
- Fix failing tests

**Configuration**:
```python
{
    "worker_type": "test",
    "specializations": ["pytest", "jest", "cypress"],
    "max_concurrent_tasks": 2,
    "permission_level": "autonomous",
    "tools": ["test_write", "test_execute", "coverage_analysis"]
}
```

### 4. Documentation Worker
**Purpose**: Generate and update documentation

**Capabilities**:
- Write README files
- Generate API documentation
- Update inline documentation
- Create user guides
- Document architecture

**Configuration**:
```python
{
    "worker_type": "docs",
    "specializations": ["markdown", "docstrings", "openapi"],
    "max_concurrent_tasks": 2,
    "permission_level": "autonomous",
    "tools": ["docs_write", "diagram_generation"]
}
```

### 5. Refactoring Worker
**Purpose**: Code improvement and optimization

**Capabilities**:
- Refactor code structure
- Optimize performance
- Improve code quality
- Update dependencies
- Apply best practices

**Configuration**:
```python
{
    "worker_type": "refactor",
    "specializations": ["code_quality", "performance", "patterns"],
    "max_concurrent_tasks": 1,
    "permission_level": "supervised",
    "tools": ["code_write", "test_execute", "linting"]
}
```

### 6. Review Worker
**Purpose**: Code review and analysis

**Capabilities**:
- Review pull requests
- Analyze code quality
- Check for security issues
- Verify best practices
- Provide feedback

**Configuration**:
```python
{
    "worker_type": "review",
    "specializations": ["code_review", "security", "best_practices"],
    "max_concurrent_tasks": 3,
    "permission_level": "autonomous",
    "tools": ["static_analysis", "security_scan", "lint_check"]
}
```

## Worker Lifecycle

### 1. Initialization

```python
class Worker:
    """AgentVine worker base class."""

    def __init__(self, config: WorkerConfig):
        self.id = str(uuid.uuid4())
        self.name = config.name
        self.worker_type = config.worker_type
        self.config = config
        self.status = WorkerStatus.INITIALIZING
        self.current_task = None

        # Initialize components
        self.queue_client = QueueClient(config.redis_url)
        self.api_client = APIClient(config.api_url, config.api_key)
        self.task_executor = TaskExecutor(self)

        # Register with backend
        self.register()

        self.status = WorkerStatus.IDLE

    def register(self):
        """Register worker with backend."""
        response = self.api_client.post("/api/v1/workers", {
            "id": self.id,
            "name": self.name,
            "worker_type": self.worker_type,
            "version": __version__,
            "config": self.config.to_dict(),
        })
        logger.info(f"Worker {self.id} registered successfully")
```

### 2. Work Loop

```python
def run(self):
    """Main worker loop."""
    logger.info(f"Worker {self.id} starting work loop")

    while True:
        try:
            # Send heartbeat
            self.send_heartbeat()

            # Claim work from queue
            work_order = self.claim_work()

            if work_order:
                # Execute task
                self.execute_work_order(work_order)
            else:
                # No work available, wait
                time.sleep(self.config.poll_interval)

        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
            break
        except Exception as e:
            logger.error(f"Error in work loop: {e}")
            self.status = WorkerStatus.ERROR
            time.sleep(60)  # Back off on error

    self.shutdown()

def claim_work(self) -> Optional[WorkOrder]:
    """Claim next available work order."""

    response = self.api_client.post("/api/v1/queue/claim", {
        "worker_id": self.id,
        "queue_names": self.config.queue_names,
    })

    if response.status_code == 200:
        return WorkOrder.from_dict(response.json())
    else:
        return None
```

### 3. Task Execution

```python
def execute_work_order(self, work_order: WorkOrder):
    """Execute a work order."""

    self.status = WorkerStatus.BUSY
    self.current_task = work_order.task_id

    try:
        logger.info(f"Executing work order {work_order.id}")

        # Create execution record
        execution = self.start_execution(work_order)

        # Execute task
        result = self.task_executor.execute(work_order)

        # Report completion
        self.complete_work_order(work_order, result)

        # Update execution record
        self.complete_execution(execution, result)

    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        self.fail_work_order(work_order, str(e))

    finally:
        self.status = WorkerStatus.IDLE
        self.current_task = None
```

### 4. Communication

```python
def request_clarification(
    self,
    work_order: WorkOrder,
    question: str,
    context: Dict[str, Any]
) -> str:
    """Request clarification from controller."""

    request = WorkerRequestMessage(
        id=str(uuid.uuid4()),
        worker_id=self.id,
        work_order_id=work_order.id,
        task_id=work_order.task_id,
        request_type="clarification",
        message=question,
        context=context,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(minutes=30),
        conversation_id=work_order.task_id,
    )

    # Send request to queue
    self.queue_client.enqueue_worker_request(request)

    # Wait for response
    response = self.wait_for_response(request.id, timeout=1800)

    return response.message

def wait_for_response(
    self,
    request_id: str,
    timeout: int = 1800
) -> ControllerResponseMessage:
    """Wait for controller response."""

    start_time = time.time()

    while time.time() - start_time < timeout:
        # Check for response in queue
        response = self.queue_client.check_for_response(
            self.id,
            request_id
        )

        if response:
            return response

        # Send heartbeat while waiting
        if time.time() % 30 == 0:
            self.send_heartbeat()

        time.sleep(5)

    raise TimeoutError(f"No response received for request {request_id}")
```

### 5. Shutdown

```python
def shutdown(self):
    """Gracefully shutdown worker."""

    logger.info(f"Worker {self.id} shutting down")

    # Complete current task if any
    if self.current_task:
        logger.warning("Task in progress, waiting for completion")
        # Wait for task to complete (with timeout)

    # Update status
    self.status = WorkerStatus.OFFLINE

    # Deregister from backend
    try:
        self.api_client.delete(f"/api/v1/workers/{self.id}")
    except Exception as e:
        logger.error(f"Error deregistering worker: {e}")

    logger.info("Worker shutdown complete")
```

## Task Executor

```python
class TaskExecutor:
    """Executes tasks in repository context."""

    def __init__(self, worker: Worker):
        self.worker = worker
        self.workspace_dir = Path(f"/tmp/agentvine/{worker.id}")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, work_order: WorkOrder) -> Dict[str, Any]:
        """Execute work order."""

        # Create working directory
        work_dir = self.workspace_dir / work_order.id
        work_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Clone repository
            repo_path = self.clone_repository(
                work_order.repository_url,
                work_order.branch_name,
                work_dir
            )

            # Execute task based on type
            if work_order.task_type == TaskType.FEATURE:
                result = self.execute_feature_task(work_order, repo_path)
            elif work_order.task_type == TaskType.BUGFIX:
                result = self.execute_bugfix_task(work_order, repo_path)
            elif work_order.task_type == TaskType.TEST:
                result = self.execute_test_task(work_order, repo_path)
            elif work_order.task_type == TaskType.DOCS:
                result = self.execute_docs_task(work_order, repo_path)
            elif work_order.task_type == TaskType.REFACTOR:
                result = self.execute_refactor_task(work_order, repo_path)
            elif work_order.task_type == TaskType.REVIEW:
                result = self.execute_review_task(work_order, repo_path)
            else:
                raise ValueError(f"Unknown task type: {work_order.task_type}")

            return result

        finally:
            # Cleanup
            if self.worker.config.cleanup_workspace:
                shutil.rmtree(work_dir, ignore_errors=True)

    def clone_repository(
        self,
        url: str,
        branch: str,
        dest: Path
    ) -> Path:
        """Clone repository to workspace."""

        repo_dir = dest / "repo"

        subprocess.run(
            ["git", "clone", "--branch", branch, "--depth", "1", url, str(repo_dir)],
            check=True,
            capture_output=True
        )

        return repo_dir

    def execute_feature_task(
        self,
        work_order: WorkOrder,
        repo_path: Path
    ) -> Dict[str, Any]:
        """Execute feature implementation task."""

        # Change to repo directory
        os.chdir(repo_path)

        # Implementation logic here
        # - Analyze requirements
        # - Write code
        # - Write tests
        # - Run tests
        # - Create commit

        # Example implementation
        files_modified = []
        tests_passed = True

        # If need clarification
        if self.needs_clarification():
            response = self.worker.request_clarification(
                work_order,
                "Should I use SQLAlchemy or raw SQL?",
                {"context": "database access pattern"}
            )
            # Process response and continue

        # Create commit
        self.create_commit("feat: implement user authentication")

        # Push changes
        if work_order.permission_level == PermissionLevel.AUTONOMOUS:
            self.push_changes(work_order.branch_name)
        else:
            # Create PR for review
            pr_url = self.create_pull_request(work_order)
            files_modified.append(("PR", pr_url))

        return {
            "status": "success",
            "files_modified": files_modified,
            "tests_passed": tests_passed,
            "output": "Feature implemented successfully"
        }
```

## Worker Configuration

```python
from dataclasses import dataclass
from typing import List

@dataclass
class WorkerConfig:
    """Worker configuration."""

    # Identity
    name: str
    worker_type: str

    # Connection
    redis_url: str
    api_url: str
    api_key: str

    # Behavior
    max_concurrent_tasks: int = 1
    poll_interval: int = 10  # seconds
    heartbeat_interval: int = 30  # seconds
    task_timeout: int = 3600  # seconds

    # Queues
    queue_names: List[str] = None

    # Capabilities
    specializations: List[str] = None
    tools: List[str] = None

    # Workspace
    workspace_dir: str = "/tmp/agentvine"
    cleanup_workspace: bool = True

    def __post_init__(self):
        if self.queue_names is None:
            # Default queue priority
            self.queue_names = ["high_priority", "default", "low_priority"]

        if self.specializations is None:
            self.specializations = []

        if self.tools is None:
            self.tools = []
```

## Monitoring & Health Checks

```python
def send_heartbeat(self):
    """Send heartbeat to backend."""

    try:
        self.api_client.post(f"/api/v1/workers/{self.id}/heartbeat", {
            "status": self.status.value,
            "current_tasks": 1 if self.current_task else 0,
            "metrics": self.get_metrics(),
        })
    except Exception as e:
        logger.error(f"Failed to send heartbeat: {e}")

def get_metrics(self) -> Dict[str, Any]:
    """Collect worker metrics."""

    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_mb": psutil.virtual_memory().used / 1024 / 1024,
        "disk_usage_gb": psutil.disk_usage("/").used / 1024 / 1024 / 1024,
        "uptime_seconds": time.time() - self.start_time,
    }
```

## Docker Deployment

```dockerfile
# Dockerfile.worker
FROM python:3.13-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI (placeholder)
RUN curl -L https://claude-code.anthropic.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy worker code
COPY workers/ /app/workers/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create workspace
RUN mkdir -p /tmp/agentvine

# Run worker
CMD ["python", "-m", "workers.main"]
```

```yaml
# docker-compose.worker.yml
services:
  feature-worker-1:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      - WORKER_NAME=feature-worker-1
      - WORKER_TYPE=feature
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - API_URL=http://api:8000
      - API_KEY=${WORKER_API_KEY}
    depends_on:
      - redis
      - api
    restart: unless-stopped

  bugfix-worker-1:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      - WORKER_NAME=bugfix-worker-1
      - WORKER_TYPE=bugfix
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - API_URL=http://api:8000
      - API_KEY=${WORKER_API_KEY}
    depends_on:
      - redis
      - api
    restart: unless-stopped
```

## Security

### Sandboxing
- Each worker runs in isolated Docker container
- Resource limits (CPU, memory, disk)
- Network restrictions
- Read-only file system (except workspace)

### Authentication
- Workers authenticate with API keys
- API keys scoped to worker type and permissions
- Keys rotated regularly

### Authorization
- Workers can only claim tasks matching their type
- Permission levels enforced (autonomous, supervised, human-required)
- Sensitive operations require approval

## Testing

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def worker_config():
    return WorkerConfig(
        name="test-worker",
        worker_type="feature",
        redis_url="redis://localhost:6379/0",
        api_url="http://localhost:8000",
        api_key="test-key"
    )

@pytest.fixture
def worker(worker_config):
    return Worker(worker_config)

def test_worker_initialization(worker):
    assert worker.status == WorkerStatus.IDLE
    assert worker.current_task is None

def test_claim_work(worker):
    with patch.object(worker.api_client, 'post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "work_order_id": "test-order",
            "task_id": "test-task",
        }

        work_order = worker.claim_work()
        assert work_order is not None
```
