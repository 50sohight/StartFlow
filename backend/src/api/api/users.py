import hashlib
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.dependencies import UserIdDep 
from src.database import async_session_maker
from src.models import UsersOrm
from src.schemas.users import UserRequestAdd, User
from src.models import ProjectsOrm, ProjectMembersOrm 
from src.schemas.project import ProjectRead

from typing import List

router = APIRouter(prefix="/users", tags=["users"])


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _hash_password(raw_password: str) -> str:
    # Для примера (без внешних зависимостей). В проде лучше passlib/bcrypt/argon2.
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


@router.get("", response_model=list[User])
async def list_users(session: SessionDep) -> list[User]:
    result = await session.execute(select(UsersOrm).order_by(UsersOrm.login))
    return list(result.scalars().all())




@router.get("/my_projects", response_model=List[ProjectRead])
async def get_user_projects(
    user_id: UserIdDep,
    session: SessionDep
) -> List[ProjectRead]:
    projects = await session.execute(
        select(ProjectsOrm)
        .options(
            selectinload(ProjectsOrm.columns),
            selectinload(ProjectsOrm.tasks),
            selectinload(ProjectsOrm.members).selectinload(ProjectMembersOrm.user)
        )
        .join(ProjectMembersOrm, ProjectsOrm.id == ProjectMembersOrm.project_id)
        .where(ProjectMembersOrm.user_id == user_id)
    )
    return projects.unique().scalars().all()

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: UUID, session: SessionDep) -> User:
    user = await session.get(UsersOrm, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserRequestAdd, session: SessionDep) -> User:
    # Простая проверка уникальности логина.
    existing = await session.execute(select(UsersOrm).where(UsersOrm.login == payload.login))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login already exists",
        )

    user = UsersOrm(
        login=payload.login,
        fullname=payload.fullname,
        password_hash=_hash_password(payload.password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, session: SessionDep) -> None:
    user = await session.get(UsersOrm, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await session.delete(user)
    await session.commit()
    return None
