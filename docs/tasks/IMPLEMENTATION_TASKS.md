# AgentVine Implementation Task List

## Task Organization

Tasks are organized by component and labeled with size:
- **XS** - Extra Small (< 2 hours)
- **S** - Small (2-4 hours)
- **M** - Medium (4-8 hours)

All tasks are designed to be:
- Single-purpose
- Testable
- Iterative
- Independent where possible

---

## Phase 1: Foundation Setup

### 1.1 Project Structure
- [ ] **XS** - Create `backend/app/core/` directory for core config
- [ ] **XS** - Create `backend/app/database/` directory for DB components
- [ ] **XS** - Create `backend/app/services/` directory for business logic
- [ ] **XS** - Create `backend/app/schemas/` directory for Pydantic schemas
- [ ] **XS** - Create `workers/` directory in project root
- [ ] **XS** - Create `controller/` directory in project root
- [ ] **XS** - Create `cli/` directory for CLI tools
- [ ] **XS** - Create `scripts/` directory for dev scripts

### 1.2 Backend Core Configuration
- [ ] **XS** - Create `backend/app/core/config.py` with settings class
- [ ] **XS** - Add environment variable validation using Pydantic
- [ ] **XS** - Create `backend/app/core/security.py` for security utils
- [ ] **XS** - Implement password hashing functions (bcrypt)
- [ ] **XS** - Implement JWT token creation function
- [ ] **XS** - Implement JWT token verification function
- [ ] **XS** - Write unit tests for password hashing
- [ ] **XS** - Write unit tests for JWT functions

### 1.3 Database Setup - Base
- [ ] **XS** - Add SQLAlchemy async dependencies to pyproject.toml
- [ ] **XS** - Add asyncpg dependency to pyproject.toml
- [ ] **XS** - Add Alembic dependency to pyproject.toml
- [ ] **XS** - Create `backend/app/database/session.py` with async engine
- [ ] **XS** - Create `backend/app/database/base.py` with Base class
- [ ] **XS** - Initialize Alembic in backend directory
- [ ] **XS** - Configure Alembic `env.py` for async SQLAlchemy
- [ ] **XS** - Create initial Alembic migration template

---

## Phase 2: Database Models

### 2.1 User Model
- [ ] **XS** - Create `backend/app/models/user.py` with User model
- [ ] **XS** - Add id, username, email fields
- [ ] **XS** - Add hashed_password, full_name fields
- [ ] **XS** - Add role, is_active, is_verified fields
- [ ] **XS** - Add timestamps (created_at, updated_at, last_login_at)
- [ ] **XS** - Add settings JSONB field
- [ ] **XS** - Add indexes for email, username, role
- [ ] **XS** - Create Alembic migration for users table
- [ ] **XS** - Run migration and verify table created

### 2.2 Worker Model
- [ ] **XS** - Create `backend/app/models/worker.py` with Worker model
- [ ] **XS** - Add id, name, worker_type, status fields
- [ ] **XS** - Add version, max_concurrent_tasks, timeout_seconds fields
- [ ] **XS** - Add context_window_size, config JSONB field
- [ ] **XS** - Add capabilities JSONB field
- [ ] **XS** - Add last_heartbeat_at timestamp
- [ ] **XS** - Add created_at, updated_at timestamps
- [ ] **XS** - Add indexes for worker_type, status, heartbeat
- [ ] **XS** - Create Alembic migration for workers table
- [ ] **XS** - Run migration and verify table created

### 2.3 Task Model
- [ ] **S** - Create `backend/app/models/task.py` with Task model
- [ ] **XS** - Add id, title, description fields
- [ ] **XS** - Add task_type, permission_level, priority fields
- [ ] **XS** - Add status field with enum
- [ ] **XS** - Add repository_url, branch_name fields
- [ ] **XS** - Add issue_number, pr_number fields
- [ ] **XS** - Add context, metadata JSONB fields
- [ ] **XS** - Add created_by FK to users
- [ ] **XS** - Add assigned_to FK to workers
- [ ] **XS** - Add parent_task_id self-referential FK
- [ ] **XS** - Add timestamps (created_at, updated_at, started_at, completed_at)
- [ ] **XS** - Add indexes for status, type, priority, created_by, assigned_to
- [ ] **XS** - Create Alembic migration for tasks table
- [ ] **XS** - Run migration and verify table created

### 2.4 Work Order Model
- [ ] **XS** - Create `backend/app/models/work_order.py`
- [ ] **XS** - Add id, task_id FK fields
- [ ] **XS** - Add queue_name, status fields
- [ ] **XS** - Add payload, result JSONB fields
- [ ] **XS** - Add error_message TEXT field
- [ ] **XS** - Add retry_count, max_retries, timeout_seconds fields
- [ ] **XS** - Add timestamps (enqueued_at, claimed_at, completed_at, expires_at)
- [ ] **XS** - Add indexes for task_id, queue_name, status, enqueued_at, expires_at
- [ ] **XS** - Create Alembic migration for work_orders table
- [ ] **XS** - Run migration and verify table created

### 2.5 Worker Assignment Model
- [ ] **XS** - Create `backend/app/models/worker_assignment.py`
- [ ] **XS** - Add id, worker_id FK, work_order_id FK
- [ ] **XS** - Add status field
- [ ] **XS** - Add assigned_at, completed_at timestamps
- [ ] **XS** - Add unique constraint (worker_id, work_order_id)
- [ ] **XS** - Add indexes for worker_id, work_order_id, status
- [ ] **XS** - Create Alembic migration for worker_assignments table
- [ ] **XS** - Run migration and verify table created

### 2.6 Execution Model
- [ ] **XS** - Create `backend/app/models/execution.py`
- [ ] **XS** - Add id, task_id FK, worker_id FK
- [ ] **XS** - Add status, exit_code fields
- [ ] **XS** - Add stdout_log, stderr_log TEXT fields
- [ ] **XS** - Add metrics JSONB field
- [ ] **XS** - Add timestamps (started_at, completed_at)
- [ ] **XS** - Add duration_seconds field
- [ ] **XS** - Add indexes for task_id, worker_id, status, started_at
- [ ] **XS** - Create Alembic migration for executions table
- [ ] **XS** - Run migration and verify table created

