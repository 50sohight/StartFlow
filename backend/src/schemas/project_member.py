from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional

from .user import UserRead

# 1. Базовая схема с общими полями
class ProjectMemberBase(BaseModel):
    role: str = Field(..., max_length=30)
    project_id: UUID
    user_id: UUID

# 2. Схема для создания (то, что присылает клиент)
# Обычно совпадает с базовой, но здесь можно добавить специфичную валидацию
class ProjectMemberCreate(ProjectMemberBase):
    pass

# 3. Схема для обновления (все поля необязательны)
class ProjectMemberUpdate(BaseModel):
    role: Optional[str] = Field(None, max_length=30)
     
# 4. Схема для ответа (то, что возвращает API)
class ProjectMemberRead(ProjectMemberBase):
    user: UserRead

    # Это важно: позволяет Pydantic читать данные прямо из объектов SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

class ProjectMemberInDB(ProjectMemberRead):
    pass
