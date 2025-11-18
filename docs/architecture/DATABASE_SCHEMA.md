# Database Schema Design

## Overview

AgentVine uses SQLAlchemy ORM with PostgreSQL (production) and SQLite (development). The schema supports the core workflow of task assignment, worker execution, and chat coordination.

## Entity Relationship Diagram

```
users ──┬─── chat_messages
        ├─── tasks (created_by)
        └─── context_documents (created_by)

workers ──┬─── worker_assignments
          ├─── executions
          └─── worker_capabilities

tasks ──┬─── work_orders
        ├─── executions
        └─── task_dependencies

work_orders ─── worker_assignments

chat_messages ─── chat_attachments

executions ─── execution_logs
```

## Tables

### 1. users

User accounts for the system (humans and service accounts).

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'developer', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    settings JSONB DEFAULT '{}'::jsonb,

    -- Indexes
    INDEX idx_users_email (email),
    INDEX idx_users_username (username),
    INDEX idx_users_role (role)
);
```

**Fields:**
- `id` - Primary key (UUID)
- `username` - Unique username
- `email` - Unique email address
- `hashed_password` - Bcrypt hashed password
- `full_name` - User's full name
- `role` - User role (admin, developer, viewer)
- `is_active` - Account active status
- `is_verified` - Email verification status
- `settings` - User preferences (JSON)

### 2. workers

Registry of Claude Code worker instances.

```sql
CREATE TABLE workers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    worker_type VARCHAR(20) NOT NULL CHECK (
        worker_type IN ('feature', 'bugfix', 'test', 'docs', 'refactor', 'review')
    ),
    status VARCHAR(20) NOT NULL CHECK (
        status IN ('idle', 'busy', 'offline', 'error')
    ),
    version VARCHAR(50),
    max_concurrent_tasks INTEGER DEFAULT 1,
    timeout_seconds INTEGER DEFAULT 3600,
    context_window_size INTEGER DEFAULT 200000,
    config JSONB DEFAULT '{}'::jsonb,
    capabilities JSONB DEFAULT '[]'::jsonb,
    last_heartbeat_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    INDEX idx_workers_type (worker_type),
    INDEX idx_workers_status (status),
    INDEX idx_workers_heartbeat (last_heartbeat_at)
);
```

**Fields:**
- `id` - Primary key (UUID)
- `name` - Worker friendly name
- `worker_type` - Type of worker
- `status` - Current worker status
- `version` - Worker software version
- `max_concurrent_tasks` - Concurrency limit
- `timeout_seconds` - Task timeout
- `context_window_size` - Token limit
- `config` - Worker configuration (JSON)
- `capabilities` - Worker capabilities (JSON array)
- `last_heartbeat_at` - Last health check

### 3. tasks

Task definitions and metadata.

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(20) NOT NULL CHECK (
        task_type IN ('feature', 'bugfix', 'test', 'docs', 'refactor', 'review')
    ),
    permission_level VARCHAR(20) NOT NULL CHECK (
        permission_level IN ('autonomous', 'supervised', 'human_required')
    ),
    priority VARCHAR(10) NOT NULL DEFAULT 'normal' CHECK (
        priority IN ('low', 'normal', 'high', 'critical')
    ),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'queued', 'in_progress', 'blocked', 'completed', 'failed', 'cancelled')
    ),
    repository_url VARCHAR(500),
    branch_name VARCHAR(255),
    issue_number INTEGER,
    pr_number INTEGER,
    context JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_to UUID REFERENCES workers(id) ON DELETE SET NULL,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Indexes
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_type (task_type),
    INDEX idx_tasks_priority (priority),
    INDEX idx_tasks_created_by (created_by),
    INDEX idx_tasks_assigned_to (assigned_to),
    INDEX idx_tasks_parent (parent_task_id)
);
```

**Fields:**
- `id` - Primary key (UUID)
- `title` - Task title
- `description` - Detailed description
- `task_type` - Type of task
- `permission_level` - Automation level
- `priority` - Task priority
- `status` - Current status
- `repository_url` - Git repository URL
- `branch_name` - Target branch
- `context` - Additional context (JSON)
- `metadata` - Task metadata (JSON)

