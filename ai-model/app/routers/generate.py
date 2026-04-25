import json
import re

from loguru import logger
from fastapi import APIRouter
from ..llm.model_loader import VikhrRAG
from ..schemas.request import ChartData, ModelRequest, ModelResponse

# Инициализация
router = APIRouter()
vikhr = VikhrRAG()

JSON_PATTERN = re.compile(r"\{.*\}", re.DOTALL)


def parse_chart_data(raw_answer: str) -> ChartData:
    """Extract and validate chart JSON from the model raw output."""
    match = JSON_PATTERN.search(raw_answer)
    if not match:
        raise ValueError("Модель не вернула JSON, вернула текст")

    json_str = match.group(0)
    data_dict = json.loads(json_str)
    return ChartData(**data_dict)


@router.post(
    "/generate",
    response_model=ModelResponse,
    summary="Генерация текста или графиков на основе данных проекта",
)
async def generate(request: ModelRequest):
    """
    Универсальный эндпоинт для вызова модели.
    :param user_query: Запрос пользователя
    :param documents: Список документов для RAG
    :param temperature: Температура генерации для финального ответа (0.1 - точно, 0.7 - творчески)
    :param top_k: Ограничение выборки токенов
    :param max_tokens: Макс длина ответа
    :return: JSON, сгенерированный моделью
    """
    logger.info(
        f"Request: query={request.user_query[:100]}..., docs={len(request.documents)} docs"
    )

    mode = "chart" if request.response_type == "chart" else "rag"
    temp = request.temperature
    if mode == "chart":
        temp = min(request.temperature, 0.3)  # Для графиков лучше поменьше температуру

    try:
        raw_answer = vikhr.ask_vikhr(
            user_query=request.user_query,
            documents=request.documents,
            temperature=temp,
            top_k=request.top_k,
            max_tokens=request.max_tokens,
            mode=mode,
        )

    except Exception as e:
        logger.exception("Model inference failed")
        return ModelResponse(error=f"Ошибка модели: {str(e)}")

    if request.response_type == "chart":
        try:
            validated_chart = parse_chart_data(raw_answer)

            logger.info("Chart data successfully validated")
            return ModelResponse(chart_data=validated_chart, raw_answer=raw_answer)

        except Exception as e:
            logger.error(f"Chart parsing error: {e}")
            return ModelResponse(
                error=f"Не удалось сформировать данные для графика: {str(e)}",
                raw_answer=raw_answer,
            )

    return ModelResponse(text_response=raw_answer, raw_answer=raw_answer)
