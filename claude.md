# AgentVine

## Project Overview

AgentVine is a hybrid agent/human event-driven orchestration system designed for software development workflows. The system uses multiple Claude Code workers running in headless mode, coordinated by either human operators or LLM agents, to execute development tasks collaboratively.

### Core Concept

Development and development tasks are driven by a series of autonomous Claude Code workers, controlled by a human or another LLM agent (which could also be a Claude Code worker) depending on the type of task being performed. This creates a flexible, scalable development workflow that can adapt to various levels of automation.

## Architecture

### Work Queuing System

- **Workers**: Each worker obtains a work "order" from a distributed queue
- **Task Execution**: Workers complete instructions autonomously or request further guidance
- **Response Mechanism**: Workers drop messages onto the queue when they need clarification or have completed tasks
- **Intelligent Routing**: Based on metadata (task type, permissions, complexity), a chat controller either:
  - Displays the message in a chat window for human response
  - Generates the response automatically with instructions for the worker

### Context Management

- **Repository-Based**: The queue is initialized on a specific repository
- **Shared Context**: Each worker and controller has Claude Code level code context
- **Controller Knowledge**: The controller maintains:
  - Design documents
  - Implementation plans
  - Planning documentation
  - Test specifications
  - Work assignment records

### Chat Interface

A standard streaming interactive chat application that:
- Displays worker requests and status updates
- Accepts human input when needed
- Routes responses back to the appropriate queue
- Provides real-time visibility into the development process

## Technology Stack

### Core Language
- **Python 3.13**: Primary development language

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Click**: CLI creation framework
- **Rich**: Terminal formatting and beautiful output
- **uv**: Fast Python package installer and resolver
- **Pydantic**: Data validation using Python type annotations
- **Marshmallow**: Object serialization/deserialization

### Frontend
- **React**: UI component library
- **Vite**: Fast build tool and dev server
- **Shad.cn**: Component library and design system

### Queue Management
- **RQ (Redis Queue)**: Simple Python job queue
- **RQ Dashboard**: Web-based monitoring for RQ

### Development Tools
- **Ruff**: Fast Python linter (strict mode)
- **pytest**: Testing framework
- **hypothesis**: Property-based testing
- **behave**: BDD testing framework

### Database
- **SQLite**: For testing and development
- **PostgreSQL**: For production deployment

### Additional Technologies
- **Redis**: Backend for RQ queue system
- **Docker**: Containerization for workers and services
- **Docker Compose**: Multi-container orchestration
- **WebSockets**: Real-time communication for chat
- **JWT**: Authentication and authorization
- **Alembic**: Database migrations
- **httpx**: Async HTTP client

## Project Structure

```
AgentVine/
├── backend/               # FastAPI backend application
│   ├── app/
│   │   ├── api/          # API routes and endpoints
│   │   ├── core/         # Core configuration and settings
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── workers/      # RQ worker definitions
│   ├── tests/            # Backend tests
│   └── pyproject.toml    # Python dependencies
├── frontend/             # React frontend application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API clients
│   │   └── utils/        # Utility functions
│   ├── tests/            # Frontend tests
│   └── package.json      # Node dependencies
├── workers/              # Claude Code worker implementations
│   ├── base/            # Base worker classes
│   ├── specialized/     # Specialized worker types
│   └── config/          # Worker configuration
├── controller/           # Chat controller logic
│   ├── routing/         # Message routing logic
│   ├── policies/        # Decision policies
│   └── context/         # Context management
├── cli/                 # CLI tools for management
├── docs/                # Documentation
│   ├── design/          # Design documents
│   ├── planning/        # Planning documents
│   └── guides/          # User guides
├── tests/               # Integration tests
├── scripts/             # Development scripts
├── docker/              # Docker configurations
├── .github/             # GitHub workflows
└── claude.md            # This file
```

## Key Components

### 1. Worker System
- Autonomous Claude Code instances running in headless mode
- Poll queue for work orders
- Execute development tasks (coding, testing, documentation)
- Request clarification when needed
- Report completion status

