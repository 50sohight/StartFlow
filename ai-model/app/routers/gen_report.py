from loguru import logger
from fastapi import APIRouter, HTTPException, status

from ..llm.model_loader import VikhrRAG
from ..schemas.request import DescriptionRequest, ModelResponse
from ..prompts import report_prompt

# Инициализация
router = APIRouter()
vikhr = VikhrRAG()

@router.post("/generate/report",
             response_model=ModelResponse,
             summary="Генерация отчета за период для раздела с отчетами")
async def gen_report(request: DescriptionRequest):
    """
    Эндпоинт для генерации отчета по проекту за период.

    Принимает данные проекта в documents и параметры генерации.
    Готовый промпт для генерации отчета задается внутри ручки.
    Возвращает сгенерированный текст в поле text_response.
    """

    if not request.documents or not any(doc.strip() for doc in request.documents):
        return ModelResponse(
            text_response="Недостаточно данных для формирования отчета по проекту.",
            raw_answer=None,
        )

    try:
        report = vikhr.ask_vikhr(
            user_query=report_prompt(),
            documents=request.documents,
            temperature=request.temperature,
            top_k=request.top_k,
            max_tokens=request.max_tokens,
            mode="rag"
        )
    except Exception as e:
        logger.exception("Report generation failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель недоступна или не смогла сгенерировать ответ",
        ) from e


    return ModelResponse(
        text_response=report,
        raw_answer=report,
    )