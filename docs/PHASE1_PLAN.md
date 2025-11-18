# AgentVine Phase 1 Implementation Plan

## Executive Summary

Phase 1 focuses on building a **multi-worker, event-driven queueing system** to manage multiple headless Claude Code instances. The system will coordinate work distribution, maintain session-to-task mappings, and provide a human chat interface for oversight. The LLM controller layer is explicitly **deferred to Phase 2+**.

## Phase 1 Core Requirements

### 1. Multi-Worker Queue System
Build a robust queue-based orchestration system that can:
- Manage multiple headless Claude Code worker instances simultaneously
- Distribute work orders to available workers via priority queues
- Track worker status and health via heartbeat mechanism
- Handle worker registration, lifecycle, and graceful shutdown

### 2. Event Orchestrator
Create an event-driven orchestrator that:
- Reads incoming messages from workers (questions, status updates, completion)
- Maintains a mapping of Claude session IDs to task IDs
- Keeps sessions alive to maintain context advantages
- Intelligently ends sessions when appropriate (task complete, timeout, or resource constraints)
- Routes all worker requests to the human chat interface (no LLM decision-making in Phase 1)

### 3. Session Management
Implement session lifecycle management that:
- Maps each Claude Code session ID to a specific task in the task list
- Tracks session age, activity, and context usage
- Preserves sessions to maintain conversation context and repository understanding
- Terminates sessions based on configurable policies (max idle time, task completion, resource limits)

### 4. Human Chat Interface (Pass-Through)
Build a chat interface with polling-based updates that:
- Displays all worker requests and questions
- Allows humans to respond directly to workers
- Shows current system state (active workers, queue depth, session mappings)
- Provides visibility into all worker-controller interactions
- **Initially handles ALL routing decisions** (no automated LLM responses)
- **Uses polling (not WebSocket)** for simplicity - checks for updates every few seconds

### 5. Basic Task Management
Provide essential task management capabilities:
- Create and queue development tasks
- Assign tasks to workers
- Track task status (queued, in-progress, completed, failed)
- Associate tasks with Git repositories and branches

## What Phase 1 Explicitly EXCLUDES

The following features are **deferred to later phases**:

- ❌ **LLM Controller Layer**: No automated decision-making or LLM-generated responses
- ❌ **Policy Engine**: No intelligent routing based on permission levels or complexity
- ❌ **Automated Handler**: No LLM evaluating whether to handle requests automatically
- ❌ **Advanced Context Management**: No design document storage or retrieval
- ❌ **Multi-Repository Support**: Single repository focus initially
- ❌ **Worker Specialization**: Basic worker types only
- ❌ **Advanced Monitoring**: Basic health checks only
- ❌ **WebSocket Real-Time Updates**: Using simple polling instead for Phase 1 simplicity

## System Architecture (Phase 1)

```
┌─────────────────────────────────────────────────────────────┐
│                  Human Chat Interface                       │
│               (React + Polling + Shad.cn)                   │
│  - Display worker requests (poll every 2-3 seconds)        │
│  - Accept human responses                                   │
│  - Show queue and worker status                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Event Orchestrator (Pass-Through)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Message Router                                      │  │
│  │  - Read worker requests from queue                   │  │
│  │  - Forward ALL requests to chat interface            │  │
│  │  - Forward human responses back to workers           │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Session Manager                                     │  │
│  │  - Map Claude session ID ↔ Task ID                   │  │
│  │  - Track session age and activity                    │  │
│  │  - Decide when to keep/terminate sessions            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  - Task API (create, list, get, update)                    │
│  - Worker API (register, heartbeat, status)                │
│  - Queue API (enqueue, claim, complete)                    │
│  - Chat API (send message, receive response)               │
│  - Session API (create, list, terminate)                   │
└────────────┬────────────────────┬──────────────────────────┘
             │                    │
             ▼                    ▼
┌─────────────────────┐  ┌──────────────────────────────────┐
│   PostgreSQL        │  │        Redis + RQ                │
│   (SQLite dev)      │  │                                  │
│  - Tasks            │  │  Queues:                         │
│  - Workers          │  │  - high_priority                 │
│  - Sessions         │  │  - default                       │
│  - Work Orders      │  │  - low_priority                  │
│  - Chat Messages    │  │  - worker_requests               │
│  - Executions       │  │  - controller_responses          │
└─────────────────────┘  └────────────┬─────────────────────┘
                                      │
                          ┌───────────┴─────────────┐
                          ▼                         ▼
                ┌──────────────────┐      ┌──────────────────┐
                │   Worker 1       │      │   Worker N       │
                │ (Claude Code)    │ ...  │ (Claude Code)    │
                │                  │      │                  │
                │ Session ID: abc  │      │ Session ID: xyz  │
                │ Task ID: task-1  │      │ Task ID: task-n  │
                └──────────────────┘      └──────────────────┘
```

