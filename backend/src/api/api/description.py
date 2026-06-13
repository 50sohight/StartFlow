from uuid import UUID
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import httpx

from sqlalchemy.orm import selectinload  
from src.database import async_session_maker
from src.models import ProjectMembersOrm, ProjectsOrm
from src.schemas.project import ProjectForDescription
from src.schemas.description import ML_request
from src.api.dependencies import UserIdDep 
from src.database import async_session_maker
from src.config import settings

router = APIRouter(prefix="/description", tags=["Описание проекта"])


async def get_description(project:ProjectForDescription):
    payload = ML_request(
        documents=project,
        temperature=0.4,
        top_k=40,
        max_tokens=256
    )
    timeout = httpx.Timeout(600.0, read=600.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f'{settings.PUBLIC_AI_URL}/ai/generate/description',
            json=payload.model_dump(mode='json'))
        return response.json()




async def get_project_info(project_id: UUID, user_id: UserIdDep):
    async with async_session_maker() as session:

        project_member = await session.get(ProjectMembersOrm, {"project_id": project_id, "user_id": user_id})
        if project_member is None:
            raise HTTPException(status_code=400, detail="вы не являетесь участником проекта")
        
        project = await session.get(
            ProjectsOrm,
            project_id,
            options = [selectinload(ProjectsOrm.tasks)]
        )
        if project is None:
            raise HTTPException(
                status_code=404, detail="Project not found"
            )
        return project



@router.post("/{project_id}")
async def get_project_description(project_id: UUID, user_id: UserIdDep):
    project = await get_project_info(project_id=project_id, user_id=user_id)
    project_schema = ProjectForDescription.model_validate(project)
    description_data = await get_description(project=project_schema)
    return description_data
    
"""
есть в проетке
{
  "id": "47d8d8f0-f76c-4a94-b214-d5cabacdfb13",
  "project_id":"0248d178-548d-4bff-b66e-ea5949b5f72a"
  "login": "string3246234636",
  "fullname": "string346346326",
  "password": "S@tring23514561465"
}




нет в проекте
{
  "login": "string3246234636787878787",
  "fullname": "string346346326",
  "password": "S@tring23514561465"
}



{
  "name": "Startflow",
  "description": "StartFlow — цифровая платформа, которая помогает предприятиям быстро внедрять  проектное управление без сложных регламентов и долгого обучения сотрудников.",
  "status": "активный",
  "id": "09db8a32-4aed-4c7d-9614-b8a396c81f87",
  "created_at": "2026-06-02T12:21:16.950555Z",
  "updated_at": "2026-06-02T12:21:16.950555Z",
  "columns": [],
  "tasks": [],
  "members": [
    {
      "role": "admin",
      "project_id": "09db8a32-4aed-4c7d-9614-b8a396c81f87",
      "user_id": "47d8d8f0-f76c-4a94-b214-d5cabacdfb13",
      "user": {
        "id": "47d8d8f0-f76c-4a94-b214-d5cabacdfb13",
        "login": "string3246234636",
        "fullname": "string346346326"
      }
    }
  ]
}




column
{
  "project_id": "09db8a32-4aed-4c7d-9614-b8a396c81f87",
  "name": "task676767676767676767g",
  "position": 0,
  "id": "d2c2730d-30e9-472f-bfe0-18a1d05a4c5d"
}



tasks
{
  "title": "task6767676767676776767676767676",
  "description": "string",
  "deadline": "2026-06-04T11:34:17.800000Z",
  "project_id": "09db8a32-4aed-4c7d-9614-b8a396c81f87",
  "column_id": "d2c2730d-30e9-472f-bfe0-18a1d05a4c5d",
  "id": "f63ff2a9-ea56-4ab0-915a-258da4f08bb2",
  "created_at": "2026-06-04T11:39:30.817865Z",
  "updated_at": "2026-06-04T11:39:30.817865Z"
}
"""
