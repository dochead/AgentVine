# API Design

## Overview

AgentVine REST API built with FastAPI, providing endpoints for task management, worker coordination, chat operations, and system monitoring.

## Base Configuration

### Base URL
- Development: `http://localhost:8000`
- Production: `https://api.agentvine.example.com`

### API Versioning
- Current version: `v1`
- URL pattern: `/api/v1/{resource}`

### Authentication
- **Type**: JWT Bearer tokens
- **Header**: `Authorization: Bearer <token>`
- **Token lifetime**: 24 hours
- **Refresh token lifetime**: 30 days

## API Endpoints

### Health & Status

#### GET /health
Health check endpoint for monitoring.

**Response 200:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T10:30:00Z",
  "version": "0.0.1",
  "database": "connected",
  "redis": "connected"
}
```

#### GET /about
Application information.

**Response 200:**
```json
{
  "name": "AgentVine",
  "version": "0.0.1",
  "description": "Hybrid agent/human event-driven orchestration system"
}
```

---

### Authentication

#### POST /api/v1/auth/register
Register a new user account.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "developer",
  "is_active": true,
  "created_at": "2025-11-18T10:30:00Z"
}
```

**Errors:**
- 400: Validation error
- 409: Username or email already exists

#### POST /api/v1/auth/login
Authenticate user and receive tokens.

**Request:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Errors:**
- 401: Invalid credentials
- 403: Account disabled

#### POST /api/v1/auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### POST /api/v1/auth/logout
Invalidate current tokens.

**Headers:** `Authorization: Bearer <token>`

**Response 204:** No content

---

### Users

#### GET /api/v1/users/me
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "developer",
  "is_active": true,
  "created_at": "2025-11-18T10:30:00Z",
  "settings": {}
}
```

#### PATCH /api/v1/users/me
Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "full_name": "John A. Doe",
  "settings": {
    "theme": "dark",
    "notifications": true
  }
}
```

**Response 200:** Updated user object

---

### Tasks

#### POST /api/v1/tasks
Create a new task.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication to the API",
  "task_type": "feature",
  "permission_level": "supervised",
  "priority": "high",
  "repository_url": "https://github.com/org/repo",
  "branch_name": "main",
  "issue_number": 123,
  "context": {
    "files": ["backend/app/auth.py"],
    "requirements": ["JWT", "OAuth2"]
  },
  "metadata": {
    "estimated_hours": 8,
    "tags": ["auth", "security"]
  }
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "title": "Implement user authentication",
  "status": "pending",
  "task_type": "feature",
  "permission_level": "supervised",
  "priority": "high",
  "created_by": "uuid",
  "created_at": "2025-11-18T10:30:00Z",
  "updated_at": "2025-11-18T10:30:00Z"
}
```

**Errors:**
- 400: Validation error
- 401: Unauthorized
- 403: Insufficient permissions

#### GET /api/v1/tasks
List tasks with filtering and pagination.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `status` - Filter by status (pending, queued, in_progress, etc.)
- `task_type` - Filter by type (feature, bugfix, etc.)
- `priority` - Filter by priority (low, normal, high, critical)
- `assigned_to` - Filter by worker ID
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)
- `sort` - Sort field (default: created_at)
- `order` - Sort order (asc, desc)

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Task title",
      "status": "in_progress",
      "task_type": "feature",
      "priority": "high",
      "created_at": "2025-11-18T10:30:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

#### GET /api/v1/tasks/{task_id}
Get task details.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "id": "uuid",
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication to the API",
  "task_type": "feature",
  "permission_level": "supervised",
  "priority": "high",
  "status": "in_progress",
  "repository_url": "https://github.com/org/repo",
  "branch_name": "main",
  "context": {},
  "metadata": {},
  "created_by": "uuid",
  "assigned_to": "uuid",
  "created_at": "2025-11-18T10:30:00Z",
  "updated_at": "2025-11-18T10:30:00Z",
  "started_at": "2025-11-18T10:35:00Z"
}
```

**Errors:**
- 404: Task not found

#### PATCH /api/v1/tasks/{task_id}
Update task.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "status": "completed",
  "metadata": {
    "completion_notes": "Successfully implemented"
  }
}
```

**Response 200:** Updated task object

**Errors:**
- 400: Invalid status transition
- 404: Task not found
- 403: Insufficient permissions

#### DELETE /api/v1/tasks/{task_id}
Cancel/delete task.

**Headers:** `Authorization: Bearer <token>`

**Response 204:** No content

**Errors:**
- 404: Task not found
- 403: Cannot delete in-progress task

---

### Workers

#### POST /api/v1/workers
Register a new worker.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Feature Worker 1",
  "worker_type": "feature",
  "version": "1.0.0",
  "max_concurrent_tasks": 1,
  "config": {
    "timeout": 3600,
    "context_window": 200000
  },
  "capabilities": [
    {"name": "python", "level": "expert"},
    {"name": "typescript", "level": "advanced"}
  ]
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "name": "Feature Worker 1",
  "worker_type": "feature",
  "status": "idle",
  "version": "1.0.0",
  "created_at": "2025-11-18T10:30:00Z"
}
```

