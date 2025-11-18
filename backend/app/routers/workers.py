"""Worker API endpoints."""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Worker, WorkerStatus
from app.schemas.worker import WorkerCreate, WorkerHeartbeat, WorkerResponse

router = APIRouter(prefix="/workers", tags=["workers"])


@router.post("", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
async def register_worker(
    worker_data: WorkerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Worker:
    """Register a new worker.

    Args:
        worker_data: Worker registration data.
        db: Database session.

    Returns:
        Worker: Registered worker.
    """
    worker = Worker(
        name=worker_data.name,
        status=WorkerStatus.IDLE,
        last_heartbeat_at=datetime.utcnow(),
    )

    db.add(worker)
    await db.commit()
    await db.refresh(worker)

    return worker


@router.get("", response_model=list[WorkerResponse])
async def list_workers(
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: WorkerStatus | None = None,
) -> list[Worker]:
    """List all workers.

    Args:
        db: Database session.
        status_filter: Optional status filter.

    Returns:
        list[Worker]: List of workers.
    """
    query = select(Worker).order_by(Worker.created_at.desc())

    if status_filter:
        query = query.where(Worker.status == status_filter)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(
    worker_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Worker:
    """Get worker by ID.

    Args:
        worker_id: Worker UUID.
        db: Database session.

    Returns:
        Worker: Worker instance.

    Raises:
        HTTPException: If worker not found.
    """
    worker = await db.get(Worker, worker_id)

    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker {worker_id} not found",
        )

    return worker


@router.post("/{worker_id}/heartbeat", response_model=WorkerResponse)
async def worker_heartbeat(
    worker_id: uuid.UUID,
    heartbeat_data: WorkerHeartbeat,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Worker:
    """Update worker heartbeat and status.

    Args:
        worker_id: Worker UUID.
        heartbeat_data: Heartbeat data.
        db: Database session.

    Returns:
        Worker: Updated worker.

    Raises:
        HTTPException: If worker not found.
    """
    worker = await db.get(Worker, worker_id)

    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker {worker_id} not found",
        )

    # Update status and heartbeat
    worker.status = heartbeat_data.status
    worker.last_heartbeat_at = datetime.utcnow()

    await db.commit()
    await db.refresh(worker)

    return worker


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deregister_worker(
    worker_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Deregister a worker.

    Args:
        worker_id: Worker UUID.
        db: Database session.

    Raises:
        HTTPException: If worker not found.
    """
    worker = await db.get(Worker, worker_id)

    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker {worker_id} not found",
        )

    await db.delete(worker)
    await db.commit()
