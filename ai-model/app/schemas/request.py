"""Pydantic схемы для запросов"""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from uuid import UUID

class ChartData(BaseModel):
    """Схема данных для построения графика на фронтенде"""
    labels: List[str] = Field(..., description="Названия категорий (оси X или легенда)")
    values: List[float] = Field(..., description="Числовые значения (ось Y)")
    title: str = Field(default="Аналитика проекта", description="Заголовок графика")
    chart_type: str = Field(default="bar", description="Тип: bar, line, pie")

class ModelRequest(BaseModel):
    user_query: str = Field(..., description="Текстовый запрос")
    documents: List[str] = []
    temperature: float = 0.3
    top_k: int = 40
    max_tokens: int = 512
    # Либо работаем с текстом - text, либо с графиком - chart
    response_type: Literal["text", "chart"] = "text"

class ModelResponse(BaseModel):
    text_response: Optional[str] = None
    chart_data: Optional[ChartData] = None
    raw_answer: Optional[str] = None

class InfoForGenerate(BaseModel):
    """Схема для сбора информации проекта без columns и members для генерации"""
    name: str
    description: str | None = None
    status: Literal['активный', 'архивный']
    created_at: datetime
    updated_at: datetime
    tasks: List["TaskRead"] = []

    model_config = ConfigDict(from_attributes=True)

# Схемы задач для схемы сбора информации для генерации
class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    deadline: datetime
    project_id: UUID
    column_id: UUID

class TaskRead(TaskBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    # Это важно: позволяет Pydantic читать данные прямо из объектов SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

class DescriptionRequest(BaseModel):
    """Схема для генерации описания"""
    documents: InfoForGenerate
    temperature: float = 0.4
    top_k: int = 40
    max_tokens: int = 512

class ReportRequest(BaseModel):
    """Схема для генерации отчетов"""
    documents: InfoForGenerate
    temperature: float = 0.3
    top_k: int = 40
    max_tokens: int = 512








