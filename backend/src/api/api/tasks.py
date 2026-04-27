from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker
from src.models import TasksOrm
from src.schemas.task import TaskCreate, TaskRead



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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, session: SessionDep) -> TaskRead:
    # # Простая проверка уникальности таски.
    # existing = await session.execute(select(TasksOrm).where(TasksOrm.title == payload.title))
    # if existing.scalar_one_or_none() is not None:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="Task with this title already exists",
    #     )

    task = TasksOrm(
        title=payload.title,
        description=payload.description,
        deadline=payload.deadline,
        project_id=payload.project_id,
        column_id=payload.column_id
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, session: SessionDep) -> None:
    task = await session.get(TasksOrm, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    await session.delete(task)
    await session.commit()
    return None
