# AgentVine QuickStart

## Phase 1: Multi-Worker Queue System

Phase 1 provides a functional multi-worker orchestration system with:
- Multiple Claude Code workers polling for tasks
- Redis-based priority queue system
- Session management (session_id ↔ task_id mapping)
- REST API for task management
- Human oversight via polling-based interface

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Redis (via Docker or local install)

## Quick Start with Docker Compose

### 1. Start the System

```bash
# Start all services (backend + redis + 3 workers)
docker compose up -d

# View logs
docker compose logs -f

# Check services are running
docker compose ps
```

### 2. Access the System

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redis**: localhost:6379

### 3. Create Your First Task

```bash
# Create a task via API
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add JWT-based authentication to the API",
    "task_type": "feature",
    "priority": "normal",
    "repository_url": "https://github.com/your/repo",
    "branch_name": "main"
  }'
```

### 4. Monitor the System

```bash
# List tasks
curl http://localhost:8000/api/v1/tasks

# Check queue status
curl http://localhost:8000/api/v1/queue/status

# List workers
curl http://localhost:8000/api/v1/workers

# List active sessions
curl http://localhost:8000/api/v1/sessions
```

### 5. Stop the System

```bash
# Stop all services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

## Local Development (Without Docker)

### 1. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally
redis-server
```

### 2. Start Backend

```bash
cd backend

# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start backend
uv run python -m app.main
```

Backend will start on `http://localhost:8000`

### 3. Start Workers

Open multiple terminals:

```bash
# Terminal 1
cd workers
uv sync
uv run python -m workers.main --name worker-1

# Terminal 2
uv run python -m workers.main --name worker-2

# Terminal 3
uv run python -m workers.main --name worker-3
```

### 4. Create Tasks

Use the curl commands above or the API docs at http://localhost:8000/docs

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  - Task API (create, list, get, update)                    │
│  - Worker API (register, heartbeat, status)                │
│  - Queue API (enqueue, claim, complete)                    │
│  - Session API (create, list, terminate)                   │
└────────────┬────────────────────┬──────────────────────────┘
             │                    │
             ▼                    ▼
┌─────────────────────┐  ┌──────────────────────────────────┐
│   SQLite (dev)      │  │        Redis + RQ                │
│  - Tasks            │  │  Queues:                         │
│  - Workers          │  │  - high_priority                 │
│  - Sessions         │  │  - default                       │
│  - Work Orders      │  │  - low_priority                  │
└─────────────────────┘  └────────────┬─────────────────────┘
                                      │
                          ┌───────────┴─────────────┐
                          ▼                         ▼
                ┌──────────────────┐      ┌──────────────────┐
                │   Worker 1       │      │   Worker N       │
                │ (Polling Loop)   │ ...  │ (Polling Loop)   │
                │                  │      │                  │
                │ - Claim work     │      │ - Claim work     │
                │ - Execute task   │      │ - Execute task   │
                │ - Send heartbeat │      │ - Send heartbeat │
                └──────────────────┘      └──────────────────┘
```

## Key Concepts

### Tasks
Development tasks with:
- Type (feature, bugfix, test, docs, etc.)
- Priority (low, normal, high)
- Status (queued, in_progress, completed, failed)
- Repository and branch information

### Workers
Claude Code instances that:
- Poll for work every 10 seconds
- Claim tasks atomically from priority queues
- Execute tasks (stub in Phase 1, full integration later)
- Send heartbeat every 30 seconds
- Register/deregister automatically

### Sessions
Session management for context preservation:
- Maps Claude Code session_id to task_id
- Tracks session age and activity
- Enables session reuse for related tasks
- Automatic termination based on idle time

### Queues
Priority-based work distribution:
- `high_priority` - Urgent tasks
- `default` - Normal tasks
- `low_priority` - Background tasks
- `worker_requests` - Worker questions (Phase 2)
- `controller_responses` - Human responses (Phase 2)

## Testing the System

### 1. Create Multiple Tasks

```bash
# Create 5 tasks with different priorities
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/tasks \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"Task $i\",
      \"description\": \"Test task number $i\",
      \"task_type\": \"feature\",
      \"priority\": \"normal\",
      \"repository_url\": \"https://github.com/test/repo\",
      \"branch_name\": \"main\"
    }"
done
```

### 2. Watch Workers Claim and Execute

```bash
# Watch worker logs
docker compose logs -f worker-1 worker-2 worker-3

# You should see:
# - Workers claiming tasks
# - Task execution (5 second stub)
# - Task completion
# - Return to idle state
```

### 3. Verify Task Completion

```bash
# Check all tasks are completed
curl http://localhost:8000/api/v1/tasks | jq '.[] | {title, status}'
```

### 4. Check Session Mappings

```bash
# See which sessions were created for tasks
curl http://localhost:8000/api/v1/sessions | jq '.[] | {session_id, task_id, status}'
```

## Phase 1 Status

✅ **Working:**
- Multi-worker coordination
- Priority-based queue system
- Task creation and management
- Worker registration and heartbeat
- Session mapping
- API endpoints for all operations

🔄 **Stub Implementation:**
- Task execution (currently 5-second sleep, needs Claude Code integration)
- Worker-human communication (queue exists, orchestrator in Phase 1.5)

📋 **Next Steps:**
- Event Orchestrator for human oversight
- Frontend for task creation and monitoring
- Actual Claude Code integration

## Troubleshooting

### Backend won't start
```bash
# Check Redis is running
docker compose ps redis

# Check backend logs
docker compose logs backend

# Verify database migration
cd backend && uv run alembic current
```

### Workers not claiming tasks
```bash
# Check workers are registered
curl http://localhost:8000/api/v1/workers

# Check queue status
curl http://localhost:8000/api/v1/queue/status

# Verify task was enqueued
curl http://localhost:8000/api/v1/tasks
```

### Clean slate restart
```bash
# Remove all containers and volumes
docker compose down -v

# Rebuild and start
docker compose up --build -d
```

## API Examples

See full API documentation at http://localhost:8000/docs

### Create Task
```bash
POST /api/v1/tasks
{
  "title": "string",
  "description": "string",
  "task_type": "feature|bugfix|test|docs",
  "priority": "low|normal|high",
  "repository_url": "string",
  "branch_name": "string"
}
```

### List Workers
```bash
GET /api/v1/workers
```

### Get Queue Status
```bash
GET /api/v1/queue/status
```

### List Sessions
```bash
GET /api/v1/sessions
```

## Performance Notes

- Workers poll every 10 seconds (configurable)
- Heartbeat sent every 30 seconds
- Task timeout: 1 hour
- Queue cleanup: Failed tasks after 7 days
- SQLite suitable for development, use PostgreSQL for production

## What's Next

Phase 1.5 will add:
- Event Orchestrator for worker-human communication
- Chat interface for human responses
- Session lifecycle management (keep-alive policies)

Phase 2 will add:
- LLM controller for intelligent routing
- Automated response generation
- Policy engine for decision-making