### 2.7 Execution Log Model
- [ ] **XS** - Create `backend/app/models/execution_log.py`
- [ ] **XS** - Add id (BIGSERIAL), execution_id FK
- [ ] **XS** - Add level, message fields
- [ ] **XS** - Add metadata JSONB field
- [ ] **XS** - Add logged_at timestamp
- [ ] **XS** - Add indexes for execution_id, level, logged_at
- [ ] **XS** - Create Alembic migration for execution_logs table
- [ ] **XS** - Run migration and verify table created

### 2.8 Chat Message Model
- [ ] **XS** - Create `backend/app/models/chat_message.py`
- [ ] **XS** - Add id, conversation_id fields
- [ ] **XS** - Add sender_type, sender_id fields
- [ ] **XS** - Add message, message_type fields
- [ ] **XS** - Add metadata JSONB field
- [ ] **XS** - Add parent_message_id self-referential FK
- [ ] **XS** - Add created_at, edited_at timestamps
- [ ] **XS** - Add indexes for conversation_id, sender, created_at, parent
- [ ] **XS** - Create Alembic migration for chat_messages table
- [ ] **XS** - Run migration and verify table created

### 2.9 Context Document Model
- [ ] **XS** - Create `backend/app/models/context_document.py`
- [ ] **XS** - Add id, title, document_type fields
- [ ] **XS** - Add content TEXT field
- [ ] **XS** - Add repository_url field
- [ ] **XS** - Add tags ARRAY field
- [ ] **XS** - Add metadata JSONB field
- [ ] **XS** - Add created_by FK, timestamps, version
- [ ] **XS** - Add indexes for document_type, repository_url, tags (GIN), created_by
- [ ] **XS** - Create Alembic migration for context_documents table
- [ ] **XS** - Run migration and verify table created

### 2.10 Supporting Models
- [ ] **XS** - Create `backend/app/models/task_dependency.py`
- [ ] **XS** - Create migration for task_dependencies table
- [ ] **XS** - Create `backend/app/models/worker_capability.py`
- [ ] **XS** - Create migration for worker_capabilities table
- [ ] **XS** - Create `backend/app/models/chat_attachment.py`
- [ ] **XS** - Create migration for chat_attachments table

---

## Phase 3: Pydantic Schemas

### 3.1 User Schemas
- [ ] **XS** - Create `backend/app/schemas/user.py`
- [ ] **XS** - Define UserBase schema
- [ ] **XS** - Define UserCreate schema with password
- [ ] **XS** - Define UserUpdate schema
- [ ] **XS** - Define UserResponse schema
- [ ] **XS** - Define UserInDB schema
- [ ] **XS** - Write validation tests for user schemas

### 3.2 Task Schemas
- [ ] **XS** - Create `backend/app/schemas/task.py`
- [ ] **XS** - Define TaskBase schema
- [ ] **XS** - Define TaskCreate schema
- [ ] **XS** - Define TaskUpdate schema
- [ ] **XS** - Define TaskResponse schema
- [ ] **XS** - Define TaskList schema with pagination
- [ ] **XS** - Write validation tests for task schemas

### 3.3 Worker Schemas
- [ ] **XS** - Create `backend/app/schemas/worker.py`
- [ ] **XS** - Define WorkerBase, WorkerCreate, WorkerUpdate schemas
- [ ] **XS** - Define WorkerResponse schema
- [ ] **XS** - Write validation tests

### 3.4 Work Order Schemas
- [ ] **XS** - Create `backend/app/schemas/work_order.py`
- [ ] **XS** - Define WorkOrderMessage schema
- [ ] **XS** - Define WorkOrderResponse schema
- [ ] **XS** - Write validation tests

### 3.5 Chat Schemas
- [ ] **XS** - Create `backend/app/schemas/chat.py`
- [ ] **XS** - Define ChatMessageCreate, ChatMessageResponse schemas
- [ ] **XS** - Define WorkerRequestMessage schema
- [ ] **XS** - Define ControllerResponseMessage schema
- [ ] **XS** - Write validation tests

### 3.6 Common Schemas
- [ ] **XS** - Create `backend/app/schemas/common.py`
- [ ] **XS** - Define PaginatedResponse generic schema
- [ ] **XS** - Define ErrorResponse schema
- [ ] **XS** - Define HealthResponse, AboutResponse schemas

---

## Phase 4: Authentication & Authorization

### 4.1 Auth Service
- [ ] **XS** - Create `backend/app/services/auth.py`
- [ ] **XS** - Implement `create_user()` function
- [ ] **XS** - Implement `authenticate_user()` function
- [ ] **XS** - Implement `get_current_user()` dependency
- [ ] **XS** - Implement `get_current_active_user()` dependency
- [ ] **XS** - Write unit tests for create_user
- [ ] **XS** - Write unit tests for authenticate_user
- [ ] **XS** - Write unit tests for dependencies

### 4.2 Auth API Endpoints
- [ ] **XS** - Create `backend/app/routers/auth.py`
- [ ] **XS** - Implement POST /api/v1/auth/register endpoint
- [ ] **XS** - Implement POST /api/v1/auth/login endpoint
- [ ] **XS** - Implement POST /api/v1/auth/refresh endpoint
- [ ] **XS** - Implement POST /api/v1/auth/logout endpoint
- [ ] **XS** - Write integration tests for register endpoint
- [ ] **XS** - Write integration tests for login endpoint
- [ ] **XS** - Write integration tests for refresh endpoint
- [ ] **XS** - Add auth router to main.py

---

## Phase 5: Core API Endpoints

