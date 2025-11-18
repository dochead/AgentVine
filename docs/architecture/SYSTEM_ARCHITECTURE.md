# AgentVine System Architecture

## Overview

AgentVine is a hybrid agent/human event-driven orchestration system for software development workflows. It uses multiple Claude Code workers coordinated by controllers (human or LLM) to execute development tasks collaboratively.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Chat Interface                          │
│                  (React + WebSocket + Shad.cn)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Chat Controller                            │
│              (Message Routing + Decision Logic)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Routing    │  │   Policies   │  │   Context    │         │
│  │   Engine     │  │   Engine     │  │   Manager    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     API      │  │   Services   │  │    Models    │         │
│  │   Endpoints  │  │   (Business) │  │  (SQLAlchemy)│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────┬─────────────────────────────┘
             │                    │
             ▼                    ▼
┌─────────────────────┐  ┌─────────────────────────────────────┐
│    PostgreSQL       │  │         Redis + RQ                  │
│    (Production)     │  │      (Queue System)                 │
│    SQLite (Dev)     │  │                                     │
└─────────────────────┘  └──────────┬──────────────────────────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
              ┌──────────────────┐  ┌──────────────────┐
              │  Worker Pool 1   │  │  Worker Pool N   │
              │ (Claude Code)    │  │ (Claude Code)    │
              │  ┌──────────┐   │  │  ┌──────────┐   │
              │  │ Feature  │   │  │  │ Bugfix   │   │
              │  │ Worker   │   │  │  │ Worker   │   │
              │  └──────────┘   │  │  └──────────┘   │
              │  ┌──────────┐   │  │  ┌──────────┐   │
              │  │   Test   │   │  │  │   Doc    │   │
              │  │  Worker  │   │  │  │  Worker  │   │
              │  └──────────┘   │  │  └──────────┘   │
              └──────────────────┘  └──────────────────┘