## Phase 1 Data Flow

### Task Execution Flow

```
1. Human Creates Task
   └─> Task stored in PostgreSQL
       └─> Work order enqueued to Redis (priority queue)

2. Worker Claims Work Order
   └─> Atomic pop from Redis queue
       └─> Session created/reused (session_id ↔ task_id mapping)
           └─> Worker begins execution in Claude Code

3. Worker Needs Clarification
   └─> Worker posts question to worker_requests queue
       └─> Orchestrator reads from queue
           └─> Orchestrator routes to chat interface
               └─> Human sees question in real-time chat
                   └─> Human types response
                       └─> Response enqueued to controller_responses
                           └─> Worker receives response
                               └─> Worker continues execution

4. Worker Completes Task
   └─> Results posted to queue
       └─> Orchestrator updates task status
           └─> Session marked for potential reuse or termination
```

### Session Lifecycle

```
1. Session Creation
   - Worker claims task
   - New Claude Code session spawned (or existing session reused)
   - session_id ↔ task_id mapping created
   - Session state: ACTIVE

2. Session Activity
   - Worker sends heartbeat with session_id
   - Orchestrator tracks last_activity timestamp
   - Session context accumulates (conversation history, file reads)

3. Session Keep-Alive Decision
   IF task_completed AND queue_has_similar_tasks AND session_age < 1hr
      THEN reuse_session_for_next_task
   ELSE IF idle_time > 30min
      THEN terminate_session
   ELSE
      THEN keep_session_alive

4. Session Termination
   - Worker finishes all work
   - Orchestrator sends shutdown signal
   - Session state: TERMINATED
   - Mapping removed
```

## Phase 1 Components Breakdown

### Backend API (FastAPI)

**Priority: Critical**

Core endpoints needed:

```
/api/v1/tasks
  POST   /           - Create task
  GET    /           - List tasks (with filters)
  GET    /{id}       - Get task details
  PATCH  /{id}       - Update task status

/api/v1/workers
  POST   /           - Register worker
  GET    /           - List workers
  GET    /{id}       - Get worker details
  POST   /{id}/heartbeat - Send heartbeat
  DELETE /{id}       - Deregister worker

/api/v1/queue
  POST   /enqueue    - Enqueue work order
  POST   /claim      - Claim work order (atomic)
  POST   /complete   - Mark work complete
  POST   /fail       - Mark work failed
  GET    /status     - Get queue stats

/api/v1/sessions
  POST   /           - Create session mapping
  GET    /           - List active sessions
  GET    /{id}       - Get session details
  DELETE /{id}       - Terminate session
  POST   /{id}/heartbeat - Update session activity

/api/v1/chat
  GET    /messages   - Get chat messages
  POST   /messages   - Send message
  WS     /ws         - WebSocket for real-time chat
```

**Database Models:**
- `users` (basic auth)
- `tasks` (work to be done)
- `workers` (registered Claude Code instances)
- `sessions` (session_id ↔ task_id mappings)
- `work_orders` (queue items)
- `chat_messages` (worker ↔ human communication)
- `executions` (execution logs)

### Queue System (Redis + RQ)

**Priority: Critical**

**Queues:**
- `high_priority` - Urgent tasks
- `default` - Normal tasks
- `low_priority` - Background tasks
- `worker_requests` - Worker questions → Orchestrator
- `controller_responses` - Human responses → Workers

**Message Types:**
- `WorkOrderMessage` - Task to execute
- `WorkerRequestMessage` - Worker question/clarification
- `ControllerResponseMessage` - Human response

**Operations:**
- Enqueue with priority
- Atomic claim (prevent double-processing)
- Retry logic with exponential backoff
- Dead letter queue for failures

### Event Orchestrator

**Priority: Critical**

**Components:**

1. **Message Receiver**
   - Poll `worker_requests` queue
   - Parse and validate incoming messages
   - Extract session_id and task_id