### 5.1 User Endpoints
- [ ] **XS** - Create `backend/app/routers/users.py`
- [ ] **XS** - Implement GET /api/v1/users/me endpoint
- [ ] **XS** - Implement PATCH /api/v1/users/me endpoint
- [ ] **XS** - Write integration tests for user endpoints
- [ ] **XS** - Add users router to main.py

### 5.2 Task Endpoints
- [ ] **XS** - Create `backend/app/routers/tasks.py`
- [ ] **XS** - Implement POST /api/v1/tasks endpoint
- [ ] **XS** - Implement GET /api/v1/tasks endpoint with filtering
- [ ] **XS** - Implement GET /api/v1/tasks/{task_id} endpoint
- [ ] **XS** - Implement PATCH /api/v1/tasks/{task_id} endpoint
- [ ] **XS** - Implement DELETE /api/v1/tasks/{task_id} endpoint
- [ ] **XS** - Write integration tests for POST tasks
- [ ] **XS** - Write integration tests for GET tasks (list)
- [ ] **XS** - Write integration tests for GET task (detail)
- [ ] **XS** - Write integration tests for PATCH/DELETE
- [ ] **XS** - Add tasks router to main.py

### 5.3 Worker Endpoints
- [ ] **XS** - Create `backend/app/routers/workers.py`
- [ ] **XS** - Implement POST /api/v1/workers endpoint
- [ ] **XS** - Implement GET /api/v1/workers endpoint
- [ ] **XS** - Implement GET /api/v1/workers/{worker_id} endpoint
- [ ] **XS** - Implement POST /api/v1/workers/{worker_id}/heartbeat endpoint
- [ ] **XS** - Implement DELETE /api/v1/workers/{worker_id} endpoint
- [ ] **XS** - Write integration tests for worker endpoints
- [ ] **XS** - Add workers router to main.py

---

## Phase 6: Queue System

### 6.1 Redis Setup
- [ ] **XS** - Add redis dependency to pyproject.toml
- [ ] **XS** - Add rq dependency to pyproject.toml
- [ ] **XS** - Create `backend/app/core/redis.py` for Redis connection
- [ ] **XS** - Implement Redis connection pooling
- [ ] **XS** - Create Redis health check function
- [ ] **XS** - Write unit tests for Redis connection

### 6.2 Queue Manager
- [ ] **XS** - Create `backend/app/services/queue_manager.py`
- [ ] **XS** - Initialize RQ queue instances (high_priority, default, low_priority)
- [ ] **XS** - Implement `enqueue_task()` method
- [ ] **XS** - Implement `enqueue_worker_request()` method
- [ ] **XS** - Implement `enqueue_controller_response()` method
- [ ] **XS** - Implement `get_queue_stats()` method
- [ ] **XS** - Write unit tests for QueueManager
- [ ] **XS** - Write integration tests with Redis

### 6.3 Queue API Endpoints
- [ ] **XS** - Create `backend/app/routers/queue.py`
- [ ] **XS** - Implement POST /api/v1/queue/enqueue endpoint
- [ ] **XS** - Implement GET /api/v1/queue/status endpoint
- [ ] **XS** - Implement POST /api/v1/queue/claim endpoint
- [ ] **XS** - Implement POST /api/v1/queue/complete endpoint
- [ ] **XS** - Implement POST /api/v1/queue/fail endpoint
- [ ] **XS** - Write integration tests for queue endpoints
- [ ] **XS** - Add queue router to main.py

---

## Phase 7: Worker System

### 7.1 Worker Base Classes
- [ ] **XS** - Create `workers/base/` directory
- [ ] **XS** - Create `workers/base/config.py` with WorkerConfig dataclass
- [ ] **XS** - Create `workers/base/worker.py` with Worker base class
- [ ] **XS** - Implement worker initialization logic
- [ ] **XS** - Implement worker registration with backend
- [ ] **XS** - Implement main work loop (poll, claim, execute)
- [ ] **XS** - Implement heartbeat sending
- [ ] **XS** - Implement graceful shutdown

### 7.2 Queue Client (Worker Side)
- [ ] **XS** - Create `workers/base/queue_client.py`
- [ ] **XS** - Implement `claim_work()` method
- [ ] **XS** - Implement `enqueue_worker_request()` method
- [ ] **XS** - Implement `check_for_response()` method
- [ ] **XS** - Implement `wait_for_response()` method with timeout
- [ ] **XS** - Write unit tests for QueueClient

### 7.3 API Client (Worker Side)
- [ ] **XS** - Create `workers/base/api_client.py`
- [ ] **XS** - Implement HTTP client with authentication
- [ ] **XS** - Implement retry logic for network errors
- [ ] **XS** - Implement request/response logging
- [ ] **XS** - Write unit tests for APIClient

### 7.4 Task Executor
- [ ] **XS** - Create `workers/base/task_executor.py`
- [ ] **XS** - Implement workspace directory creation
- [ ] **XS** - Implement repository cloning logic
- [ ] **XS** - Implement task execution dispatch (by type)
- [ ] **XS** - Implement cleanup logic
- [ ] **XS** - Write unit tests for TaskExecutor

### 7.5 Feature Worker
- [ ] **XS** - Create `workers/specialized/` directory
- [ ] **XS** - Create `workers/specialized/feature_worker.py`
- [ ] **XS** - Implement feature task execution logic
- [ ] **XS** - Implement code generation logic
- [ ] **XS** - Implement test writing logic
- [ ] **XS** - Implement commit creation logic
- [ ] **XS** - Write unit tests for FeatureWorker

### 7.6 Bugfix Worker
- [ ] **XS** - Create `workers/specialized/bugfix_worker.py`
- [ ] **XS** - Implement bugfix task execution logic
- [ ] **XS** - Implement error analysis logic
- [ ] **XS** - Implement fix verification logic
- [ ] **XS** - Write unit tests for BugfixWorker

