from fastapi import APIRouter, HTTPException, Cookie, status, Depends
from src.database import async_session_maker
from src.models import LinksOrm, ProjectMembersOrm
from uuid import UUID
from src.config import settings
from src.services.auth import TokenService
from sqlalchemy import select

import datetime

import secrets

router = APIRouter(prefix="/link", tags=["Ссылки-приглашения"])

async def get_current_user_uuid(access_token: str | None = Cookie(default=None)):

    token_service = TokenService()

    payload = token_service.decode_token(access_token)
    return UUID(payload["user_id"])
        

@router.post("/generate_link/{project_uuid}")
async def genetate_link(project_uuid: UUID, created_by: UUID = Depends(get_current_user_uuid)):
    '''
    генерируем ссылку, записываем в links, пока used_by=null ссылка будет считаться неиспользованой
    '''
    link = secrets.token_urlsafe(24)
    async with async_session_maker() as session:
        new_link = LinksOrm(
            link=link, 
            created_by=created_by, 
            expires_at=datetime.datetime.now() + datetime.timedelta(hours=2),
            project_id=project_uuid
            )
        session.add(new_link)
        await session.commit()
    return link

@router.post("/use_link/{user_link}")
async def use_link(user_link: str, used_by: UUID = Depends(get_current_user_uuid)):
    '''
    получаем ссылку, ищем ее в links, смотрим была/не была использована, истекла по времени или нет,
    есть она или нет, првоеряем есть участник в проекте до действия ссылки(учатсник уже в проекте)
    если все ок меняем used_by и used_at, также записываем в project_members нового чела
    '''
    async with async_session_maker() as session:

        stmt_for_link = select(LinksOrm).where(LinksOrm.link == user_link)
        result_for_link = await session.execute(stmt_for_link)

        link_obj = result_for_link.scalar_one_or_none()

        if link_obj is None:
            raise HTTPException(status_code=404, detail="Ссылка не найдена")
        
        if link_obj.expires_at < datetime.datetime.now(datetime.timezone.utc):
            raise HTTPException(status_code=400, detail="Ссылка просрочена")

        if link_obj.used_by is not None:
            raise HTTPException(status_code=400, detail="Ссылка уже была использована")

        stmt_for_project = select(ProjectMembersOrm).where(
            ProjectMembersOrm.user_id == used_by,
            ProjectMembersOrm.project_id == link_obj.project_id
        )

        result_for_project = await session.execute(stmt_for_project)

        proj_mem_obj = result_for_project.scalar_one_or_none()
        
        if proj_mem_obj is not None:
            raise HTTPException(status_code=400, detail="Участник уже в проекте")

        link_obj.used_by = used_by
        link_obj.used_at = datetime.datetime.now(datetime.timezone.utc)

        new_project_member = ProjectMembersOrm(
            project_id=link_obj.project_id,
            user_id=used_by,
            role="Common"
        )
        session.add(new_project_member)
        await session.commit()
    return {"success": True}
    