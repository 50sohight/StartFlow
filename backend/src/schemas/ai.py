from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .description import ML_request


class ChartRequest(ML_request):
    """Расширенный запрос для генерации графика."""

    response_type: Literal["chart"] = "chart"


class ChartData(BaseModel):
    """Схема данных графика от AI."""

    labels: List[str] = Field(..., description="Названия категорий (оси X или легенда)")
    values: List[float] = Field(..., description="Числовые значения (ось Y)")
    title: str = Field(default="Аналитика проекта", description="Заголовок графика")
    chart_type: str = Field(default="bar", description="Тип: bar, line, pie")


class ChartResponse(BaseModel):
    """Ответ от AI с графиком."""

    chart_data: Optional[ChartData] = None
    text_response: Optional[str] = None
    raw_answer: Optional[str] = None
