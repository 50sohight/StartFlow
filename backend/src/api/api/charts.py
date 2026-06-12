from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.api.projects import get_session
from src.models import (
    ColumnsOrm,
    ProjectMembersOrm,
    ProjectsOrm,
    TaskAssigneesOrm,
    TasksOrm,
    UsersOrm,
)
from src.schemas.charts import ChartPoint, LastColumnRead, TeamLoadPoint
from src.services.charts import get_last_column_for_project


router = APIRouter(prefix="/charts", tags=["charts"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _date_range(start_date, end_date):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


async def _get_project_or_404(session: AsyncSession, project_id: UUID) -> ProjectsOrm:
    project = await session.get(ProjectsOrm, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


async def _get_last_column_or_404(session: AsyncSession, project_id: UUID) -> ColumnsOrm:
    last_column = await get_last_column_for_project(session, project_id)
    if last_column is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project has no columns",
        )
    return last_column


@router.get("/{project_id}/get_last_column", response_model=LastColumnRead)
async def get_last_column(project_id: UUID, session: SessionDep) -> LastColumnRead:
    await _get_project_or_404(session, project_id)
    return await _get_last_column_or_404(session, project_id)


@router.get("/burndown/{project_id}/ideal", response_model=list[ChartPoint])
async def burndown_ideal(project_id: UUID, session: SessionDep) -> list[ChartPoint]:
    await _get_project_or_404(session, project_id)

    stmt = select(TasksOrm.deadline).where(TasksOrm.project_id == project_id)
    deadlines = list((await session.execute(stmt)).scalars().all())
    if not deadlines:
        return []

    deadlines_by_day = Counter(deadline.date() for deadline in deadlines)
    start_date = min(deadlines_by_day)
    end_date = max(deadlines_by_day)

    result: list[ChartPoint] = []
    running_total = 0
    for day in _date_range(start_date, end_date):
        running_total += deadlines_by_day.get(day, 0)
        result.append(ChartPoint(date=day, count=running_total))

    return result


@router.get("/burndown/{project_id}/actual", response_model=list[ChartPoint])
async def burndown_actual(project_id: UUID, session: SessionDep) -> list[ChartPoint]:
    await _get_project_or_404(session, project_id)
    last_column = await _get_last_column_or_404(session, project_id)

    deadline_stmt = select(TasksOrm.deadline).where(TasksOrm.project_id == project_id)
    deadlines = list((await session.execute(deadline_stmt)).scalars().all())
    if not deadlines:
        return []

    stmt = select(TasksOrm.done_at).where(
        TasksOrm.project_id == project_id,
        TasksOrm.column_id == last_column.id,
        TasksOrm.done_at.is_not(None),
    )
    done_dates = list((await session.execute(stmt)).scalars().all())
    done_by_day = Counter(done_at.date() for done_at in done_dates)

    start_date = min(deadline.date() for deadline in deadlines)
    end_date = max(deadline.date() for deadline in deadlines)

    result: list[ChartPoint] = []
    today = datetime.now(timezone.utc).date()
    for day in _date_range(start_date, end_date):
        if day > today:
            result.append(ChartPoint(date=day, count=0))
            continue
        result.append(ChartPoint(date=day, count=done_by_day.get(day, 0)))

    return result


@router.get("/teamload/{project_id}/done", response_model=list[TeamLoadPoint])
async def teamload_done(project_id: UUID, session: SessionDep) -> list[TeamLoadPoint]:
    await _get_project_or_404(session, project_id)
    last_column = await _get_last_column_or_404(session, project_id)

    count_expr = func.coalesce(
        func.sum(
            case(
                (TasksOrm.column_id == last_column.id, 1),
                else_=0,
            )
        ),
        0,
    )

    stmt = (
        select(
            UsersOrm.id,
            UsersOrm.login,
            UsersOrm.fullname,
            count_expr.label("count"),
        )
        .select_from(ProjectMembersOrm)
        .join(UsersOrm, UsersOrm.id == ProjectMembersOrm.user_id)
        .outerjoin(TaskAssigneesOrm, TaskAssigneesOrm.user_id == UsersOrm.id)
        .outerjoin(
            TasksOrm,
            and_(
                TasksOrm.id == TaskAssigneesOrm.task_id,
                TasksOrm.project_id == project_id,
            ),
        )
        .where(ProjectMembersOrm.project_id == project_id)
        .group_by(UsersOrm.id, UsersOrm.login, UsersOrm.fullname)
        .order_by(UsersOrm.login)
    )

    result = await session.execute(stmt)
    return [
        TeamLoadPoint(
            user_id=row.id,
            login=row.login,
            fullname=row.fullname,
            count=row.count,
        )
        for row in result.all()
    ]


@router.get("/teamload/{project_id}/assigned", response_model=list[TeamLoadPoint])
async def teamload_assigned(project_id: UUID, session: SessionDep) -> list[TeamLoadPoint]:
    await _get_project_or_404(session, project_id)
    last_column = await _get_last_column_or_404(session, project_id)

    count_expr = func.coalesce(
        func.sum(
            case(
                (
                    and_(
                        TasksOrm.id.is_not(None),
                        TasksOrm.column_id != last_column.id,
                    ),
                    1,
                ),
                else_=0,
            )
        ),
        0,
    )

    stmt = (
        select(
            UsersOrm.id,
            UsersOrm.login,
            UsersOrm.fullname,
            count_expr.label("count"),
        )
        .select_from(ProjectMembersOrm)
        .join(UsersOrm, UsersOrm.id == ProjectMembersOrm.user_id)
        .outerjoin(TaskAssigneesOrm, TaskAssigneesOrm.user_id == UsersOrm.id)
        .outerjoin(
            TasksOrm,
            and_(
                TasksOrm.id == TaskAssigneesOrm.task_id,
                TasksOrm.project_id == project_id,
            ),
        )
        .where(ProjectMembersOrm.project_id == project_id)
        .group_by(UsersOrm.id, UsersOrm.login, UsersOrm.fullname)
        .order_by(UsersOrm.login)
    )

    result = await session.execute(stmt)
    return [
        TeamLoadPoint(
            user_id=row.id,
            login=row.login,
            fullname=row.fullname,
            count=row.count,
        )
        for row in result.all()
    ]