#### GET /api/v1/workers
List all workers.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `worker_type` - Filter by type
- `status` - Filter by status (idle, busy, offline, error)
- `page`, `page_size`

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Feature Worker 1",
      "worker_type": "feature",
      "status": "busy",
      "last_heartbeat_at": "2025-11-18T10:35:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

#### GET /api/v1/workers/{worker_id}
Get worker details.

**Response 200:**
```json
{
  "id": "uuid",
  "name": "Feature Worker 1",
  "worker_type": "feature",
  "status": "busy",
  "version": "1.0.0",
  "max_concurrent_tasks": 1,
  "current_tasks": 1,
  "capabilities": [
    {"name": "python", "level": "expert"}
  ],
  "last_heartbeat_at": "2025-11-18T10:35:00Z",
  "created_at": "2025-11-18T10:30:00Z"
}
```

#### POST /api/v1/workers/{worker_id}/heartbeat
Worker health check.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "status": "busy",
  "current_tasks": 1,
  "metrics": {
    "cpu_percent": 45.2,
    "memory_mb": 512
  }
}
```

**Response 200:**
```json
{
  "acknowledged": true,
  "server_time": "2025-11-18T10:35:00Z"
}
```

#### DELETE /api/v1/workers/{worker_id}
Deregister worker.

**Headers:** `Authorization: Bearer <token>`

**Response 204:** No content

---

### Work Queue

#### POST /api/v1/queue/enqueue
Add task to work queue.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "task_id": "uuid",
  "queue_name": "high_priority",
  "timeout_seconds": 3600,
  "max_retries": 3
}
```

**Response 201:**
```json
{
  "work_order_id": "uuid",
  "task_id": "uuid",
  "queue_name": "high_priority",
  "status": "pending",
  "enqueued_at": "2025-11-18T10:35:00Z",
  "expires_at": "2025-11-18T11:35:00Z"
}
```

#### GET /api/v1/queue/status
Get queue statistics.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "queues": {
    "high_priority": {
      "pending": 5,
      "claimed": 2,
      "completed": 128,
      "failed": 3
    },
    "default": {
      "pending": 12,
      "claimed": 8,
      "completed": 456,
      "failed": 10
    }
  },
  "workers": {
    "total": 10,
    "idle": 3,
    "busy": 7,
    "offline": 0
  }
}
```

#### POST /api/v1/queue/claim
Worker claims a work order.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "worker_id": "uuid",
  "queue_names": ["high_priority", "default"]
}
```

**Response 200:**
```json
{
  "work_order_id": "uuid",
  "task_id": "uuid",
  "payload": {},
  "claimed_at": "2025-11-18T10:35:00Z"
}
```

**Response 204:** No work available

#### POST /api/v1/queue/complete
Worker completes a work order.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "work_order_id": "uuid",
  "worker_id": "uuid",
  "result": {
    "status": "success",
    "output": "Task completed successfully",
    "files_modified": ["src/auth.py"]
  }
}
```

**Response 200:**
```json
{
  "acknowledged": true,
  "completed_at": "2025-11-18T10:45:00Z"
}
```

#### POST /api/v1/queue/fail
Worker reports work order failure.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "work_order_id": "uuid",
  "worker_id": "uuid",
  "error_message": "Syntax error in generated code",
  "retry": true
}
```

**Response 200:**
```json
{
  "acknowledged": true,
  "retry_scheduled": true,
  "retry_at": "2025-11-18T10:50:00Z"
}
```

---

### Chat

#### GET /api/v1/chat/conversations
List chat conversations.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "items": [
    {
      "conversation_id": "uuid",
      "title": "Feature implementation discussion",
      "last_message_at": "2025-11-18T10:35:00Z",
      "message_count": 15
    }
  ]
}
```

#### GET /api/v1/chat/conversations/{conversation_id}/messages
Get messages in a conversation.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`, `page_size`
- `since` - ISO timestamp (get messages since)

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "sender_type": "worker",
      "sender_id": "uuid",
      "message": "I need clarification on the authentication flow",
      "message_type": "question",
      "created_at": "2025-11-18T10:35:00Z"
    }
  ]
}
```

#### POST /api/v1/chat/conversations/{conversation_id}/messages
Send a message.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "message": "Use OAuth2 with JWT tokens",
  "message_type": "response",
  "parent_message_id": "uuid"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "sender_type": "user",
  "sender_id": "uuid",
  "message": "Use OAuth2 with JWT tokens",
  "created_at": "2025-11-18T10:36:00Z"
}
```

