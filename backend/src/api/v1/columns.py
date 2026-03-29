from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker
from src.models.columns import ColumnsOrm
from src.schemas.column import ColumnCreate, ColumnRead



router = APIRouter(prefix="/columns", tags=["columns"])


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[ColumnRead])
async def list_columns(session: SessionDep) -> list[ColumnRead]:
    result = await session.execute(select(ColumnsOrm))
    return list(result.scalars().all())


@router.get("/{column_id}", response_model=ColumnRead)
async def get_column(column_id: UUID, session: SessionDep) -> ColumnRead:
    column = await session.get(ColumnsOrm, column_id)
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
    return column


@router.post("", response_model=ColumnRead, status_code=status.HTTP_201_CREATED)
async def create_column(payload: ColumnCreate, session: SessionDep) -> ColumnRead:
    # Простая проверка уникальности колонки.
    existing = await session.execute(select(ColumnsOrm).where(ColumnsOrm.name == payload.name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Column with this name already exists",
        )

    column = ColumnsOrm(
        project_id=payload.project_id,
        name=payload.name,
        position=payload.position
    )

    session.add(column)
    await session.commit()
    await session.refresh(column)
    return column


@router.delete("/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(column_id: UUID, session: SessionDep) -> None:
    column = await session.get(ColumnsOrm, column_id)
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")

    await session.delete(column)
    await session.commit()
    return None
