from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload  
from src.database import async_session_maker
from src.models import ColumnsOrm, ProjectMembersOrm, ProjectsOrm
from src.schemas.project import ProjectCreate, ProjectRead
from src.schemas.project_member import ProjectMemberRead
from src.api.dependencies import UserIdDep 
router = APIRouter(prefix="/projects", tags=["projects"])


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=List[ProjectRead])
async def list_projects(session: SessionDep) -> List[ProjectRead]:
    result = await session.execute(
        select(ProjectsOrm)
        .options(
            selectinload(ProjectsOrm.members).selectinload(ProjectMembersOrm.user),
            selectinload(ProjectsOrm.columns).selectinload(ColumnsOrm.tasks),
            selectinload(ProjectsOrm.tasks),
        )
        .order_by(ProjectsOrm.updated_at)
    )
    return list(result.scalars().all())


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: UUID, session: SessionDep) -> ProjectRead:
    project = await session.get(
        ProjectsOrm,
        project_id,
        options=[
            selectinload(ProjectsOrm.members).selectinload(ProjectMembersOrm.user),
            selectinload(ProjectsOrm.columns).selectinload(ColumnsOrm.tasks),
            selectinload(ProjectsOrm.tasks),
        ],
    )
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, session: SessionDep, created_by:  UserIdDep) -> ProjectRead:
    existing = await session.execute(
        select(ProjectsOrm).where(ProjectsOrm.name == payload.name)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail="Project with this name already exists",
        )

    project = ProjectsOrm(
        name=payload.name, description=payload.description, status=payload.status
    )
    session.add(project)

    await session.flush()
    member = ProjectMembersOrm(
        project_id=project.id,
        user_id=created_by,
        role="creator"
    )
    session.add(member)
    await session.commit()
    await session.refresh(project)

    result = await session.execute(
        select(ProjectsOrm)
        .where(ProjectsOrm.id == project.id)
        .options(
            selectinload(ProjectsOrm.members).selectinload(ProjectMembersOrm.user),
            selectinload(ProjectsOrm.columns).selectinload(ColumnsOrm.tasks),
            selectinload(ProjectsOrm.tasks),
        )
    )
    return result.scalar_one()


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, session: SessionDep) -> None:
    project = await session.get(ProjectsOrm, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    await session.delete(project)
    await session.commit()
    return None


@router.get("/{project_id}/members", response_model=List[ProjectMemberRead])
async def list_project_members(
    project_id: UUID, session: SessionDep
) -> List[ProjectMemberRead]:
    result = await session.execute(
        select(ProjectMembersOrm)
        .where(ProjectMembersOrm.project_id == project_id)
        .options(selectinload(ProjectMembersOrm.user))
        .order_by(ProjectMembersOrm.user_id)
    )
    return list(result.scalars().all())
