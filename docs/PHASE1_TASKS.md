# Phase 1 Implementation Tasks

**Timeline: 1-2 Days**
**Goal: Multi-worker queue system with human chat oversight**

---

## Day 1: Backend & Core System (6-8 hours)

### 1. Database Models & Migrations (30-45 min)

**Files to create:**
- `backend/app/models/task.py`
- `backend/app/models/worker.py`
- `backend/app/models/session.py`
- `backend/app/models/work_order.py`
- `backend/app/models/chat_message.py`
- `backend/app/models/execution.py`

**Models to implement:**

```python
# Task
- id (UUID, PK)
- title (String)
- description (Text)
- task_type (Enum: feature, bugfix, test, docs)
- status (Enum: queued, in_progress, completed, failed)
- priority (Enum: high, normal, low)
- repository_url (String)
- branch_name (String)
- created_at, updated_at, completed_at (DateTime)

# Worker
- id (UUID, PK)
- name (String)
- status (Enum: idle, busy, waiting, error, offline)
- last_heartbeat_at (DateTime)
- created_at, updated_at (DateTime)

# Session
- id (UUID, PK)
- session_id (String, unique) # Claude Code session ID
- worker_id (UUID, FK → workers)
- task_id (UUID, FK → tasks, nullable)
- status (Enum: active, idle, terminated)
- last_activity_at (DateTime)
- created_at, terminated_at (DateTime)

# WorkOrder
- id (UUID, PK)
- task_id (UUID, FK → tasks)
- worker_id (UUID, FK → workers, nullable)
- status (Enum: queued, claimed, completed, failed)
- priority (Enum: high, normal, low)
- enqueued_at, claimed_at, completed_at (DateTime)
- retry_count (Integer)

# ChatMessage
- id (UUID, PK)
- conversation_id (UUID)
- sender_type (Enum: worker, human, system)
- sender_id (UUID)
- message (Text)
- message_type (Enum: request, response, status)
- parent_message_id (UUID, nullable)
- created_at (DateTime)

# Execution
- id (UUID, PK)
- task_id (UUID, FK → tasks)
- worker_id (UUID, FK → workers)
- session_id (UUID, FK → sessions)
- status (Enum: running, completed, failed)
- started_at, completed_at (DateTime)
- output (Text)
```

**Migrations:**
```bash
cd backend
alembic revision --autogenerate -m "Initial models"
alembic upgrade head
```

---

### 2. Queue Manager Service (45-60 min)

**File to create:**
- `backend/app/services/queue_manager.py`

**Implement:**

```python
class QueueManager:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)
        self.high_priority = Queue("high_priority", connection=self.redis)
        self.default = Queue("default", connection=self.redis)
        self.low_priority = Queue("low_priority", connection=self.redis)
        self.worker_requests = Queue("worker_requests", connection=self.redis)
        self.controller_responses = Queue("controller_responses", connection=self.redis)

    def enqueue_task(self, work_order: WorkOrder, priority: str) -> str
    def claim_work(self, worker_id: str) -> Optional[WorkOrder]
    def enqueue_worker_request(self, request: WorkerRequest) -> str
    def enqueue_controller_response(self, response: ControllerResponse) -> str
    def get_queue_stats(self) -> dict
```

**Dependencies:**
```bash
uv add redis rq
```

---

### 3. Core API Endpoints (90-120 min)

**Files to create:**
- `backend/app/routers/tasks.py`
- `backend/app/routers/workers.py`
- `backend/app/routers/queue.py`
- `backend/app/routers/sessions.py`
- `backend/app/routers/chat.py`

**Endpoints:**

```python
# Tasks
POST   /api/v1/tasks          # Create task
GET    /api/v1/tasks          # List tasks (with filters)
GET    /api/v1/tasks/{id}     # Get task
PATCH  /api/v1/tasks/{id}     # Update task

# Workers
POST   /api/v1/workers        # Register worker
GET    /api/v1/workers        # List workers
GET    /api/v1/workers/{id}   # Get worker
POST   /api/v1/workers/{id}/heartbeat  # Heartbeat
DELETE /api/v1/workers/{id}   # Deregister

# Queue
POST   /api/v1/queue/enqueue  # Enqueue work order
POST   /api/v1/queue/claim    # Claim work (atomic)
POST   /api/v1/queue/complete # Mark complete
POST   /api/v1/queue/fail     # Mark failed
GET    /api/v1/queue/status   # Queue stats

# Sessions
POST   /api/v1/sessions       # Create session mapping
GET    /api/v1/sessions       # List sessions
GET    /api/v1/sessions/{id}  # Get session
DELETE /api/v1/sessions/{id}  # Terminate session
POST   /api/v1/sessions/{id}/heartbeat  # Update activity

# Chat
GET    /api/v1/chat/messages  # Get messages
POST   /api/v1/chat/messages  # Send message
WS     /api/v1/chat/ws        # WebSocket connection
```

---

