import json
import re

from loguru import logger
from fastapi import APIRouter, HTTPException, status

from ..llm.model_loader import VikhrRAG
from ..schemas.request import ModelRequest, ModelResponse, ChartData

# Инициализация
router = APIRouter()
vikhr = VikhrRAG()

JSON_PATTERN = re.compile(r'\{.*\}', re.DOTALL)

@router.post("/generate",
             response_model=ModelResponse,
             summary="Генерация текста или графиков на основе данных проекта")
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
    logger.info(f"Request: query={request.user_query[:100]}..., docs={len(request.documents)} docs")

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
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель недоступна или не смогла сгенерировать ответ",
        ) from e

    if not raw_answer or not raw_answer.strip():
        logger.error("Model returned empty answer")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Модель вернула пустой ответ",
        )

    if request.response_type == "chart":
        try:
            match = JSON_PATTERN.search(raw_answer)
            if not match:
                raise ValueError("Модель не вернула JSON, вернула текст")

            json_str = match.group(0)
            data_dict = json.loads(json_str)

            validated_chart = ChartData(**data_dict)

            logger.info("Chart data successfully validated")
            return ModelResponse(chart_data=validated_chart, raw_answer=raw_answer)


        except Exception as e:
            logger.debug(f"Raw model answer: {raw_answer}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Не удалось преобразовать ответ модели в данные графика",
            ) from e

    return ModelResponse(text_response=raw_answer, raw_answer=raw_answer)

