"""Session API endpoints."""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Session, SessionStatus
from app.schemas.session import SessionCreate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Session:
    """Create a new session mapping.

    Args:
        session_data: Session creation data.
        db: Database session.

    Returns:
        Session: Created session.
    """
    session = Session(
        session_id=session_data.session_id,
        worker_id=session_data.worker_id,
        task_id=session_data.task_id,
        status=SessionStatus.ACTIVE,
        last_activity_at=datetime.utcnow(),
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return session


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: SessionStatus | None = None,
) -> list[Session]:
    """List all sessions.

    Args:
        db: Database session.
        status_filter: Optional status filter.

    Returns:
        list[Session]: List of sessions.
    """
    query = select(Session).order_by(Session.created_at.desc())

    if status_filter:
        query = query.where(Session.status == status_filter)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Session:
    """Get session by ID.

    Args:
        session_id: Session UUID.
        db: Database session.

    Returns:
        Session: Session instance.

    Raises:
        HTTPException: If session not found.
    """
    session = await db.get(Session, session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    return session


@router.post("/{session_id}/heartbeat", response_model=SessionResponse)
async def session_heartbeat(
    session_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Session:
    """Update session activity timestamp.

    Args:
        session_id: Session UUID.
        db: Database session.

    Returns:
        Session: Updated session.

    Raises:
        HTTPException: If session not found.
    """
    session = await db.get(Session, session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    session.last_activity_at = datetime.utcnow()

    await db.commit()
    await db.refresh(session)

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_session(
    session_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Terminate a session.

    Args:
        session_id: Session UUID.
        db: Database session.

    Raises:
        HTTPException: If session not found.
    """
    session = await db.get(Session, session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    session.status = SessionStatus.TERMINATED
    session.terminated_at = datetime.utcnow()

    await db.commit()
