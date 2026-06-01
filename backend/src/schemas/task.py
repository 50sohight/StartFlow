from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

# 1. Базовая схема с общими полями
class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    deadline: datetime
    project_id: UUID
    column_id: UUID

# 2. Схема для создания (то, что присылает клиент)
# Обычно совпадает с базовой, но здесь можно добавить специфичную валидацию
class TaskCreate(TaskBase):
    pass

# 3. Схема для обновления (все поля необязательны)
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    column_id: Optional[UUID] = None

# 4. Схема для ответа (то, что возвращает API)
class TaskRead(TaskBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    # Это важно: позволяет Pydantic читать данные прямо из объектов SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