#### WS /api/v1/chat/ws/{conversation_id}
WebSocket connection for real-time chat.

**Protocol:** WebSocket
**Auth:** JWT token as query parameter

**Client → Server:**
```json
{
  "type": "message",
  "content": "Use OAuth2 with JWT tokens"
}
```

**Server → Client:**
```json
{
  "type": "message",
  "id": "uuid",
  "sender_type": "worker",
  "sender_id": "uuid",
  "content": "Thanks! Implementing now...",
  "timestamp": "2025-11-18T10:37:00Z"
}
```

---

### Context Documents

#### POST /api/v1/context/documents
Create a context document.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "title": "Authentication Design",
  "document_type": "design",
  "content": "# Authentication Design\n\n...",
  "repository_url": "https://github.com/org/repo",
  "tags": ["auth", "design"]
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "title": "Authentication Design",
  "document_type": "design",
  "created_at": "2025-11-18T10:30:00Z",
  "version": 1
}
```

#### GET /api/v1/context/documents
List context documents.

**Query Parameters:**
- `document_type` - Filter by type
- `repository_url` - Filter by repository
- `tags` - Filter by tags (comma-separated)
- `search` - Full-text search

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Authentication Design",
      "document_type": "design",
      "tags": ["auth", "design"],
      "created_at": "2025-11-18T10:30:00Z"
    }
  ]
}
```

#### GET /api/v1/context/documents/{document_id}
Get document details.

**Response 200:**
```json
{
  "id": "uuid",
  "title": "Authentication Design",
  "document_type": "design",
  "content": "# Authentication Design\n\n...",
  "repository_url": "https://github.com/org/repo",
  "tags": ["auth", "design"],
  "created_by": "uuid",
  "created_at": "2025-11-18T10:30:00Z",
  "version": 1
}
```

---

### Executions

#### GET /api/v1/executions
List task executions.

**Query Parameters:**
- `task_id` - Filter by task
- `worker_id` - Filter by worker
- `status` - Filter by status

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "task_id": "uuid",
      "worker_id": "uuid",
      "status": "completed",
      "duration_seconds": 125,
      "started_at": "2025-11-18T10:30:00Z",
      "completed_at": "2025-11-18T10:32:05Z"
    }
  ]
}
```

#### GET /api/v1/executions/{execution_id}
Get execution details.

**Response 200:**
```json
{
  "id": "uuid",
  "task_id": "uuid",
  "worker_id": "uuid",
  "status": "completed",
  "exit_code": 0,
  "metrics": {
    "files_modified": 3,
    "lines_added": 145,
    "lines_removed": 23
  },
  "duration_seconds": 125,
  "started_at": "2025-11-18T10:30:00Z",
  "completed_at": "2025-11-18T10:32:05Z"
}
```

#### GET /api/v1/executions/{execution_id}/logs
Get execution logs.

**Response 200:**
```json
{
  "items": [
    {
      "level": "INFO",
      "message": "Starting task execution",
      "logged_at": "2025-11-18T10:30:00Z"
    }
  ]
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success, no response body
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict
- `422 Unprocessable Entity` - Semantic error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service down

### Error Codes

- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_REQUIRED` - No auth token provided
- `INVALID_TOKEN` - Token is invalid or expired
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `RESOURCE_CONFLICT` - Resource already exists
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Unexpected server error

## Rate Limiting

### Limits
- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Per endpoint**: Varies (e.g., auth: 10/minute)

### Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1637251200
```

### Response (429)
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 seconds"
  }
}
```

## Pagination

### Query Parameters
- `page` - Page number (1-indexed)
- `page_size` - Items per page (max: 100)

### Response Format
```json
{
  "items": [...],
  "total": 1000,
  "page": 1,
  "page_size": 20,
  "pages": 50
}
```

## Filtering & Sorting

### Filtering
- Use query parameters matching field names
- Multiple values: comma-separated
- Example: `?status=pending,in_progress&priority=high`

### Sorting
- `sort` - Field name
- `order` - `asc` or `desc`
- Example: `?sort=created_at&order=desc`

## CORS

### Allowed Origins
- Development: `http://localhost:3000`, `http://localhost:5173`
- Production: Configured per deployment

### Allowed Methods
- `GET`, `POST`, `PATCH`, `DELETE`, `OPTIONS`

### Allowed Headers
- `Content-Type`, `Authorization`, `X-Request-ID`

## OpenAPI Documentation

### Swagger UI
- URL: `/docs`
- Interactive API documentation
- Try-it-now functionality

### ReDoc
- URL: `/redoc`
- Alternative documentation view

### OpenAPI Schema
- URL: `/openapi.json`
- Machine-readable API schema