### 7.7 Test Worker
- [ ] **XS** - Create `workers/specialized/test_worker.py`
- [ ] **XS** - Implement test writing logic
- [ ] **XS** - Implement test execution logic
- [ ] **XS** - Implement coverage analysis logic
- [ ] **XS** - Write unit tests for TestWorker

### 7.8 Documentation Worker
- [ ] **XS** - Create `workers/specialized/docs_worker.py`
- [ ] **XS** - Implement documentation generation logic
- [ ] **XS** - Implement README creation logic
- [ ] **XS** - Write unit tests for DocsWorker

### 7.9 Worker CLI
- [ ] **XS** - Create `workers/cli.py` with Click commands
- [ ] **XS** - Implement `worker start` command
- [ ] **XS** - Implement `worker status` command
- [ ] **XS** - Implement `worker stop` command
- [ ] **XS** - Add worker configuration via CLI args

### 7.10 Worker Deployment
- [ ] **XS** - Create `Dockerfile.worker`
- [ ] **XS** - Create docker-compose.worker.yml
- [ ] **XS** - Create worker startup script
- [ ] **XS** - Document worker deployment process

---

## Phase 8: Controller System

### 8.1 Controller Base
- [ ] **XS** - Create `controller/` directory structure
- [ ] **XS** - Create `controller/config.py` with ControllerConfig
- [ ] **XS** - Create `controller/main.py` with ChatController class
- [ ] **XS** - Implement controller initialization
- [ ] **XS** - Implement main controller loop (poll messages)
- [ ] **XS** - Implement graceful shutdown

### 8.2 Message Receiver
- [ ] **XS** - Create `controller/message_receiver.py`
- [ ] **XS** - Implement `poll()` method for worker requests
- [ ] **XS** - Implement `validate_message()` method
- [ ] **XS** - Write unit tests for MessageReceiver

### 8.3 Policy Engine
- [ ] **XS** - Create `controller/policies/` directory
- [ ] **XS** - Create `controller/policies/policy_engine.py`
- [ ] **XS** - Define Policy dataclass
- [ ] **XS** - Implement PolicyEngine class
- [ ] **XS** - Add default routing policies
- [ ] **XS** - Implement policy evaluation logic
- [ ] **XS** - Write unit tests for PolicyEngine

### 8.4 Routing Engine
- [ ] **XS** - Create `controller/routing/` directory
- [ ] **XS** - Create `controller/routing/routing_engine.py`
- [ ] **XS** - Implement RoutingEngine class
- [ ] **XS** - Implement `route()` method with metadata extraction
- [ ] **XS** - Write unit tests for RoutingEngine

### 8.5 Automated Handler
- [ ] **XS** - Create `controller/handlers/` directory
- [ ] **XS** - Create `controller/handlers/automated_handler.py`
- [ ] **XS** - Add Anthropic SDK dependency
- [ ] **XS** - Implement AutomatedHandler class
- [ ] **XS** - Implement `generate_response()` method
- [ ] **XS** - Implement prompt building logic
- [ ] **XS** - Write unit tests for AutomatedHandler

### 8.6 Human Handler
- [ ] **XS** - Create `controller/handlers/human_handler.py`
- [ ] **XS** - Implement HumanHandler class
- [ ] **XS** - Implement `request_human_response()` method
- [ ] **XS** - Implement response waiting logic with timeout
- [ ] **XS** - Implement `receive_human_response()` method
- [ ] **XS** - Write unit tests for HumanHandler

### 8.7 Context Manager
- [ ] **XS** - Create `controller/context/` directory
- [ ] **XS** - Create `controller/context/context_manager.py`
- [ ] **XS** - Implement ContextManager class
- [ ] **XS** - Implement `get_design_documents()` method
- [ ] **XS** - Implement `get_task_context()` method
- [ ] **XS** - Implement `store_context_document()` method
- [ ] **XS** - Write unit tests for ContextManager

### 8.8 Response Dispatcher
- [ ] **XS** - Create `controller/response_dispatcher.py`
- [ ] **XS** - Implement ResponseDispatcher class
- [ ] **XS** - Implement `dispatch()` method
- [ ] **XS** - Implement response logging
- [ ] **XS** - Write unit tests for ResponseDispatcher

### 8.9 Controller Integration
- [ ] **S** - Integrate all controller components in main.py
- [ ] **XS** - Add error handling to main loop
- [ ] **XS** - Add metrics collection
- [ ] **XS** - Write integration tests for full controller flow

### 8.10 Controller Deployment
- [ ] **XS** - Create `Dockerfile.controller`
- [ ] **XS** - Create docker-compose.controller.yml
- [ ] **XS** - Create controller startup script
- [ ] **XS** - Document controller deployment

---

## Phase 9: Chat System

### 9.1 Chat Service (Backend)
- [ ] **XS** - Create `backend/app/services/chat_service.py`
- [ ] **XS** - Implement `create_message()` method
- [ ] **XS** - Implement `get_messages()` method with pagination
- [ ] **XS** - Implement `get_conversation()` method
- [ ] **XS** - Implement `get_response()` method
- [ ] **XS** - Write unit tests for ChatService

### 9.2 Chat API Endpoints
- [ ] **XS** - Create `backend/app/routers/chat.py`
- [ ] **XS** - Implement GET /api/v1/chat/conversations endpoint
- [ ] **XS** - Implement GET /api/v1/chat/conversations/{id}/messages endpoint
- [ ] **XS** - Implement POST /api/v1/chat/conversations/{id}/messages endpoint
- [ ] **XS** - Write integration tests for chat endpoints
- [ ] **XS** - Add chat router to main.py

### 9.3 WebSocket Support
- [ ] **XS** - Add python-socketio dependency
- [ ] **XS** - Create `backend/app/websocket/` directory
- [ ] **XS** - Create `backend/app/websocket/manager.py`
- [ ] **XS** - Implement WebSocket connection management
- [ ] **XS** - Implement message broadcasting
- [ ] **XS** - Implement WS /api/v1/chat/ws/{conversation_id} endpoint
- [ ] **XS** - Write integration tests for WebSocket
- [ ] **XS** - Add WebSocket support to main.py