### 4. WebSocket Support (30-45 min)

**File to create:**
- `backend/app/websocket/manager.py`

**Implement:**

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket)
    async def disconnect(self, websocket: WebSocket)
    async def broadcast(self, message: dict)
    async def send_personal(self, message: dict, websocket: WebSocket)
```

**Add to router:**
```python
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming messages
            await manager.broadcast(data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
```

**Dependencies:**
```bash
uv add websockets
```

---

### 5. Worker Base System (90-120 min)

**Files to create:**
- `workers/base/worker.py`
- `workers/base/config.py`
- `workers/base/api_client.py`
- `workers/base/queue_client.py`

**Implement:**

```python
class Worker:
    def __init__(self, config: WorkerConfig):
        self.id = str(uuid.uuid4())
        self.session_id = None  # Claude Code session ID
        self.status = WorkerStatus.IDLE
        self.api_client = APIClient(config.api_url)
        self.queue_client = QueueClient(config.redis_url)

    def run(self):
        """Main work loop"""
        while True:
            self.send_heartbeat()
            work_order = self.claim_work()
            if work_order:
                self.execute_work_order(work_order)
            else:
                time.sleep(self.poll_interval)

    def claim_work(self) -> Optional[WorkOrder]
    def execute_work_order(self, work_order: WorkOrder)
    def request_clarification(self, question: str) -> str
    def send_heartbeat(self)
```

**Key methods:**
- `claim_work()` - Poll queue and claim work
- `execute_work_order()` - Execute task (stub for now, Claude Code integration later)
- `request_clarification()` - Post to worker_requests queue, wait for response
- `send_heartbeat()` - Update worker status and session activity

---

### 6. Event Orchestrator (90-120 min)

**Files to create:**
- `orchestrator/main.py`
- `orchestrator/session_manager.py`
- `orchestrator/message_router.py`

**Implement:**

```python
class Orchestrator:
    def __init__(self):
        self.queue_client = QueueClient(redis_url)
        self.session_manager = SessionManager()
        self.message_router = MessageRouter()

    async def run(self):
        """Main orchestrator loop"""
        while True:
            # Poll for worker requests
            request = self.queue_client.worker_requests.dequeue()
            if request:
                await self.process_request(request)
            await asyncio.sleep(5)

    async def process_request(self, request: WorkerRequest):
        # Update session activity
        await self.session_manager.update_activity(request.session_id)

        # Forward to chat interface via WebSocket
        await self.message_router.forward_to_chat(request)

        # Wait for human response (handled by chat API endpoint)
```

**SessionManager:**
```python
class SessionManager:
    async def create_session(self, session_id: str, worker_id: str, task_id: str)
    async def update_activity(self, session_id: str)
    async def should_terminate(self, session_id: str) -> bool
    async def terminate_session(self, session_id: str)
    async def get_session_mapping(self) -> dict[str, str]  # session_id → task_id
```

**Keep-alive policy:**
```python
def should_terminate(session: Session) -> bool:
    idle_time = now() - session.last_activity_at
    session_age = now() - session.created_at

    # Terminate if idle > 30 min
    if idle_time > timedelta(minutes=30):
        return True

    # Terminate if total age > 1 hour
    if session_age > timedelta(hours=1):
        return True

    # Keep alive if active
    return False
```

---

### 7. Docker Compose Setup (30 min)

**File to update:**
- `docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: agentvine
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: agentvine
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://agentvine:dev_password@postgres:5432/agentvine
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app

  orchestrator:
    build: ./orchestrator
    environment:
      - REDIS_URL=redis://redis:6379/0
      - API_URL=http://backend:8000
    depends_on:
      - backend
      - redis

volumes:
  postgres_data:
  redis_data:
```

---

## Day 2: Frontend & Polish (4-6 hours)

### 8. React Frontend Setup (30-45 min)

**Initialize frontend:**
```bash
cd frontend
npm install @tanstack/react-query zustand socket.io-client
```

**Create structure:**
```
frontend/src/
  components/
    chat/
    dashboard/
    tasks/
  services/
    api.ts
    websocket.ts
  stores/
    authStore.ts
    chatStore.ts
  pages/
    DashboardPage.tsx
    ChatPage.tsx
    TasksPage.tsx
```

---

### 9. Chat Interface (90-120 min)

**Files to create:**
- `frontend/src/components/chat/ChatWindow.tsx`
- `frontend/src/components/chat/MessageList.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/components/chat/ChatInput.tsx`

**Features:**
- Real-time message display via WebSocket
- Message differentiation (worker vs. human)
- Input field with send button
- Auto-scroll to latest message
- Timestamp formatting

**Key implementation:**
```tsx
function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([])
  const ws = useWebSocket()

  useEffect(() => {
    ws.on('worker_request', (msg) => {
      setMessages(prev => [...prev, msg])
    })
  }, [])

  const handleSend = (text: string) => {
    ws.send({ type: 'human_response', message: text })
  }

  return (
    <div>
      <MessageList messages={messages} />
      <ChatInput onSend={handleSend} />
    </div>
  )
}
```

---

### 10. Dashboard Views (60-90 min)

**Files to create:**
- `frontend/src/components/dashboard/WorkerStatus.tsx`
- `frontend/src/components/dashboard/QueueStats.tsx`
- `frontend/src/components/dashboard/SessionList.tsx`

**Metrics to display:**
- Active workers (idle/busy/waiting)
- Queue depth (high/default/low priority)
- Active sessions (session_id → task_id)
- Recent activity timeline

**Auto-refresh:**
```tsx
const { data: workers } = useQuery({
  queryKey: ['workers'],
  queryFn: () => api.get('/api/v1/workers'),
  refetchInterval: 5000  // Refresh every 5 seconds
})
```

---

### 11. Task List & Creation UI (45-60 min)

**Files to create:**
- `frontend/src/components/tasks/TaskTable.tsx`
- `frontend/src/components/tasks/CreateTaskDialog.tsx`

**Features:**
- Display tasks with status badges
- Filter by status/type
- Create task form (title, description, repo URL, branch)
- Enqueue task button

---

### 12. Integration Testing (60-90 min)

**Test scenarios:**

1. **Full workflow test:**
   ```python
   # Create task
   task = create_task(title="Test task", repo="...", branch="main")

   # Start worker
   worker = Worker(config)
   worker.start()

   # Worker should claim task
   assert worker.current_task == task.id

   # Worker requests clarification
   response = worker.request_clarification("Which library?")

   # Human responds via chat
   chat.send_response("Use library X")

   # Worker receives response
   assert response == "Use library X"

   # Worker completes task
   worker.complete_task()

   # Task marked as completed
   assert task.status == "completed"
   ```

2. **Multi-worker test:**
   ```python
   # Create 3 tasks
   tasks = [create_task(...) for _ in range(3)]

   # Start 3 workers
   workers = [Worker(config) for _ in range(3)]
   for w in workers:
       w.start()

   # Each worker should claim different task
   claimed_tasks = [w.current_task for w in workers]
   assert len(set(claimed_tasks)) == 3
   ```

3. **Session lifecycle test:**
   ```python
   # Create session
   session = create_session(session_id="abc", task_id=task1.id)

   # Update activity
   update_session_activity("abc")

   # Check should_terminate (should be False)
   assert not should_terminate("abc")

   # Simulate 35 minutes idle
   session.last_activity_at = now() - timedelta(minutes=35)

   # Should terminate now
   assert should_terminate("abc")
   ```

---

### 13. Deployment Documentation (30 min)

**Create:**
- `docs/QUICKSTART.md` - Getting started guide
- `docs/DEVELOPMENT.md` - Development setup
- Update `README.md` - Overview and links

**Quickstart content:**
```markdown
# QuickStart