### 4. work_orders

Queued work items for workers to claim.

```sql
CREATE TABLE work_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    queue_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'claimed', 'completed', 'failed', 'expired')
    ),
    payload JSONB NOT NULL,
    result JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 3600,
    enqueued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    claimed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,

    -- Indexes
    INDEX idx_work_orders_task (task_id),
    INDEX idx_work_orders_queue (queue_name),
    INDEX idx_work_orders_status (status),
    INDEX idx_work_orders_enqueued (enqueued_at),
    INDEX idx_work_orders_expires (expires_at)
);
```

**Fields:**
- `id` - Primary key (UUID)
- `task_id` - Reference to task
- `queue_name` - Redis queue name
- `status` - Order status
- `payload` - Work order data (JSON)
- `result` - Execution result (JSON)
- `retry_count` - Current retry attempt
- `expires_at` - Expiration timestamp

### 5. worker_assignments

Active worker-task assignments.

```sql
CREATE TABLE worker_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (
        status IN ('active', 'completed', 'failed', 'timeout')
    ),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    UNIQUE (worker_id, work_order_id),

    -- Indexes
    INDEX idx_assignments_worker (worker_id),
    INDEX idx_assignments_order (work_order_id),
    INDEX idx_assignments_status (status)
);
```

**Fields:**
- `id` - Primary key (UUID)
- `worker_id` - Assigned worker
- `work_order_id` - Assigned work order
- `status` - Assignment status
- `assigned_at` - Assignment timestamp
- `completed_at` - Completion timestamp

### 6. executions

Execution history and logs.

```sql
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'running' CHECK (
        status IN ('running', 'completed', 'failed', 'timeout', 'cancelled')
    ),
    exit_code INTEGER,
    stdout_log TEXT,
    stderr_log TEXT,
    metrics JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,

    -- Indexes
    INDEX idx_executions_task (task_id),
    INDEX idx_executions_worker (worker_id),
    INDEX idx_executions_status (status),
    INDEX idx_executions_started (started_at)
);
```

**Fields:**
- `id` - Primary key (UUID)
- `task_id` - Associated task
- `worker_id` - Executing worker
- `status` - Execution status
- `stdout_log` - Standard output
- `stderr_log` - Standard error
- `metrics` - Performance metrics (JSON)
- `duration_seconds` - Execution duration

### 7. execution_logs

Detailed execution logs with timestamps.

```sql
CREATE TABLE execution_logs (
    id BIGSERIAL PRIMARY KEY,
    execution_id UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    level VARCHAR(10) NOT NULL CHECK (
        level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    ),
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    INDEX idx_execution_logs_execution (execution_id),
    INDEX idx_execution_logs_level (level),
    INDEX idx_execution_logs_logged_at (logged_at)
);
```

**Fields:**
- `id` - Primary key (auto-increment)
- `execution_id` - Associated execution
- `level` - Log level
- `message` - Log message
- `metadata` - Additional data (JSON)
- `logged_at` - Log timestamp

### 8. chat_messages

Chat conversation history.

```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    sender_type VARCHAR(10) NOT NULL CHECK (
        sender_type IN ('user', 'worker', 'system', 'controller')
    ),
    sender_id UUID,
    message TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL DEFAULT 'text' CHECK (
        message_type IN ('text', 'question', 'response', 'status', 'error')
    ),
    metadata JSONB DEFAULT '{}'::jsonb,
    parent_message_id UUID REFERENCES chat_messages(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    edited_at TIMESTAMP WITH TIME ZONE,

    -- Indexes
    INDEX idx_chat_messages_conversation (conversation_id),
    INDEX idx_chat_messages_sender (sender_type, sender_id),
    INDEX idx_chat_messages_created (created_at),
    INDEX idx_chat_messages_parent (parent_message_id)
);
```

**Fields:**
- `id` - Primary key (UUID)
- `conversation_id` - Conversation thread ID
- `sender_type` - Type of sender
- `sender_id` - ID of sender (user/worker)
- `message` - Message content
- `message_type` - Type of message
- `parent_message_id` - Reply threading

### 9. chat_attachments