```

## Core Components

### 1. Chat Interface (Frontend)

**Technology Stack:**
- React 19 with TypeScript
- Vite for build tooling
- Shad.cn component library
- TailwindCSS for styling
- WebSocket for real-time communication
- TanStack Query for data fetching
- Zustand for state management

**Responsibilities:**
- Display worker requests and status updates
- Accept human input when needed
- Show real-time queue status
- Display system state and active workers
- Provide visibility into development process

**Key Features:**
- Streaming chat interface
- Real-time worker status
- Queue visualization
- Task assignment UI
- Context viewer
- Metrics dashboard

### 2. Chat Controller

**Technology Stack:**
- Python 3.13
- FastAPI for HTTP endpoints
- WebSocket for real-time communication
- Redis for caching and pub/sub
- SQLAlchemy for state persistence

**Components:**

#### Routing Engine
- Analyzes incoming worker messages
- Extracts metadata (task type, priority, permissions)
- Routes to appropriate handler (human or automated)
- Maintains routing history

#### Policies Engine
- Decision logic for automation vs. human intervention
- Permission-based routing rules
- Priority-based escalation
- Context-aware decision making

#### Context Manager
- Maintains design documents
- Stores implementation plans
- Tracks work assignments
- Provides repository context
- Manages shared knowledge base

### 3. Backend API (FastAPI)

**Technology Stack:**
- FastAPI 0.109.0
- SQLAlchemy (async) with PostgreSQL/SQLite
- Pydantic for validation
- Alembic for migrations
- JWT for authentication
- Redis for caching

**API Modules:**

#### Core Endpoints
- `/health` - Health checks
- `/about` - System information
- `/auth/*` - Authentication
- `/workers/*` - Worker management
- `/tasks/*` - Task operations
- `/queue/*` - Queue operations
- `/chat/*` - Chat operations
- `/context/*` - Context management

#### Services Layer
- Worker orchestration
- Task scheduling
- Queue management
- Context management
- Notification service
- Analytics service

### 4. Queue System (RQ + Redis)

**Technology Stack:**
- RQ (Redis Queue)
- Redis 7.x
- RQ Dashboard for monitoring

**Queue Types:**
- `high_priority` - Critical tasks
- `default` - Normal tasks
- `low_priority` - Background tasks
- `worker_requests` - Worker clarification requests
- `controller_responses` - Controller responses

**Message Structure:**
```json
{
  "id": "uuid",
  "task_type": "feature|bugfix|test|docs|refactor|review",
  "permission_level": "autonomous|supervised|human-required",
  "priority": "high|normal|low",
  "worker_id": "uuid",
  "context": {
    "repository": "url",
    "branch": "name",
    "files": ["paths"],
    "issue_id": "number"
  },
  "payload": {},
  "metadata": {},
  "created_at": "iso8601",
  "timeout": 3600
}
```

### 5. Worker System (Claude Code)

**Worker Types:**

1. **Feature Worker** - Implements new features
2. **Bugfix Worker** - Debugs and fixes issues
3. **Test Worker** - Writes and executes tests
4. **Documentation Worker** - Generates documentation
5. **Refactoring Worker** - Code improvement
6. **Review Worker** - Code review and analysis

**Worker Lifecycle:**
1. Poll queue for work orders
2. Claim work order (atomic operation)
3. Execute task with full repo context
4. Request clarification if needed (post to queue)
5. Wait for response (blocking on queue)
6. Complete task
7. Report results and status
8. Return to polling

**Worker Configuration:**
```yaml
worker:
  id: uuid
  type: feature|bugfix|test|docs|refactor|review
  max_concurrent_tasks: 1
  timeout: 3600
  permissions:
    - code_write
    - test_execute
    - docs_write
  context_window: 200000
  specializations:
    - python
    - typescript
    - react
```

### 6. Database Schema

**Core Tables:**
- `users` - User accounts
- `workers` - Worker registry
- `tasks` - Task definitions
- `work_orders` - Queued work
- `executions` - Execution logs
- `chat_messages` - Chat history
- `context_documents` - Shared context
- `worker_assignments` - Active assignments

See `DATABASE_SCHEMA.md` for detailed schema.

## Data Flow

### Task Execution Flow

```
1. Task Created (Human or System)
   └─> Task stored in database
       └─> Work order enqueued to Redis

2. Worker Claims Work Order
   └─> Atomic pop from Redis queue
       └─> Assignment recorded in database
           └─> Worker begins execution

3. Worker Execution
   ├─> Success Path:
   │   └─> Results posted to queue
   │       └─> Controller validates
   │           └─> Task marked complete
   │
   └─> Clarification Needed Path:
       └─> Question posted to queue
           └─> Controller routes (auto or human)
               ├─> Automated: Generate response
               │   └─> Response enqueued
               │       └─> Worker continues
               │
               └─> Human Required: Display in chat
                   └─> Human responds
                       └─> Response enqueued
                           └─> Worker continues
```

### Message Routing Flow

```
Worker Message
  │
  ▼
Controller Receives Message
  │
  ├─> Extract Metadata
  │   ├─> task_type
  │   ├─> permission_level
  │   ├─> priority
  │   └─> context
  │
  ▼
Policy Engine Evaluates
  │
  ├─> autonomous + simple → Automated Response
  │   └─> LLM generates response
  │       └─> Enqueue to worker
  │
  ├─> supervised → Human Review
  │   └─> Display in chat
  │       └─> Human approves/modifies
  │           └─> Enqueue to worker
  │
  └─> human-required → Human Interaction
      └─> Display in chat
          └─> Human responds
              └─> Enqueue to worker
```

## Security Architecture

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Permission levels: admin, developer, viewer
- Worker authentication via API keys

### Sandboxing
- Workers run in isolated Docker containers
- Resource limits (CPU, memory, disk)
- Network restrictions
- File system isolation

### Permission System
- Task-level permissions
- Operation-level permissions
- Human approval requirements:
  - Database migrations
  - Deployments
  - Security-sensitive changes
  - Configuration changes

### API Security
- Rate limiting (per user, per endpoint)
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (sanitization)
- CORS configuration

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers (scale via load balancer)
- Multiple worker pools
- Redis clustering for queue
- PostgreSQL replication

### Performance Targets
- API response time: < 50ms (p95)
- Queue throughput: > 1000 tasks/minute
- Worker startup: < 5 seconds
- WebSocket latency: < 100ms

### Resource Management
- Worker pool auto-scaling
- Queue priority management
- Task timeout handling
- Dead letter queues

## Monitoring & Observability

### Metrics
- API request/response metrics
- Queue depth and throughput
- Worker utilization
- Task completion rates
- Error rates

### Logging
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation
- Request tracing (correlation IDs)

### Dashboards
- RQ Dashboard for queue monitoring
- Custom metrics dashboard
- Worker health dashboard
- Task analytics

## Deployment Architecture

### Development
- SQLite database
- Local Redis
- Single worker
- Hot reload enabled

### Production
- PostgreSQL (managed service)
- Redis cluster (managed service)
- Multiple worker pools
- Load-balanced API servers
- Docker + Kubernetes orchestration

## Technology Decisions

### Why FastAPI?
- Modern async support
- Automatic OpenAPI documentation
- High performance
- Type safety with Pydantic
- Active ecosystem

### Why RQ?
- Simple Python-native queue
- Good monitoring (RQ Dashboard)
- Reliable with Redis
- Easy to understand and debug

### Why React?
- Rich ecosystem
- Component reusability
- Strong TypeScript support
- Excellent tooling (Vite)

### Why SQLAlchemy?
- Mature ORM
- Async support
- Type safety
- Migration support (Alembic)

## Future Enhancements

### Phase 2
- Multi-repository support
- Advanced worker specialization
- Worker collaboration protocols

### Phase 3
- ML-based routing decisions
- GitHub/GitLab integration
- Distributed worker pools

### Phase 4
- Advanced context sharing
- Intelligent task decomposition
- Autonomous planning
