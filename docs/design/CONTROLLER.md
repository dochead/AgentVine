# Controller Design

## Overview

The Chat Controller is the intelligent routing system that receives messages from workers, makes decisions about automation vs. human intervention, and coordinates responses. It acts as the orchestration layer between workers and humans.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chat Controller                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Message Receiver                        │  │
│  │  - Listen to worker_requests queue                   │  │
│  │  - Parse incoming messages                           │  │
│  │  - Validate message format                           │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                             │
│               ▼                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Routing Engine                          │  │
│  │  - Extract metadata                                  │  │
│  │  - Classify request type                             │  │
│  │  - Determine routing path                            │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                             │
│          ┌────┴────┐                                        │
│          ▼         ▼                                        │
│  ┌────────────┐  ┌────────────┐                           │
│  │ Automated  │  │   Human    │                           │
│  │  Handler   │  │  Handler   │                           │
│  └─────┬──────┘  └─────┬──────┘                           │
│        │               │                                   │
│        ▼               ▼                                   │
│  ┌────────────┐  ┌────────────────────────────────────┐  │
│  │  Response  │  │      Chat Interface                │  │
│  │ Generator  │  │  - Display to human                │  │
│  └─────┬──────┘  │  - Wait for input                  │  │
│        │         │  - Capture response                │  │
│        │         └─────┬──────────────────────────────┘  │
│        │               │                                   │
│        └───────┬───────┘                                   │
│                ▼                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Response Dispatcher                         │  │
│  │  - Format response                                   │  │
│  │  - Enqueue to controller_responses                   │  │
│  │  - Log interaction                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────┬──────────────────────────────────────────┘
                    │
                    ▼
             ┌────────────┐
             │   Redis    │
             │   Queue    │
             └────────────┘
```

## Core Components

### 1. Message Receiver

```python
from typing import Optional
from dataclasses import dataclass

class MessageReceiver:
    """Receives and parses worker messages."""

    def __init__(self, queue_client: QueueClient):
        self.queue_client = queue_client

    def poll(self) -> Optional[WorkerRequestMessage]:
        """Poll for new worker requests."""

        job = self.queue_client.worker_requests.dequeue()

        if job:
            return WorkerRequestMessage.from_dict(job.args[0])

        return None

    def validate_message(
        self,
        message: WorkerRequestMessage
    ) -> bool:
        """Validate message format and required fields."""

        required_fields = [
            "id", "worker_id", "work_order_id",
            "task_id", "request_type", "message"
        ]

        for field in required_fields:
            if not getattr(message, field):
                logger.error(f"Missing required field: {field}")
                return False

        return True
```

### 2. Routing Engine

```python
from enum import Enum

class RoutingDecision(str, Enum):
    AUTOMATED = "automated"
    HUMAN = "human"
    ESCALATE = "escalate"

class RoutingEngine:
    """Determines routing path for worker requests."""

    def __init__(self, policy_engine: PolicyEngine):
        self.policy_engine = policy_engine

    def route(
        self,
        message: WorkerRequestMessage,
        context: Dict[str, Any]
    ) -> RoutingDecision:
        """Determine routing decision."""

        # Extract metadata
        task_type = context.get("task_type")
        permission_level = context.get("permission_level")
        priority = context.get("priority")

        # Apply policies
        decision = self.policy_engine.evaluate(
            request_type=message.request_type,
            task_type=task_type,
            permission_level=permission_level,
            priority=priority,
            message_content=message.message,
        )

        logger.info(
            f"Routing decision for {message.id}: {decision}"
        )

        return decision
```

### 3. Policy Engine

```python
from typing import Callable, List

@dataclass
class Policy:
    """Routing policy definition."""

    name: str
    condition: Callable[[Dict[str, Any]], bool]
    decision: RoutingDecision
    priority: int = 0

class PolicyEngine:
    """Evaluates policies to make routing decisions."""

    def __init__(self):
        self.policies: List[Policy] = []
        self._register_default_policies()

    def _register_default_policies(self):
        """Register default routing policies."""

        # Human-required permission level always goes to human
        self.add_policy(Policy(
            name="human_required",
            condition=lambda ctx: ctx.get("permission_level") == "human_required",
            decision=RoutingDecision.HUMAN,
            priority=100
        ))

        # Critical priority always goes to human
        self.add_policy(Policy(
            name="critical_priority",
            condition=lambda ctx: ctx.get("priority") == "critical",
            decision=RoutingDecision.HUMAN,
            priority=90
        ))

        # Approval requests go to human
        self.add_policy(Policy(
            name="approval_required",
            condition=lambda ctx: ctx.get("request_type") == "approval",
            decision=RoutingDecision.HUMAN,
            priority=80
        ))

        # Simple clarifications can be automated
        self.add_policy(Policy(
            name="simple_clarification",
            condition=lambda ctx: (
                ctx.get("request_type") == "clarification" and
                ctx.get("permission_level") == "autonomous" and
                self._is_simple_question(ctx.get("message_content", ""))
            ),
            decision=RoutingDecision.AUTOMATED,
            priority=50
        ))

        # Default to human for safety
        self.add_policy(Policy(
            name="default_human",
            condition=lambda ctx: True,
            decision=RoutingDecision.HUMAN,
            priority=0
        ))

    def add_policy(self, policy: Policy):
        """Add a routing policy."""
        self.policies.append(policy)
        self.policies.sort(key=lambda p: p.priority, reverse=True)

    def evaluate(self, **context) -> RoutingDecision:
        """Evaluate policies and return decision."""

        for policy in self.policies:
            if policy.condition(context):
                logger.info(f"Policy '{policy.name}' matched")
                return policy.decision

        # Should never reach here due to default policy
        return RoutingDecision.HUMAN

    @staticmethod
    def _is_simple_question(message: str) -> bool:
        """Check if question is simple enough for automation."""

        simple_patterns = [
            "which library should i use",
            "should i use",
            "do you prefer",
            "is it ok to",
            "can i",
        ]

        message_lower = message.lower()
        return any(pattern in message_lower for pattern in simple_patterns)
