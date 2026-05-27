from typing import Annotated
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session_maker
from src.models import TasksOrm
from src.services.charts import get_last_column_for_project
from src.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[TaskRead])
async def list_tasks(session: SessionDep) -> list[TaskRead]:
    result = await session.execute(select(TasksOrm))
    return list(result.scalars().all())


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: UUID, session: SessionDep) -> TaskRead:
    task = await session.get(TasksOrm, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, session: SessionDep) -> TaskRead:
    last_column = await get_last_column_for_project(session, payload.project_id)
    task = TasksOrm(
        title=payload.title,
        description=payload.description,
        deadline=payload.deadline,
        project_id=payload.project_id,
        column_id=payload.column_id,
    )

    if last_column is not None and payload.column_id == last_column.id:
        task.done_at = datetime.now(timezone.utc)

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, session: SessionDep) -> None:
    task = await session.get(TasksOrm, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    await session.delete(task)
    await session.commit()
    return None


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    session: SessionDep,
) -> TaskRead:
    task = await session.get(TasksOrm, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    old_column_id = task.column_id
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now(timezone.utc)

    last_column = await get_last_column_for_project(session, task.project_id)
    if last_column is not None:
        if task.column_id == last_column.id:
            if old_column_id != last_column.id or task.done_at is None:
                task.done_at = datetime.now(timezone.utc)
        else:
            task.done_at = None

    await session.commit()
    await session.refresh(task)
    return task