### 2. Queue System
- Built on RQ (Redis Queue)
- Handles work distribution
- Manages message passing between workers and controller
- Includes metadata for routing decisions:
  - Task type (feature, bugfix, documentation, etc.)
  - Permission level (autonomous, supervised, human-required)
  - Priority
  - Context references

### 3. Chat Controller
- Receives messages from workers
- Makes routing decisions based on metadata
- For automated responses:
  - Analyzes worker request
  - Generates appropriate instructions
  - Enqueues response
- For human responses:
  - Displays in chat interface
  - Waits for human input
  - Forwards response to worker

### 4. Chat Interface
- Real-time streaming chat
- Displays worker requests and status
- Accepts human input
- Shows system state and active workers
- Provides visibility into queue status

## Development Workflow

### Typical Task Flow

1. **Task Creation**: Human or system creates a work order with metadata
2. **Queue Assignment**: Work order is placed in queue
3. **Worker Pickup**: Available worker claims the work order
4. **Execution**: Worker begins task execution with full repo context
5. **Decision Point**:
   - If autonomous: Worker completes and reports
   - If clarification needed: Worker sends question to queue
6. **Controller Routing**:
   - Automated tasks: Controller generates response
   - Complex/critical tasks: Controller routes to human
7. **Response**: Instructions sent back to worker
8. **Completion**: Worker completes task and reports results
9. **Validation**: System validates completion (tests, linting, etc.)

### Worker Types

- **Feature Workers**: Implement new features
- **Bugfix Workers**: Debug and fix issues
- **Test Workers**: Write and execute tests
- **Documentation Workers**: Generate and update docs
- **Refactoring Workers**: Code improvement and optimization
- **Review Workers**: Code review and analysis

## Getting Started

### Prerequisites
- Python 3.13+
- Node.js 18+
- Redis
- PostgreSQL (for production)
- Docker (recommended)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd AgentVine

# Backend setup
cd backend
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"

# Frontend setup
cd ../frontend
npm install

# Start Redis (required for queue)
redis-server

# Run migrations
cd ../backend
alembic upgrade head
```

### Running the System

```bash
# Terminal 1: Start backend API
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start RQ workers
cd backend
rq worker --with-scheduler

# Terminal 3: Start RQ Dashboard
rq-dashboard

# Terminal 4: Start frontend
cd frontend
npm run dev

# Terminal 5: Start controller
cd controller
python main.py
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
cd tests
behave
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=sqlite:///./test.db  # or postgresql://...

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here

# Workers
MAX_WORKERS=5
WORKER_TIMEOUT=3600

# Claude API
ANTHROPIC_API_KEY=your-api-key-here
```

### Worker Configuration

Workers can be configured with:
- Maximum concurrent tasks
- Specialization areas
- Permission levels
- Timeout settings
- Context window size

## Coding Standards

### Python (Ruff - Strict Mode)
- All code must pass Ruff linting in strict mode
- Type hints required for all functions
- Docstrings required for public APIs
- Maximum line length: 100 characters

### Testing Requirements
- Minimum 80% code coverage
- Unit tests for all business logic
- Integration tests for API endpoints
- BDD scenarios for user workflows
- Property-based tests for complex logic

### Commit Standards
- Conventional commits format
- All commits must pass CI checks
- No direct commits to main branch
- All changes via pull requests

## Security Considerations

- Workers run in sandboxed environments
- Permission-based task assignment
- Human approval required for:
  - Database migrations
  - Deployment operations
  - Security-sensitive changes
- API authentication via JWT
- Rate limiting on all endpoints

## Monitoring and Observability

- RQ Dashboard for queue monitoring
- Structured logging (JSON format)
- Performance metrics collection
- Worker health checks
- Task execution analytics

## Future Enhancements

- Multi-repository support
- Advanced worker specialization
- Machine learning for routing decisions
- Integration with GitHub/GitLab APIs
- Distributed worker pools
- Advanced context sharing mechanisms
- Worker collaboration protocols

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on:
- Code style
- Testing requirements
- PR process
- Issue reporting

## License

See [LICENSE](./LICENSE) for details.

## Contact

For questions, issues, or contributions, please refer to the project's issue tracker.