2. **Session Manager**
   - Maintain session_id ↔ task_id mapping in PostgreSQL
   - Track session age, last activity
   - Implement keep-alive policies
   - Trigger session termination when needed

3. **Pass-Through Router**
   - Forward ALL worker requests to chat interface
   - Forward ALL human responses back to workers
   - Log all interactions
   - Update session activity timestamps

**Configuration:**
```python
session_config = {
    "max_idle_time": 1800,  # 30 minutes
    "max_session_age": 3600,  # 1 hour
    "reuse_for_similar_tasks": True,
    "context_preservation": True,
}
```

### Worker System (Claude Code)

**Priority: Critical**

**Worker Capabilities:**
- Run Claude Code in headless mode
- Poll queue for work orders
- Execute tasks with full repo context
- Request clarification from orchestrator
- Send heartbeat with session_id
- Report task completion or failure

**Worker Configuration:**
```python
worker_config = {
    "id": "uuid",
    "session_id": "claude-session-abc123",
    "redis_url": "redis://...",
    "api_url": "http://backend:8000",
    "poll_interval": 10,  # seconds
    "heartbeat_interval": 30,  # seconds
}
```

**Worker States:**
- `IDLE` - Available for work
- `BUSY` - Executing task
- `WAITING` - Waiting for human response
- `ERROR` - Error occurred
- `OFFLINE` - Shut down

### Chat Interface (Frontend)

**Priority: Critical**

**Technology:**
- React 19 + TypeScript
- Vite build system
- Shad.cn UI components
- WebSocket for real-time updates
- TanStack Query for data fetching

**Key Features:**
- Real-time message display (worker questions)
- Human response input (text area + send button)
- Worker status dashboard (idle/busy/waiting)
- Queue depth visualization
- Session list (session_id → task mapping)
- Task list with status

**UI Screens:**
1. **Dashboard** - System overview
2. **Chat** - Real-time worker communication
3. **Tasks** - Task list and creation
4. **Workers** - Worker status and management
5. **Sessions** - Active session monitoring

## Phase 1 Success Criteria

Phase 1 is considered complete when:

✅ **Multiple workers can run concurrently**
- 3+ Claude Code workers can run simultaneously
- Workers can claim and execute different tasks in parallel

✅ **Queue system is functional**
- Tasks can be enqueued with priority
- Workers can atomically claim work
- Failed tasks are retried automatically

✅ **Session management works**
- Session IDs are mapped to task IDs correctly
- Sessions persist across multiple related tasks
- Idle sessions are terminated appropriately

✅ **Human chat interface is operational**
- All worker requests appear in real-time
- Humans can respond to worker questions
- Responses are delivered back to workers correctly

✅ **End-to-end workflow completes**
- Create task → Worker claims → Worker asks question → Human responds → Worker completes → Task marked done

✅ **System monitoring is basic but functional**
- Worker heartbeats tracked
- Queue depth visible
- Session activity monitored

## Phase 1 Implementation Order

**Realistic Timeline: 1-2 Days**

Most of Phase 1 is standard web application boilerplate that can be implemented rapidly. The only complex integration is with headless Claude Code instances.

### Day 1: Core System (6-8 hours)

**Backend Foundation (2-3 hours)**
- Database models (tasks, workers, sessions, work_orders, chat_messages)
- Alembic migrations (auto-generated)
- Core API endpoints (tasks, workers, queue, sessions, chat)
- Redis/RQ queue manager service

**Worker & Orchestrator (3-4 hours)**
- Worker base class with polling loop
- Queue claim logic (atomic operations)
- Event orchestrator with session management
- Pass-through router (worker requests → chat, responses → workers)
- Heartbeat mechanism

**Testing & Integration (1-2 hours)**
- Basic unit tests for queue operations
- Integration test for full workflow
- Docker compose setup

### Day 2: Frontend & Polish (4-6 hours)

**Frontend (3-4 hours)**
- React + Vite setup with WebSocket
- Chat interface (message list, input, real-time updates)
- Dashboard (worker status, queue depth, sessions)
- Task list and creation UI

**End-to-End Testing (1-2 hours)**
- Multi-worker test (3+ workers)
- Full workflow validation
- Basic deployment documentation

### What Takes Actual Time?

The only genuinely time-consuming part is **integrating with headless Claude Code**, which is external tooling that needs experimentation. Everything else is standard patterns.

