from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import async_session_maker
from src.models.project_members import ProjectMembersOrm
from src.schemas.project_member import ProjectMemberRead, ProjectMemberUpdate



router = APIRouter(prefix="/project_members", tags=["project_members"])


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[ProjectMemberRead])
async def list_project_members(session: SessionDep) -> list[ProjectMemberRead]:
    result = await session.execute(select(ProjectMembersOrm).options(selectinload(ProjectMembersOrm.user)))
    return list(result.scalars().all())


@router.get("/{project_id}/{user_id}", response_model=ProjectMemberRead)
async def get_project_member(project_id: UUID, user_id: UUID, session: SessionDep) -> ProjectMemberRead:
    project_member = await session.get(ProjectMembersOrm, {"project_id": project_id, "user_id": user_id})
    if project_member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project member not found")
    return project_member


@router.patch("/{project_id}/{user_id}", response_model=ProjectMemberRead)
async def update_project_member_role(
    project_id: UUID,
    user_id: UUID,
    payload: ProjectMemberUpdate,
    session: SessionDep,
) -> ProjectMemberRead:
    project_member = await session.get(ProjectMembersOrm, {"project_id": project_id, "user_id": user_id})
    if project_member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project member not found")

    if payload.role is not None:
        project_member.role = payload.role

    await session.commit()
    await session.refresh(project_member)
    return project_member
