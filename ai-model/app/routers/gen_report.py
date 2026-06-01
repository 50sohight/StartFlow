from loguru import logger
from fastapi import APIRouter, HTTPException, status

from ..llm.model_loader import VikhrRAG
from ..schemas.request import DescriptionRequest, ModelResponse
from ..prompts import report_prompt
from gen_description import is_invalid_response

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
            text_response="Недостаточно данных для формирования описания проекта.",
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
        logger.exception("Description generation failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель недоступна или не смогла сгенерировать ответ",
        ) from e

    if is_invalid_response(report):
        logger.warning(f"Model returned invalid report: {report[:300]}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Модель не смогла сформировать отчет проекта по переданным данным",
        )

    return ModelResponse(
        text_response=report,
        raw_answer=report,
    )