## Prerequisites
- Docker & Docker Compose
- Python 3.13+ (for local development)
- Node.js 18+ (for frontend development)

## Start the system

```bash
# Start all services
docker compose up -d

# Check services are running
docker compose ps

# View logs
docker compose logs -f
```

## Access the application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- RQ Dashboard: http://localhost:9181

## Create your first task

1. Open http://localhost:5173
2. Click "Create Task"
3. Fill in: title, description, repo URL, branch
4. Click "Enqueue"
5. Watch a worker claim and execute the task
6. Respond to worker questions in the chat
```

---

## Success Checklist

Phase 1 is complete when you can:

- ✅ Start 3 workers via `docker compose up --scale worker=3`
- ✅ Create a task via the frontend UI
- ✅ See the task claimed by a worker in the dashboard
- ✅ See worker questions appear in real-time chat
- ✅ Respond to worker via chat input
- ✅ See worker receive response and continue
- ✅ See task marked as completed in task list
- ✅ See session mapping in dashboard (session_id → task_id)
- ✅ See idle sessions terminated after 30 minutes

---

## What's NOT in Phase 1

These are explicitly deferred:

- ❌ Actual Claude Code integration (stub implementation for now)
- ❌ LLM controller (all routing goes to human)
- ❌ Policy engine
- ❌ Advanced context management
- ❌ Multi-repository support
- ❌ Worker specialization
- ❌ Production deployment configs

---

## Estimated Lines of Code

**Backend:**
- Models: ~300 lines
- API endpoints: ~500 lines
- Queue manager: ~200 lines
- WebSocket: ~100 lines
- **Total: ~1100 lines**

**Worker:**
- Base worker: ~300 lines
- Queue client: ~150 lines
- **Total: ~450 lines**

**Orchestrator:**
- Main loop: ~200 lines
- Session manager: ~200 lines
- Message router: ~150 lines
- **Total: ~550 lines**

**Frontend:**
- Components: ~600 lines
- Services: ~200 lines
- **Total: ~800 lines**

**Grand Total: ~2900 lines** (very achievable in 1-2 days)
