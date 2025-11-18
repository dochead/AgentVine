"""Task API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Task, TaskStatus, WorkOrder
from app.models.work_order import WorkOrderPriority, WorkOrderStatus
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.queue_manager import QueueManager

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Task:
    """Create a new task and enqueue it.

    Args:
        task_data: Task creation data.
        db: Database session.

    Returns:
        Task: Created task.
    """
    # Create task
    task = Task(**task_data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Create work order
    work_order = WorkOrder(
        task_id=task.id,
        priority=WorkOrderPriority(task.priority.value),
        status=WorkOrderStatus.QUEUED,
    )
    db.add(work_order)
    await db.commit()
    await db.refresh(work_order)

    # Enqueue to Redis
    queue_manager = QueueManager()
    queue_manager.enqueue_work_order(
        work_order_id=work_order.id,
        task_data={
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type.value,
            "repository_url": task.repository_url,
            "branch_name": task.branch_name,
        },
        priority=WorkOrderPriority(task.priority.value),
    )

    return task


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: TaskStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Task]:
    """List tasks with optional filtering.

    Args:
        db: Database session.
        status_filter: Optional status filter.
        limit: Maximum number of results.
        offset: Number of results to skip.

    Returns:
        list[Task]: List of tasks.
    """
    query = select(Task).order_by(Task.created_at.desc()).limit(limit).offset(offset)

    if status_filter:
        query = query.where(Task.status == status_filter)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Task:
    """Get task by ID.

    Args:
        task_id: Task UUID.
        db: Database session.

    Returns:
        Task: Task instance.

    Raises:
        HTTPException: If task not found.
    """
    task = await db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Task:
    """Update task.

    Args:
        task_id: Task UUID.
        task_data: Task update data.
        db: Database session.

    Returns:
        Task: Updated task.

    Raises:
        HTTPException: If task not found.
    """
    task = await db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Handle completion timestamp
    if update_data.get("status") == TaskStatus.COMPLETED:
        from datetime import datetime

        task.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    return task
