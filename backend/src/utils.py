import uuid
from functools import wraps

from fpdf import FPDF
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.services.project_members import ProjectMembersService

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("dejavu_sans", "", fname=f"{settings.FONT_FOLDER}DejaVuSans.ttf", uni=True)
        self.add_font("dejavu_sans", "B", fname=f"{settings.FONT_FOLDER}DejaVuSans-Bold.ttf", uni=True)


def admin_checker(func):
    @wraps(func)
    async def wrapper(
            user_id: uuid.UUID,
            session: AsyncSession,
            project_id: uuid.UUID,
            *args,
            **kwargs
    ):
        if await ProjectMembersService(session).check_admin(user_id, project_id):
            return await func(user_id, session, project_id, *args, **kwargs)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуются права администратора"
            )
    return wrapper

