from loguru import logger
from fastapi import APIRouter, HTTPException, status

from ..llm.model_loader import VikhrRAG
from ..schemas.request import DescriptionRequest, ModelResponse
from ..prompts import description_prompt

# Инициализация
router = APIRouter()
vikhr = VikhrRAG()


@router.post("/generate/description",
             response_model=ModelResponse,
             summary="Генерация текста для раздела с описанием с готовым промптом")
async def gen_description(request: DescriptionRequest):
    """
    Эндпоинт для генерации описания проекта.

    Принимает данные проекта в documents и параметры генерации.
    Готовый промпт для генерации описания задается внутри ручки.
    Возвращает сгенерированный текст в поле text_response.
    """

    if not request.documents or not any(doc.strip() for doc in request.documents):
        return ModelResponse(
            text_response="Недостаточно данных для формирования описания проекта.",
            raw_answer=None,
        )

    try:
        description = vikhr.ask_vikhr(
            user_query=description_prompt(),
            documents=request.documents,
            temperature=request.temperature,
            top_k=request.top_k,
            max_tokens=request.max_tokens,
            mode="rag"
        )
    except Exception as e:
        logger.exception("Description generation failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель недоступна или не смогла сгенерировать ответ",
        ) from e

    return ModelResponse(
        text_response=description,
        raw_answer=description,
    )