```

### 4. Automated Handler

```python
from anthropic import Anthropic

class AutomatedHandler:
    """Handles automated responses using LLM."""

    def __init__(self, context_manager: ContextManager):
        self.anthropic = Anthropic()
        self.context_manager = context_manager

    def generate_response(
        self,
        message: WorkerRequestMessage,
        context: Dict[str, Any]
    ) -> str:
        """Generate automated response."""

        # Retrieve relevant context
        design_docs = self.context_manager.get_design_documents(
            context.get("repository_url")
        )
        task_context = self.context_manager.get_task_context(
            message.task_id
        )

        # Build prompt
        prompt = self._build_prompt(
            message,
            design_docs,
            task_context
        )

        # Call Claude API
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return response.content[0].text

    def _build_prompt(
        self,
        message: WorkerRequestMessage,
        design_docs: List[str],
        task_context: Dict[str, Any]
    ) -> str:
        """Build prompt for LLM."""

        context_str = "\n\n".join([
            f"# Design Document\n{doc}" for doc in design_docs
        ])

        return f"""You are a technical lead reviewing a question from a worker implementing a task.

# Task Context
Task ID: {message.task_id}
Task Type: {task_context.get('task_type')}
Title: {task_context.get('title')}
Description: {task_context.get('description')}

# Design Documents
{context_str}

# Worker Question
{message.message}

# Additional Context
{json.dumps(message.context, indent=2)}

Provide a clear, concise answer to guide the worker. Focus on:
1. Following the design documents
2. Best practices for the technology stack
3. Consistency with existing codebase
4. Security and performance considerations

Answer:"""
```

### 5. Human Handler

```python
class HumanHandler:
    """Handles human interaction via chat interface."""

    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service
        self.pending_responses: Dict[str, asyncio.Event] = {}

    async def request_human_response(
        self,
        message: WorkerRequestMessage,
        context: Dict[str, Any]
    ) -> str:
        """Request human response via chat interface."""

        # Create chat message
        chat_message = await self.chat_service.create_message(
            conversation_id=message.conversation_id,
            sender_type="worker",
            sender_id=message.worker_id,
            message=message.message,
            message_type=message.request_type,
            metadata={
                "task_id": message.task_id,
                "work_order_id": message.work_order_id,
                "context": context,
            }
        )

        # Wait for human response
        event = asyncio.Event()
        self.pending_responses[message.id] = event

        # Timeout after 30 minutes
        try:
            await asyncio.wait_for(event.wait(), timeout=1800)
        except asyncio.TimeoutError:
            logger.warning(f"No human response for {message.id}")
            raise

        # Retrieve response
        response = await self.chat_service.get_response(
            message.id
        )

        return response.message

    async def receive_human_response(
        self,
        request_id: str,
        response: str
    ):
        """Receive human response from chat interface."""

        if request_id in self.pending_responses:
            # Store response
            await self.chat_service.create_message(
                conversation_id=response.conversation_id,
                sender_type="user",
                sender_id=response.user_id,
                message=response,
                message_type="response",
                parent_message_id=request_id,
            )

            # Signal waiting coroutine
            self.pending_responses[request_id].set()
