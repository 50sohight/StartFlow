from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from .task import TaskRead


class ColumnBase(BaseModel):
    project_id: UUID 
    name: str = Field(..., max_length=50)
    position: int


class ColumnCreate(ColumnBase):
    pass


class ColumnUpdate(BaseModel):
    position: Optional[int] = Field(None, ge=0)
    name: str | None = Field(None, min_length=1, max_length=50)


class ColumnRead(ColumnBase):
    """Ответ API: без секретов."""
    tasks: list[TaskRead] = []

    model_config = ConfigDict(from_attributes=True)

    id: UUID


class ColumnInDB(ColumnRead):
    """Соответствует полям ColumnsOrm (в т.ч. для чтения из сессии)."""

    pass