## Phase 1 Deployment

### Development Environment
```bash
# Start dependencies
docker compose up -d postgres redis

# Start backend
cd backend
uv run python -m app.main

# Start orchestrator
cd orchestrator
uv run python -m orchestrator.main

# Start workers (multiple terminals)
cd workers
uv run python -m workers.main --worker-id worker-1
uv run python -m workers.main --worker-id worker-2
uv run python -m workers.main --worker-id worker-3

# Start frontend
cd frontend
npm run dev
```

### Production Environment
```bash
# Single command deployment
docker compose up -d

# Services:
# - postgres
# - redis
# - backend (FastAPI)
# - orchestrator
# - worker-1, worker-2, worker-3 (scalable)
# - frontend (nginx)
```

## Transition to Phase 2

After Phase 1 is complete and stable, Phase 2 will introduce:

**Phase 2: Intelligent LLM Controller**
- LLM-based routing decisions
- Policy engine (autonomous vs. human-required)
- Automated handler (LLM generates responses)
- Context manager (design docs, best practices)
- Hybrid mode (some requests automated, some human)

**Phase 3: Advanced Features**
- Multi-repository support
- Worker specialization (feature, bugfix, test, docs)
- Advanced monitoring and metrics
- Performance optimization
- Security hardening

## Key Design Decisions

### Why Pass-Through Controller in Phase 1?

1. **Simplicity**: Easier to build, test, and debug
2. **Validation**: Proves the queue system and worker coordination work
3. **Human Learning**: Humans learn what questions workers ask
4. **Data Collection**: Gather Q&A pairs to train/test LLM later
5. **Incremental**: Add intelligence gradually without breaking core system

### Why Session Management is Critical?

1. **Context Preservation**: Claude Code maintains conversation history
2. **Repository Understanding**: Accumulated knowledge of codebase
3. **Efficiency**: Reusing sessions faster than spawning new ones
4. **Cost**: Reduces API calls and token usage
5. **Quality**: Better responses with maintained context

### Why Redis + RQ?

1. **Simplicity**: Python-native, easy to understand
2. **Reliability**: Battle-tested in production
3. **Monitoring**: RQ Dashboard provides excellent visibility
4. **Atomicity**: Guarantees work is claimed exactly once
5. **Scalability**: Can handle 1000+ tasks/minute

## Metrics to Track (Phase 1)

**System Health:**
- Worker uptime percentage
- Queue depth (current items in each queue)
- Average claim-to-complete time
- Failed task percentage

**Session Metrics:**
- Active session count
- Average session duration
- Session reuse rate
- Sessions terminated (idle vs. completed)

**Communication Metrics:**
- Worker requests per hour
- Human response time (median, p95)
- Messages per task (average)

**Performance Metrics:**
- Task throughput (tasks/hour)
- Queue latency (enqueue to claim time)
- Worker utilization (busy vs. idle time)

## Risk Mitigation

**Risk: Workers deadlock waiting for responses**
- Mitigation: Timeouts on all wait operations (30min max)
- Fallback: Task moved back to queue if timeout

**Risk: Session mappings get out of sync**
- Mitigation: Heartbeat mechanism validates session_id ↔ task_id
- Fallback: Recreate session if mapping invalid

**Risk: Redis connection loss**
- Mitigation: Connection pooling with retry logic
- Fallback: Workers and orchestrator gracefully handle disconnects

**Risk: Too many idle sessions consuming resources**
- Mitigation: Aggressive session termination policies
- Monitoring: Alert if active sessions > threshold

## Implementation Philosophy

Phase 1 is intentionally **simple and direct**:
- No over-engineering
- Standard patterns (FastAPI, RQ, React)
- Minimal abstractions
- Focus on getting the core loop working

The complexity is not in the implementation—it's in the **design decisions** about session management and worker coordination. Once those are clear (which they are), implementation is straightforward.

## Conclusion

Phase 1 delivers a **functional multi-worker orchestration system** with human oversight in 1-2 days of focused implementation. It establishes the foundation for queue-based coordination, session management, and worker lifecycle while deferring complex LLM decision-making to later phases.

**Success = Multiple workers executing tasks concurrently, coordinated through queues, with humans providing guidance through a real-time chat interface.**

**Timeline Reality Check**: This is ~1500-2000 lines of Python and ~800-1000 lines of TypeScript/React—very achievable in a day or two with AI assistance.
