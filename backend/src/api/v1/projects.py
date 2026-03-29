from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import async_session_maker
from src.models.project_members import ProjectMembersOrm
from src.models.projects import ProjectsOrm
from src.schemas.project import ProjectCreate, ProjectRead
from src.schemas.project_member import ProjectMemberRead



router = APIRouter(prefix="/projects", tags=["projects"])


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[ProjectRead])
async def list_projects(session: SessionDep) -> list[ProjectRead]:
    result = await session.execute(select(ProjectsOrm).order_by(ProjectsOrm.updated_at))  # Сортируем по времени редактирования
    return list(result.scalars().all())


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: UUID, session: SessionDep) -> ProjectRead:
    project = await session.get(ProjectsOrm, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project    


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, session: SessionDep) -> ProjectRead:
    # Простая проверка уникальности проекта.
    existing = await session.execute(select(ProjectsOrm).where(ProjectsOrm.name == payload.name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with this name already exists",
        )

    project = ProjectsOrm(
        name=payload.name,
        description=payload.description,
        status=payload.status
    )

    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, session: SessionDep) -> None:
    project = await session.get(ProjectsOrm, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    await session.delete(project)
    await session.commit()
    return None


@router.get("/{project_id}/members", response_model=list[ProjectMemberRead])
async def list_project_members(project_id: UUID, session: SessionDep) -> list[ProjectMemberRead]:
    project = await session.get(ProjectsOrm, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    result = await session.execute(
        select(ProjectMembersOrm)
        .where(ProjectMembersOrm.project_id == project_id)
        .options(selectinload(ProjectMembersOrm.user))
        .order_by(ProjectMembersOrm.user_id)
    )
    return list(result.scalars().all())
