# src/api/chart.py
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from src.api.dependencies import UserIdDep
from src.database import async_session_maker
from src.models import ProjectMembersOrm, ProjectsOrm
from src.schemas.ai import ChartRequest, ChartResponse
from src.schemas.project import ProjectForDescription

router = APIRouter(prefix="/chart", tags=["Графики проекта"])


async def get_project_info(project_id: UUID, user_id: UUID):
    async with async_session_maker() as session:
        member = await session.get(
            ProjectMembersOrm, {"project_id": project_id, "user_id": user_id}
        )
        if member is None:
            raise HTTPException(
                status_code=400, detail="Вы не являетесь участником проекта"
            )

        project = await session.get(
            ProjectsOrm, project_id, options=[selectinload(ProjectsOrm.tasks)]
        )
        if project is None:
            raise HTTPException(status_code=404, detail="Проект не найден")
        return project


async def get_chart_data(project: ProjectForDescription):
    prompt = (
        "Построй график распределения задач по статусам (колонкам). "
        "Данные проекта представлены в documents. "
        "Используй тип графика bar."
    )

    payload = ChartRequest(
        user_query=prompt, documents=project, temperature=0.2, top_k=40, max_tokens=1024
    )

    timeout = httpx.Timeout(600.0, read=600.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            "http://204.12.253.210:8077/ai/generate",
            json=payload.model_dump(mode="json"),
        )
        response.raise_for_status()
        data = response.json()
        return ChartResponse(**data)


@router.post("/{project_id}", response_model=ChartResponse)
async def generate_chart(project_id: UUID, user_id: UserIdDep):
    project = await get_project_info(project_id, user_id)
    project_schema = ProjectForDescription.model_validate(project)
    chart_response = await get_chart_data(project_schema)
    return chart_response
