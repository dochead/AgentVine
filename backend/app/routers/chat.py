"""Chat API endpoints for worker-human communication."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    HumanResponseCreate,
    WorkerMessageRequest,
    ConversationResponse,
)
from app.services.orchestrator import EventOrchestrator

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/worker-message", response_model=dict)
async def send_worker_message(
    message_data: WorkerMessageRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Worker sends a message to human (via orchestrator).

    Phase 1: All messages are passed through to human chat interface.

    Args:
        message_data: Message from worker
        db: Database session

    Returns:
        dict with routing information
    """
    orchestrator = EventOrchestrator(db)

    result = await orchestrator.handle_worker_message(
        session_id=message_data.session_id,
        worker_id=message_data.worker_id,
        message=message_data.message,
        task_id=message_data.task_id,
    )

    return result


@router.post("/human-response", response_model=dict)
async def send_human_response(
    response_data: HumanResponseCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Human responds to a worker message.

    Args:
        response_data: Human's response
        db: Database session

    Returns:
        dict with routing information
    """
    orchestrator = EventOrchestrator(db)

    result = await orchestrator.handle_human_response(
        message_id=response_data.message_id,
        response=response_data.response,
    )

    return result


@router.get("/pending", response_model=list[dict])
async def get_pending_messages(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50,
) -> list[dict]:
    """
    Get pending worker messages awaiting human response.

    Args:
        db: Database session
        limit: Maximum number of messages

    Returns:
        list of pending messages
    """
    orchestrator = EventOrchestrator(db)
    messages = await orchestrator.get_pending_worker_messages(limit=limit)
    return messages


@router.get("/conversation/{session_id}", response_model=list[dict])
async def get_conversation(
    session_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[dict]:
    """
    Get full conversation for a session.

    Args:
        session_id: Claude Code session ID
        db: Database session

    Returns:
        list of messages in chronological order
    """
    orchestrator = EventOrchestrator(db)
    messages = await orchestrator.get_session_conversation(session_id)
    return messages


@router.post("/cleanup-sessions", response_model=dict)
async def cleanup_idle_sessions(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Check and cleanup idle sessions.

    Should be called periodically (e.g., every 5 minutes).

    Returns:
        dict with cleanup statistics
    """
    orchestrator = EventOrchestrator(db)
    stats = await orchestrator.check_and_cleanup_idle_sessions()
    return stats
