from uuid import UUID

from pydantic import BaseModel


class TaskAssigneeRead(BaseModel):
    task_id: UUID
    user_id: UUID
    login: str
    fullname: str

    model_config = {"from_attributes": True}
