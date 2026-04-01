"""Pydantic схемы для запросов"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Literal

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
    max_tokens: int = 2048
    # Либо работаем с текстом - text, либо с графиком - chart
    response_type: Literal["text", "chart"] = "text"

class ModelResponse(BaseModel):
    text_response: Optional[str] = None
    chart_data: Optional[ChartData] = None
    raw_answer: Optional[str] = None


