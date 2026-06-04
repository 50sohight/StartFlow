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
    
    columns: list["ColumnRead"] | None = None
    tasks: List["TaskRead"] = []
    members: list["ProjectMemberRead"] | None = None
    
    model_config = ConfigDict(from_attributes=True)


class ProjectInDB(ProjectRead):
    pass

class ProjectForDescription(BaseModel):
    """Схема только для генерации описания — без columns и members"""
    #Влад, эта схема и должна быть вместо List[str]
    name: str
    description: str | None = None
    status: Literal['активный', 'архивный']
    created_at: datetime
    updated_at: datetime
    tasks: List["TaskRead"] = []   

    model_config = ConfigDict(from_attributes=True)