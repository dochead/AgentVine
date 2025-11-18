"""
Event Orchestrator Service

Manages the routing of messages between workers and humans:
- Maps Claude session IDs to tasks
- Routes worker requests to human chat interface (pass-through mode)
- Manages session lifecycle (keep-alive, termination)
- Queues messages for human review
- Routes human responses back to workers
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session, SessionStatus
from app.models.chat_message import ChatMessage, MessageDirection
from app.models.task import Task
from app.models.worker import Worker
from app.services.queue_manager import QueueManager


class EventOrchestrator:
    """
    Orchestrates communication between workers and humans.

    Phase 1 Implementation:
    - All worker messages are passed through to human chat interface
    - Session mapping maintains context between task and Claude session
    - Session lifecycle management keeps sessions alive when beneficial
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.queue_manager = QueueManager()
        # Session keep-alive settings
        self.session_idle_timeout = timedelta(minutes=30)
        self.session_max_lifetime = timedelta(hours=4)

    async def handle_worker_message(
        self,
        session_id: str,
        worker_id: uuid.UUID,
        message: str,
        task_id: Optional[uuid.UUID] = None
    ) -> dict:
        """
        Handle incoming message from worker.

        Phase 1: Pass-through mode - all messages go to human chat interface.

        Args:
            session_id: Claude Code session ID
            worker_id: Worker UUID
            message: Message content from worker
            task_id: Optional task ID (if known)

        Returns:
            dict with routing information and chat message ID
        """
        # Get or create session mapping
        session = await self._get_or_create_session(session_id, worker_id, task_id)

        # Create chat message record
        chat_message = ChatMessage(
            session_id=session.id,
            direction=MessageDirection.WORKER_TO_HUMAN,
            content=message,
            sender_worker_id=worker_id,
        )
        self.db.add(chat_message)
        await self.db.commit()
        await self.db.refresh(chat_message)

        # Update session activity
        session.last_activity_at = datetime.utcnow()
        await self.db.commit()

        # Enqueue worker request for human review
        self.queue_manager.enqueue_worker_request(
            chat_message.id,
            {
                "message_id": str(chat_message.id),
                "session_id": session_id,
                "worker_id": str(worker_id),
                "task_id": str(session.task_id) if session.task_id else None,
                "message": message,
                "timestamp": chat_message.created_at.isoformat(),
            }
        )

        return {
            "message_id": str(chat_message.id),
            "session_id": session_id,
            "routed_to": "human",
            "status": "queued_for_human_review",
        }

    async def handle_human_response(
        self,
        message_id: uuid.UUID,
        response: str,
    ) -> dict:
        """
        Handle response from human to worker.

        Args:
            message_id: Original chat message ID being responded to
            response: Human's response content

        Returns:
            dict with routing information
        """
        # Get original message to find session
        result = await self.db.execute(
            select(ChatMessage).where(ChatMessage.id == message_id)
        )
        original_message = result.scalar_one_or_none()

        if not original_message:
            raise ValueError(f"Message {message_id} not found")

        # Create response message
        response_message = ChatMessage(
            session_id=original_message.session_id,
            direction=MessageDirection.HUMAN_TO_WORKER,
            content=response,
            in_reply_to_id=message_id,
        )
        self.db.add(response_message)
        await self.db.commit()
        await self.db.refresh(response_message)

        # Update session activity
        result = await self.db.execute(
            select(Session).where(Session.id == original_message.session_id)
        )
        session = result.scalar_one_or_none()

        if session:
            session.last_activity_at = datetime.utcnow()
            await self.db.commit()

        # Enqueue response for worker
        self.queue_manager.enqueue_controller_response(
            response_message.id,
            {
                "message_id": str(response_message.id),
                "original_message_id": str(message_id),
                "session_id": session.session_id if session else None,
                "response": response,
                "timestamp": response_message.created_at.isoformat(),
            }
        )

        return {
            "message_id": str(response_message.id),
            "original_message_id": str(message_id),
            "status": "queued_for_worker",
        }

    async def get_pending_worker_messages(self, limit: int = 50) -> list[dict]:
        """
        Get pending messages from workers awaiting human response.

        Returns messages that haven't been replied to yet.
        """
        result = await self.db.execute(
            select(ChatMessage)
            .where(
                ChatMessage.direction == MessageDirection.WORKER_TO_HUMAN,
                ChatMessage.in_reply_to_id.is_(None),  # Not a reply itself
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()

        # Check which messages have responses
        pending = []
        for msg in messages:
            # Check if there's a response
            response_result = await self.db.execute(
                select(ChatMessage)
                .where(ChatMessage.in_reply_to_id == msg.id)
                .limit(1)
            )
            has_response = response_result.scalar_one_or_none() is not None

            if not has_response:
                # Get session info
                session_result = await self.db.execute(
                    select(Session).where(Session.id == msg.session_id)
                )
                session = session_result.scalar_one_or_none()

                pending.append({
                    "message_id": str(msg.id),
                    "session_id": session.session_id if session else None,
                    "task_id": str(session.task_id) if session and session.task_id else None,
                    "worker_id": str(msg.sender_worker_id) if msg.sender_worker_id else None,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                })

        return pending

    async def get_session_conversation(self, session_id: str) -> list[dict]:
        """
        Get full conversation for a session.

        Args:
            session_id: Claude Code session ID

        Returns:
            List of messages in chronological order
        """
        # Get session
        result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            return []

        # Get all messages for this session
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.asc())
        )
        messages = result.scalars().all()

        return [
            {
                "message_id": str(msg.id),
                "direction": msg.direction.value,
                "content": msg.content,
                "in_reply_to": str(msg.in_reply_to_id) if msg.in_reply_to_id else None,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]

    async def _get_or_create_session(
        self,
        session_id: str,
        worker_id: uuid.UUID,
        task_id: Optional[uuid.UUID] = None,
    ) -> Session:
        """Get existing session or create new one."""
        result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        if session:
            # Update existing session
            session.last_activity_at = datetime.utcnow()
            if task_id and not session.task_id:
                session.task_id = task_id
            session.status = SessionStatus.ACTIVE
            await self.db.commit()
            return session

        # Create new session
        session = Session(
            session_id=session_id,
            worker_id=worker_id,
            task_id=task_id,
            status=SessionStatus.ACTIVE,
            last_activity_at=datetime.utcnow(),
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def check_and_cleanup_idle_sessions(self) -> dict:
        """
        Check for idle sessions and terminate them if necessary.

        Session lifecycle policy:
        - Mark as IDLE if no activity for session_idle_timeout (30 min)
        - Terminate if idle for too long or max lifetime exceeded

        Returns:
            dict with cleanup statistics
        """
        now = datetime.utcnow()
        idle_cutoff = now - self.session_idle_timeout
        max_lifetime_cutoff = now - self.session_max_lifetime

        # Get active sessions
        result = await self.db.execute(
            select(Session).where(Session.status == SessionStatus.ACTIVE)
        )
        active_sessions = result.scalars().all()

        marked_idle = 0
        terminated = 0

        for session in active_sessions:
            # Check max lifetime
            if session.created_at < max_lifetime_cutoff:
                session.status = SessionStatus.TERMINATED
                session.terminated_at = now
                terminated += 1
                continue

            # Check idle timeout
            if session.last_activity_at < idle_cutoff:
                session.status = SessionStatus.IDLE
                marked_idle += 1

        await self.db.commit()

        return {
            "marked_idle": marked_idle,
            "terminated": terminated,
            "checked_at": now.isoformat(),
        }