### 9.4 Context Document Endpoints
- [ ] **XS** - Create `backend/app/routers/context.py`
- [ ] **XS** - Implement POST /api/v1/context/documents endpoint
- [ ] **XS** - Implement GET /api/v1/context/documents endpoint
- [ ] **XS** - Implement GET /api/v1/context/documents/{id} endpoint
- [ ] **XS** - Write integration tests for context endpoints
- [ ] **XS** - Add context router to main.py

### 9.5 Execution Endpoints
- [ ] **XS** - Create `backend/app/routers/executions.py`
- [ ] **XS** - Implement GET /api/v1/executions endpoint
- [ ] **XS** - Implement GET /api/v1/executions/{id} endpoint
- [ ] **XS** - Implement GET /api/v1/executions/{id}/logs endpoint
- [ ] **XS** - Write integration tests for execution endpoints
- [ ] **XS** - Add executions router to main.py

---

## Phase 10: Frontend Foundation

### 10.1 Project Setup
- [ ] **XS** - Install TailwindCSS 4
- [ ] **XS** - Install TanStack Query
- [ ] **XS** - Install Zustand
- [ ] **XS** - Install React Router 7
- [ ] **XS** - Install Socket.IO client
- [ ] **XS** - Install Zod
- [ ] **XS** - Install React Markdown
- [ ] **XS** - Configure TypeScript strict mode

### 10.2 Shad.cn Setup
- [ ] **XS** - Initialize Shad.cn in project
- [ ] **XS** - Install Button component
- [ ] **XS** - Install Card component
- [ ] **XS** - Install Dialog component
- [ ] **XS** - Install Table component
- [ ] **XS** - Install Form component
- [ ] **XS** - Install Input, Select components
- [ ] **XS** - Install Badge, Toast components
- [ ] **XS** - Install Tabs, ScrollArea components

### 10.3 Directory Structure
- [ ] **XS** - Create src/components/ui/ directory
- [ ] **XS** - Create src/components/chat/ directory
- [ ] **XS** - Create src/components/tasks/ directory
- [ ] **XS** - Create src/components/workers/ directory
- [ ] **XS** - Create src/services/ directory
- [ ] **XS** - Create src/stores/ directory
- [ ] **XS** - Create src/hooks/ directory
- [ ] **XS** - Create src/types/ directory
- [ ] **XS** - Create src/utils/ directory

### 10.4 TypeScript Types
- [ ] **XS** - Create src/types/api.ts with API response types
- [ ] **XS** - Create src/types/models.ts with domain models
- [ ] **XS** - Create src/types/events.ts with event types
- [ ] **XS** - Export all types from index.ts

---

## Phase 11: Frontend Services

### 11.1 API Client
- [ ] **XS** - Create src/services/api.ts
- [ ] **XS** - Set up axios instance with base URL
- [ ] **XS** - Add request interceptor for auth token
- [ ] **XS** - Add response interceptor for error handling
- [ ] **XS** - Add 401 handling (logout and redirect)
- [ ] **XS** - Export api client

### 11.2 Auth Service
- [ ] **XS** - Create src/services/auth.ts
- [ ] **XS** - Implement login() function
- [ ] **XS** - Implement register() function
- [ ] **XS** - Implement logout() function
- [ ] **XS** - Implement refreshToken() function
- [ ] **XS** - Write unit tests for auth service

### 11.3 WebSocket Service
- [ ] **XS** - Create src/services/websocket.ts
- [ ] **XS** - Implement WebSocketService class
- [ ] **XS** - Implement connect() method
- [ ] **XS** - Implement disconnect() method
- [ ] **XS** - Implement sendMessage() method
- [ ] **XS** - Implement event listener management (on/off)
- [ ] **XS** - Export wsService singleton

### 11.4 Storage Service
- [ ] **XS** - Create src/services/storage.ts
- [ ] **XS** - Implement localStorage wrapper
- [ ] **XS** - Implement token storage helpers
- [ ] **XS** - Implement user preferences storage

---

## Phase 12: Frontend State Management

### 12.1 Auth Store
- [ ] **XS** - Create src/stores/authStore.ts
- [ ] **XS** - Define AuthState interface
- [ ] **XS** - Implement login action
- [ ] **XS** - Implement logout action
- [ ] **XS** - Implement isAuthenticated selector
- [ ] **XS** - Add persist middleware
- [ ] **XS** - Export useAuthStore hook

### 12.2 UI Store
- [ ] **XS** - Create src/stores/uiStore.ts
- [ ] **XS** - Define UIState interface
- [ ] **XS** - Implement sidebar toggle action
- [ ] **XS** - Implement theme toggle action
- [ ] **XS** - Export useUIStore hook

### 12.3 Realtime Store
- [ ] **XS** - Create src/stores/realtimeStore.ts
- [ ] **XS** - Define RealtimeState interface
- [ ] **XS** - Implement WebSocket connection state
- [ ] **XS** - Implement message handling
- [ ] **XS** - Export useRealtimeStore hook

---

## Phase 13: Frontend Custom Hooks

### 13.1 Auth Hooks
- [ ] **XS** - Create src/hooks/useAuth.ts
- [ ] **XS** - Wrap authStore in useAuth hook
- [ ] **XS** - Add loading and error states

### 13.2 WebSocket Hooks
- [ ] **XS** - Create src/hooks/useWebSocket.ts
- [ ] **XS** - Implement connection lifecycle
- [ ] **XS** - Implement message state management
- [ ] **XS** - Add auto-reconnect logic
- [ ] **XS** - Return messages, sendMessage, isConnected

### 13.3 Data Fetching Hooks
- [ ] **XS** - Create src/hooks/useTasks.ts with TanStack Query
- [ ] **XS** - Create src/hooks/useWorkers.ts with TanStack Query
- [ ] **XS** - Create src/hooks/useQueue.ts with TanStack Query
- [ ] **XS** - Create src/hooks/useChat.ts with TanStack Query

