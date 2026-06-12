from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChartPoint(BaseModel):
    date: date
    count: int


class TeamLoadPoint(BaseModel):
    user_id: UUID
    login: str
    fullname: str
    count: int


class LastColumnRead(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    position: int

    model_config = ConfigDict(from_attributes=True)