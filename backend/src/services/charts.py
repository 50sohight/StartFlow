from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ColumnsOrm


async def get_last_column_for_project(
    session: AsyncSession,
    project_id: UUID,
) -> ColumnsOrm | None:
    stmt = (
        select(ColumnsOrm)
        .where(ColumnsOrm.project_id == project_id)
        .order_by(ColumnsOrm.position.desc(), ColumnsOrm.id.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()