File attachments in chat messages.

```sql
CREATE TABLE chat_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size_bytes BIGINT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    INDEX idx_chat_attachments_message (message_id)
);
```

### 10. context_documents

Shared context and knowledge base.

```sql
CREATE TABLE context_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL CHECK (
        document_type IN ('design', 'plan', 'specification', 'guide', 'reference')
    ),
    content TEXT NOT NULL,
    repository_url VARCHAR(500),
    tags VARCHAR(50)[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,

    -- Indexes
    INDEX idx_context_docs_type (document_type),
    INDEX idx_context_docs_repo (repository_url),
    INDEX idx_context_docs_tags (tags) USING GIN,
    INDEX idx_context_docs_created_by (created_by)
);
```

**Fields:**
- `id` - Primary key (UUID)
- `title` - Document title
- `document_type` - Type of document
- `content` - Document content (markdown)
- `repository_url` - Associated repository
- `tags` - Searchable tags (array)
- `version` - Version number

### 11. task_dependencies

Task dependency relationships.

```sql
CREATE TABLE task_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    depends_on_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    dependency_type VARCHAR(20) NOT NULL DEFAULT 'blocks' CHECK (
        dependency_type IN ('blocks', 'related', 'duplicate')
    ),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE (task_id, depends_on_task_id),
    CHECK (task_id != depends_on_task_id),

    -- Indexes
    INDEX idx_task_deps_task (task_id),
    INDEX idx_task_deps_depends_on (depends_on_task_id)
);
```

### 12. worker_capabilities

Worker skills and specializations.

```sql
CREATE TABLE worker_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
    capability_name VARCHAR(100) NOT NULL,
    capability_level VARCHAR(20) DEFAULT 'intermediate' CHECK (
        capability_level IN ('beginner', 'intermediate', 'advanced', 'expert')
    ),
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    UNIQUE (worker_id, capability_name),

    -- Indexes
    INDEX idx_worker_caps_worker (worker_id),
    INDEX idx_worker_caps_name (capability_name)
);
```

**Examples:**
- Python (expert)
- TypeScript (advanced)
- React (advanced)
- FastAPI (expert)
- Testing (intermediate)

## Migrations

### Using Alembic

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Migration Strategy

1. **Development**: Auto-generate migrations
2. **Staging**: Review and test migrations
3. **Production**: Apply with backup

## Indexes Strategy

### Performance Indexes
- All foreign keys have indexes
- Status fields have indexes for filtering
- Timestamp fields for sorting/filtering
- JSONB fields use GIN indexes where appropriate

### Composite Indexes (Future)
```sql
-- Frequently queried combinations
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority);
CREATE INDEX idx_workers_type_status ON workers(worker_type, status);
CREATE INDEX idx_executions_task_status ON executions(task_id, status);
```

## Data Retention

### Logs
- `execution_logs`: 30 days retention
- Archive to cold storage after 30 days

### Completed Tasks
- Keep indefinitely for audit
- Archive old executions (> 90 days)

### Chat Messages
- Keep indefinitely
- Optional archival after 1 year

## Backup Strategy

### PostgreSQL
- Daily full backups
- WAL archiving for point-in-time recovery
- Backup retention: 30 days
- Test restore monthly

### SQLite (Development)
- Committed to git (empty schema)
- Local backups optional

## Performance Considerations

### Connection Pooling
```python
# SQLAlchemy async engine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)
```

### Query Optimization
- Use select_in_loading for relationships
- Avoid N+1 queries
- Use EXPLAIN ANALYZE for slow queries
- Monitor query performance

### JSONB Performance
- Index frequently queried paths
- Use containment operators (@>)
- Consider separate tables for complex queries

## Security

### Data Protection
- Passwords hashed with bcrypt
- Sensitive data encrypted at rest
- SSL/TLS for connections
- Row-level security (future)

### Audit Trail
- `created_at` and `updated_at` on all tables
- Soft deletes for critical data
- Change tracking (future)

## SQLAlchemy Models

See `/backend/app/models/` for implementation.

Models should include:
- Type hints
- Relationships
- Validators
- Serialization methods
- Indexes defined in model