---

## Phase 14: Frontend Components - Chat

### 14.1 Chat Layout
- [ ] **XS** - Create src/components/chat/ChatWindow.tsx
- [ ] **XS** - Create basic layout (header, messages, input)
- [ ] **XS** - Add responsive design

### 14.2 Message Components
- [ ] **XS** - Create src/components/chat/MessageList.tsx
- [ ] **XS** - Create src/components/chat/MessageBubble.tsx
- [ ] **XS** - Implement message sender type differentiation
- [ ] **XS** - Add markdown rendering support
- [ ] **XS** - Add timestamp formatting
- [ ] **XS** - Add auto-scroll to bottom

### 14.3 Chat Input
- [ ] **XS** - Create src/components/chat/ChatInput.tsx
- [ ] **XS** - Add textarea with auto-resize
- [ ] **XS** - Add send button
- [ ] **XS** - Add keyboard shortcuts (Enter to send)
- [ ] **XS** - Add loading state while sending

### 14.4 Context Sidebar
- [ ] **XS** - Create src/components/chat/ContextSidebar.tsx
- [ ] **XS** - Display task context
- [ ] **XS** - Display design documents
- [ ] **XS** - Add collapsible sections

---

## Phase 15: Frontend Components - Tasks

### 15.1 Task List
- [ ] **XS** - Create src/components/tasks/TaskTable.tsx
- [ ] **XS** - Display tasks in table format
- [ ] **XS** - Add status badges
- [ ] **XS** - Add priority indicators
- [ ] **XS** - Add click to view details

### 15.2 Task Filters
- [ ] **XS** - Create src/components/tasks/TaskFilters.tsx
- [ ] **XS** - Add status filter dropdown
- [ ] **XS** - Add type filter dropdown
- [ ] **XS** - Add priority filter dropdown
- [ ] **XS** - Add search input

### 15.3 Task Creation
- [ ] **XS** - Create src/components/tasks/CreateTaskDialog.tsx
- [ ] **XS** - Add form fields (title, description, type, priority)
- [ ] **XS** - Add repository URL, branch inputs
- [ ] **XS** - Add form validation with Zod
- [ ] **XS** - Implement submit handler
- [ ] **XS** - Add loading and error states

### 15.4 Task Detail
- [ ] **XS** - Create src/components/tasks/TaskDetail.tsx
- [ ] **XS** - Display full task information
- [ ] **XS** - Display execution history
- [ ] **XS** - Add edit/delete actions

---

## Phase 16: Frontend Components - Workers

### 16.1 Worker Grid
- [ ] **XS** - Create src/components/workers/WorkerGrid.tsx
- [ ] **XS** - Display workers in grid layout
- [ ] **XS** - Add status indicators (idle, busy, offline, error)
- [ ] **XS** - Add worker type badges
- [ ] **XS** - Add last heartbeat timestamp

### 16.2 Worker Stats
- [ ] **XS** - Create src/components/workers/WorkerStats.tsx
- [ ] **XS** - Display total workers count
- [ ] **XS** - Display workers by status
- [ ] **XS** - Display workers by type

### 16.3 Worker Detail
- [ ] **XS** - Create src/components/workers/WorkerDetail.tsx
- [ ] **XS** - Display worker configuration
- [ ] **XS** - Display capabilities
- [ ] **XS** - Display current task (if any)
- [ ] **XS** - Display metrics (CPU, memory)

---

## Phase 17: Frontend Pages

### 17.1 Dashboard Page
- [ ] **XS** - Create src/pages/DashboardPage.tsx
- [ ] **XS** - Add metrics grid component
- [ ] **XS** - Add queue status chart
- [ ] **XS** - Add recent activity timeline
- [ ] **XS** - Add quick action buttons

### 17.2 Chat Page
- [ ] **XS** - Create src/pages/ChatPage.tsx
- [ ] **XS** - Integrate ChatWindow component
- [ ] **XS** - Add conversation list sidebar
- [ ] **XS** - Add conversation switching
- [ ] **XS** - Integrate WebSocket connection

### 17.3 Tasks Page
- [ ] **XS** - Create src/pages/TasksPage.tsx
- [ ] **XS** - Integrate TaskTable component
- [ ] **XS** - Integrate TaskFilters component
- [ ] **XS** - Add create task button
- [ ] **XS** - Add pagination

### 17.4 Workers Page
- [ ] **XS** - Create src/pages/WorkersPage.tsx
- [ ] **XS** - Integrate WorkerStats component
- [ ] **XS** - Integrate WorkerGrid component
- [ ] **XS** - Add worker filtering

### 17.5 Context Page
- [ ] **XS** - Create src/pages/ContextPage.tsx
- [ ] **XS** - Display context documents list
- [ ] **XS** - Add document viewer
- [ ] **XS** - Add create document dialog
- [ ] **XS** - Add search and filtering

### 17.6 Settings Page
- [ ] **XS** - Create src/pages/SettingsPage.tsx
- [ ] **XS** - Add user profile section
- [ ] **XS** - Add theme selector
- [ ] **XS** - Add notification preferences

---

## Phase 18: Frontend Routing & App

### 18.1 Router Setup
- [ ] **XS** - Update src/App.tsx with React Router
- [ ] **XS** - Add route for / (Dashboard)
- [ ] **XS** - Add route for /chat
- [ ] **XS** - Add route for /chat/:conversationId
- [ ] **XS** - Add route for /tasks
- [ ] **XS** - Add route for /workers
- [ ] **XS** - Add route for /context
- [ ] **XS** - Add route for /settings
- [ ] **XS** - Add route for /login
- [ ] **XS** - Add route for /register

### 18.2 Protected Routes
- [ ] **XS** - Create ProtectedRoute component
- [ ] **XS** - Add authentication check
- [ ] **XS** - Add redirect to login if not authenticated

