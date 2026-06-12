from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.api.projects import get_session
from src.models import ProjectMembersOrm, TaskAssigneesOrm, TasksOrm, UsersOrm
from src.schemas.task_assign import TaskAssigneeRead

router = APIRouter(tags=["task_assignments"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def _check_task_and_membership(
    session: AsyncSession, task_id: UUID, user_id: UUID
) -> TasksOrm:
    """Проверяет существование задачи и то, что пользователь является участником проекта."""
    task = await session.get(TasksOrm, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    membership = await session.execute(
        select(ProjectMembersOrm).where(
            and_(
                ProjectMembersOrm.project_id == task.project_id,
                ProjectMembersOrm.user_id == user_id,
            )
        )
    )
    if not membership.scalar_one_or_none():
        raise HTTPException(
            status_code=403, detail="User is not a member of the project"
        )
    return task


@router.post("/tasks/{task_id}/assign", status_code=status.HTTP_201_CREATED)
async def assign_user(task_id: UUID, user_id: UUID, session: SessionDep):
    """Назначить пользователя исполнителем задачи."""
    task = await _check_task_and_membership(session, task_id, user_id)

    # Проверяем, что ещё не назначен
    existing = await session.execute(
        select(TaskAssigneesOrm).where(
            and_(
                TaskAssigneesOrm.task_id == task_id,
                TaskAssigneesOrm.user_id == user_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="User already assigned to this task"
        )

    new_assignment = TaskAssigneesOrm(task_id=task_id, user_id=user_id)
    session.add(new_assignment)
    await session.commit()
    return {"message": "User assigned successfully"}


@router.delete("/tasks/{task_id}/unassign", status_code=status.HTTP_200_OK)
async def unassign_user(task_id: UUID, user_id: UUID, session: SessionDep):
    """Снять пользователя с задачи."""
    await _check_task_and_membership(session, task_id, user_id)

    assignment = await session.execute(
        select(TaskAssigneesOrm).where(
            and_(
                TaskAssigneesOrm.task_id == task_id,
                TaskAssigneesOrm.user_id == user_id,
            )
        )
    )
    assignment = assignment.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    await session.delete(assignment)
    await session.commit()
    return {"message": "User unassigned successfully"}


@router.get("/projects/{project_id}/assignments", response_model=list[TaskAssigneeRead])
async def get_project_assignments(project_id: UUID, session: SessionDep):
    """Все назначения по задачам проекта (с информацией о пользователях)."""
    result = await session.execute(
        select(TaskAssigneesOrm.task_id, UsersOrm.id, UsersOrm.login, UsersOrm.fullname)
        .join(UsersOrm, UsersOrm.id == TaskAssigneesOrm.user_id)
        .join(TasksOrm, TasksOrm.id == TaskAssigneesOrm.task_id)
        .where(TasksOrm.project_id == project_id)
        .order_by(UsersOrm.fullname)
    )
    assignments = result.all()
    return [
        TaskAssigneeRead(
            task_id=a.task_id,
            user_id=a.id,
            login=a.login,
            fullname=a.fullname,
        )
        for a in assignments
    ]
