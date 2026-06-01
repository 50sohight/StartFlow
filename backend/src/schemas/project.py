from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

from .column import ColumnRead
from .task import TaskRead
# Импортируем правильную схему для участника
from .project_member import ProjectMemberRead 
from .users import User

class ProjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str
    status: Literal['активный', 'архивный'] = 'активный'


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: str | None = Field(None, min_length=1, max_length=20)


class ProjectRead(ProjectBase):
    """Ответ API"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    columns: List["ColumnRead"] = []
    tasks: List["TaskRead"] = []
    
    # ИСПРАВЛЕНИЕ: меняем List["User"] на List["ProjectMemberRead"]
    # Так как ProjectsOrm.members возвращает список участников проекта (с ролями), а не просто юзеров
    members: List["ProjectMemberRead"] = []

    model_config = ConfigDict(from_attributes=True)


class ProjectInDB(ProjectRead):
    pass

# Нужно добавить обновление forward references, если используешь старые версии Pydantic/Python, 
# но в современных версиях это работает автоматом.