### 18.3 Layout Components
- [ ] **XS** - Create src/components/shared/Layout.tsx
- [ ] **XS** - Create src/components/shared/Navbar.tsx
- [ ] **XS** - Create src/components/shared/Sidebar.tsx
- [ ] **XS** - Integrate Navigation component

### 18.4 App Setup
- [ ] **XS** - Set up QueryClientProvider in main.tsx
- [ ] **XS** - Add React Query DevTools
- [ ] **XS** - Add error boundary
- [ ] **XS** - Add global loading indicator

---

## Phase 19: Testing & Quality

### 19.1 Backend Tests
- [ ] **S** - Achieve 90%+ code coverage for backend
- [ ] **XS** - Add tests for all API endpoints
- [ ] **XS** - Add tests for all services
- [ ] **XS** - Add tests for queue operations
- [ ] **XS** - Add tests for auth flows

### 19.2 Worker Tests
- [ ] **XS** - Add unit tests for Worker class
- [ ] **XS** - Add unit tests for TaskExecutor
- [ ] **XS** - Add integration tests for queue claiming
- [ ] **XS** - Add integration tests for API communication

### 19.3 Controller Tests
- [ ] **XS** - Add unit tests for PolicyEngine
- [ ] **XS** - Add unit tests for RoutingEngine
- [ ] **XS** - Add unit tests for handlers
- [ ] **XS** - Add integration tests for full flow

### 19.4 Frontend Tests
- [ ] **XS** - Add tests for components (Vitest + Testing Library)
- [ ] **XS** - Add tests for hooks
- [ ] **XS** - Add tests for stores
- [ ] **XS** - Add E2E tests with Playwright

### 19.5 Code Quality
- [ ] **XS** - Run ruff linting on all Python code
- [ ] **XS** - Run mypy type checking (100% coverage)
- [ ] **XS** - Run black formatting on all Python code
- [ ] **XS** - Run bandit security scan
- [ ] **XS** - Run ESLint on all TypeScript code
- [ ] **XS** - Fix all linting/type errors

---

## Phase 20: Documentation

### 20.1 API Documentation
- [ ] **XS** - Verify OpenAPI schema is complete
- [ ] **XS** - Add examples to all endpoints
- [ ] **XS** - Add authentication documentation
- [ ] **XS** - Test Swagger UI

### 20.2 User Guides
- [ ] **XS** - Create docs/guides/INSTALLATION.md
- [ ] **XS** - Create docs/guides/QUICKSTART.md
- [ ] **XS** - Create docs/guides/CREATING_TASKS.md
- [ ] **XS** - Create docs/guides/WORKER_SETUP.md
- [ ] **XS** - Create docs/guides/CONTROLLER_SETUP.md

### 20.3 Developer Guides
- [ ] **XS** - Create docs/guides/DEVELOPMENT.md
- [ ] **XS** - Create docs/guides/TESTING.md
- [ ] **XS** - Create docs/guides/DEPLOYMENT.md
- [ ] **XS** - Create docs/guides/CONTRIBUTING.md

### 20.4 README Updates
- [ ] **XS** - Update main README.md with overview
- [ ] **XS** - Add architecture diagram
- [ ] **XS** - Add getting started section
- [ ] **XS** - Add links to documentation

---

## Phase 21: Deployment & DevOps

### 21.1 Docker Compose
- [ ] **XS** - Create docker-compose.yml for full stack
- [ ] **XS** - Add PostgreSQL service
- [ ] **XS** - Add Redis service
- [ ] **XS** - Add backend service
- [ ] **XS** - Add frontend service (nginx)
- [ ] **XS** - Add worker services (multiple instances)
- [ ] **XS** - Add controller service
- [ ] **XS** - Add RQ Dashboard service
- [ ] **XS** - Add health checks to all services
- [ ] **XS** - Add volume mounts for persistence

### 21.2 Environment Configuration
- [ ] **XS** - Create .env.example for all services
- [ ] **XS** - Document all environment variables
- [ ] **XS** - Create .env.development
- [ ] **XS** - Create .env.production template

### 21.3 CI/CD
- [ ] **XS** - Create .github/workflows/backend-tests.yml
- [ ] **XS** - Create .github/workflows/frontend-tests.yml
- [ ] **XS** - Create .github/workflows/worker-tests.yml
- [ ] **XS** - Create .github/workflows/lint.yml
- [ ] **XS** - Create .github/workflows/security.yml
- [ ] **XS** - Create .github/workflows/build.yml

### 21.4 Deployment Scripts
- [ ] **XS** - Create scripts/deploy-backend.sh
- [ ] **XS** - Create scripts/deploy-frontend.sh
- [ ] **XS** - Create scripts/deploy-workers.sh
- [ ] **XS** - Create scripts/deploy-controller.sh
- [ ] **XS** - Create scripts/backup-db.sh
- [ ] **XS** - Create scripts/restore-db.sh

---

## Phase 22: Monitoring & Observability

### 22.1 Logging
- [ ] **XS** - Configure structured logging for backend
- [ ] **XS** - Configure structured logging for workers
- [ ] **XS** - Configure structured logging for controller
- [ ] **XS** - Add correlation IDs to all logs
- [ ] **XS** - Set up log aggregation (optional)

### 22.2 Metrics
- [ ] **XS** - Add Prometheus metrics to backend
- [ ] **XS** - Add custom metrics (request count, duration, etc.)
- [ ] **XS** - Add queue depth metrics
- [ ] **XS** - Add worker metrics
- [ ] **XS** - Create Grafana dashboard (optional)

### 22.3 Health Checks
- [ ] **XS** - Verify /health endpoint returns all statuses
- [ ] **XS** - Add database health check
- [ ] **XS** - Add Redis health check
- [ ] **XS** - Add worker health monitoring
- [ ] **XS** - Add controller health monitoring