```

### 6. Context Manager

```python
class ContextManager:
    """Manages shared context and knowledge base."""

    def __init__(self, db_session):
        self.db = db_session

    async def get_design_documents(
        self,
        repository_url: str
    ) -> List[str]:
        """Retrieve design documents for repository."""

        docs = await self.db.execute(
            select(ContextDocument)
            .filter(
                ContextDocument.repository_url == repository_url,
                ContextDocument.document_type == "design"
            )
        )

        return [doc.content for doc in docs.scalars()]

    async def get_task_context(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """Retrieve context for a task."""

        task = await self.db.get(Task, task_id)

        if not task:
            return {}

        return {
            "task_id": task.id,
            "task_type": task.task_type,
            "title": task.title,
            "description": task.description,
            "repository_url": task.repository_url,
            "branch_name": task.branch_name,
            "context": task.context,
        }

    async def store_context_document(
        self,
        title: str,
        document_type: str,
        content: str,
        repository_url: str,
        created_by: str
    ) -> ContextDocument:
        """Store a new context document."""

        doc = ContextDocument(
            title=title,
            document_type=document_type,
            content=content,
            repository_url=repository_url,
            created_by=created_by,
        )

        self.db.add(doc)
        await self.db.commit()

        return doc
```

### 7. Response Dispatcher

```python
class ResponseDispatcher:
    """Dispatches responses back to workers."""

    def __init__(self, queue_client: QueueClient):
        self.queue_client = queue_client

    async def dispatch(
        self,
        request: WorkerRequestMessage,
        response_message: str,
        generated_by: str,
        responder_id: Optional[str] = None
    ):
        """Dispatch response to worker."""

        response = ControllerResponseMessage(
            id=str(uuid.uuid4()),
            request_id=request.id,
            worker_id=request.worker_id,
            work_order_id=request.work_order_id,
            response_type="answer",
            message=response_message,
            generated_by=generated_by,
            responder_id=responder_id,
            created_at=datetime.now(),
        )

        # Enqueue response
        self.queue_client.enqueue_controller_response(response)

        logger.info(
            f"Dispatched response {response.id} to worker {request.worker_id}"
        )
```

## Controller Main Loop

```python
class ChatController:
    """Main controller orchestrating the system."""

    def __init__(self, config: ControllerConfig):
        self.config = config

        # Initialize components
        self.queue_client = QueueClient(config.redis_url)
        self.db = DatabaseSession(config.database_url)
        self.message_receiver = MessageReceiver(self.queue_client)
        self.context_manager = ContextManager(self.db)
        self.policy_engine = PolicyEngine()
        self.routing_engine = RoutingEngine(self.policy_engine)
        self.automated_handler = AutomatedHandler(self.context_manager)
        self.human_handler = HumanHandler(ChatService(self.db))
        self.response_dispatcher = ResponseDispatcher(self.queue_client)

    async def run(self):
        """Main controller loop."""

        logger.info("Chat Controller starting")

        while True:
            try:
                # Poll for worker requests
                message = self.message_receiver.poll()

                if message:
                    # Process message
                    await self.process_message(message)
                else:
                    # No messages, wait
                    await asyncio.sleep(self.config.poll_interval)

            except KeyboardInterrupt:
                logger.info("Shutdown signal received")
                break
            except Exception as e:
                logger.error(f"Error in controller loop: {e}")
                await asyncio.sleep(60)

    async def process_message(
        self,
        message: WorkerRequestMessage
    ):
        """Process worker request message."""

        # Validate message
        if not self.message_receiver.validate_message(message):
            logger.error(f"Invalid message: {message.id}")
            return

        # Get task context
        context = await self.context_manager.get_task_context(
            message.task_id
        )

        # Route message
        decision = self.routing_engine.route(message, context)

        # Handle based on decision
        if decision == RoutingDecision.AUTOMATED:
            response = await self.automated_handler.generate_response(
                message,
                context
            )
            generated_by = "automated"
            responder_id = None

        elif decision == RoutingDecision.HUMAN:
            response = await self.human_handler.request_human_response(
                message,
                context
            )
            generated_by = "human"
            responder_id = "user_id"  # Get from chat response

        else:
            logger.error(f"Unknown routing decision: {decision}")
            return

        # Dispatch response
        await self.response_dispatcher.dispatch(
            message,
            response,
            generated_by,
            responder_id
        )
```

## Configuration

```python
@dataclass
class ControllerConfig:
    """Controller configuration."""

    redis_url: str
    database_url: str
    anthropic_api_key: str

    poll_interval: int = 5  # seconds
    max_concurrent_requests: int = 10

    # Policy configuration
    auto_response_enabled: bool = True
    auto_response_confidence_threshold: float = 0.8
```

## Deployment

```dockerfile
# Dockerfile.controller
FROM python:3.13-slim

WORKDIR /app

COPY controller/ /app/controller/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "controller.main"]
```

```yaml
# docker-compose.controller.yml
services:
  controller:
    build:
      context: .
      dockerfile: Dockerfile.controller
    environment:
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - DATABASE_URL=postgresql://user:pass@db:5432/agentvine
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis
      - db
    restart: unless-stopped
```

## Monitoring

```python
from prometheus_client import Counter, Histogram

# Metrics
requests_received = Counter(
    "controller_requests_received_total",
    "Total requests received",
    ["request_type"]
)

routing_decisions = Counter(
    "controller_routing_decisions_total",
    "Routing decisions",
    ["decision"]
)

response_time = Histogram(
    "controller_response_time_seconds",
    "Time to generate response",
    ["handler_type"]
)
```

## Testing

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def controller_config():
    return ControllerConfig(
        redis_url="redis://localhost:6379/0",
        database_url="sqlite:///test.db",
        anthropic_api_key="test-key"
    )

@pytest.mark.asyncio
async def test_routing_human_required():
    policy_engine = PolicyEngine()
    routing_engine = RoutingEngine(policy_engine)

    decision = routing_engine.route(
        Mock(request_type="approval"),
        {"permission_level": "human_required"}
    )

    assert decision == RoutingDecision.HUMAN
```