### 22.4 Alerting
- [ ] **XS** - Set up alerts for high queue depth
- [ ] **XS** - Set up alerts for worker failures
- [ ] **XS** - Set up alerts for API errors
- [ ] **XS** - Set up alerts for database issues

---

## Phase 23: Performance & Optimization

### 23.1 Backend Optimization
- [ ] **XS** - Add database connection pooling
- [ ] **XS** - Add Redis connection pooling
- [ ] **XS** - Optimize database queries (add indexes)
- [ ] **XS** - Add caching for frequently accessed data
- [ ] **XS** - Run performance tests (aim for <50ms p95)

### 23.2 Frontend Optimization
- [ ] **XS** - Implement code splitting with React.lazy()
- [ ] **XS** - Add memoization to expensive components
- [ ] **XS** - Optimize images (lazy loading)
- [ ] **XS** - Add service worker for offline support
- [ ] **XS** - Run Lighthouse audit and fix issues

### 23.3 Queue Optimization
- [ ] **XS** - Implement batch enqueueing
- [ ] **XS** - Optimize queue polling interval
- [ ] **XS** - Add queue priority handling
- [ ] **XS** - Test queue throughput (aim for >1000 tasks/min)

---

## Phase 24: Security Hardening

### 24.1 Backend Security
- [ ] **XS** - Enable HTTPS in production
- [ ] **XS** - Add rate limiting to all endpoints
- [ ] **XS** - Add CORS configuration
- [ ] **XS** - Add security headers middleware
- [ ] **XS** - Run bandit security scan and fix issues
- [ ] **XS** - Add SQL injection protection verification
- [ ] **XS** - Add XSS protection verification

### 24.2 Auth Security
- [ ] **XS** - Implement password strength requirements
- [ ] **XS** - Add password reset functionality
- [ ] **XS** - Add email verification
- [ ] **XS** - Add account lockout after failed attempts
- [ ] **XS** - Add JWT token rotation
- [ ] **XS** - Add refresh token revocation

### 24.3 Worker Security
- [ ] **XS** - Implement worker authentication with API keys
- [ ] **XS** - Add worker authorization checks
- [ ] **XS** - Add sandboxing for worker execution
- [ ] **XS** - Add resource limits (CPU, memory, disk)
- [ ] **XS** - Add network restrictions

### 24.4 Data Security
- [ ] **XS** - Encrypt sensitive data at rest
- [ ] **XS** - Use SSL/TLS for all connections
- [ ] **XS** - Add audit logging for sensitive operations
- [ ] **XS** - Implement data retention policies

---

## Phase 25: Integration & E2E Testing

### 25.1 Full System Integration
- [ ] **M** - Start all services with docker-compose
- [ ] **XS** - Verify backend API is accessible
- [ ] **XS** - Verify frontend loads correctly
- [ ] **XS** - Verify worker can register
- [ ] **XS** - Verify controller starts successfully
- [ ] **XS** - Verify Redis and PostgreSQL are healthy

### 25.2 End-to-End Workflows
- [ ] **S** - Test complete task flow (create → enqueue → execute → complete)
- [ ] **S** - Test worker request → controller → human response flow
- [ ] **S** - Test worker request → controller → automated response flow
- [ ] **XS** - Test chat message flow via WebSocket
- [ ] **XS** - Test authentication flow (register → login → access protected)
- [ ] **XS** - Test worker failure and retry flow

### 25.3 Load Testing
- [ ] **S** - Load test API endpoints (>1000 req/s)
- [ ] **S** - Load test queue system (>1000 tasks/min)
- [ ] **S** - Load test WebSocket connections (>100 concurrent)
- [ ] **XS** - Test with multiple workers (5+)
- [ ] **XS** - Test with high queue depth (1000+ tasks)

---

## Phase 26: Polish & Launch Prep

### 26.1 UI/UX Polish
- [ ] **XS** - Add loading skeletons to all pages
- [ ] **XS** - Add error states to all components
- [ ] **XS** - Add empty states to all lists
- [ ] **XS** - Add toast notifications for actions
- [ ] **XS** - Add confirmation dialogs for destructive actions
- [ ] **XS** - Test responsiveness on mobile
- [ ] **XS** - Test dark mode (if implemented)

### 26.2 Final Testing
- [ ] **S** - Run full test suite (backend, frontend, integration)
- [ ] **XS** - Fix all failing tests
- [ ] **XS** - Verify code coverage >90%
- [ ] **XS** - Run all linters and fix issues
- [ ] **XS** - Run security scans and fix vulnerabilities

### 26.3 Documentation Review
- [ ] **XS** - Review all design documents
- [ ] **XS** - Review all API documentation
- [ ] **XS** - Review all user guides
- [ ] **XS** - Review README files
- [ ] **XS** - Add troubleshooting guide

### 26.4 Deployment Preparation
- [ ] **XS** - Test production build locally
- [ ] **XS** - Verify environment variable configuration
- [ ] **XS** - Test database migration process
- [ ] **XS** - Test backup and restore process
- [ ] **XS** - Create deployment checklist

---

## Summary

**Total Estimated Tasks**: ~450+

**Size Distribution**:
- XS (< 2 hours): ~95%
- S (2-4 hours): ~4%
- M (4-8 hours): ~1%

**Key Principles**:
1. Each task is independently testable
2. Tasks can be completed in order within each phase
3. Most tasks are < 2 hours (XS size)
4. Clear acceptance criteria for each task
5. Dependencies are minimized
6. Tasks build incrementally

**Recommended Approach**:
1. Complete phases 1-3 first (foundation and models)
2. Then tackle phases 4-6 (auth, API, queue)
3. Build workers and controller (phases 7-8)
4. Implement chat system (phase 9)
5. Build frontend (phases 10-18)
6. Test, document, and deploy (phases 19-26)

**Next Steps**:
1. Review and refine task list
2. Assign priorities to tasks
3. Create project board (GitHub Projects or similar)
4. Begin with Phase 1 tasks
5. Track progress and update as needed
