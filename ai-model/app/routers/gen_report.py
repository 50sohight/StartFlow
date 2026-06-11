from loguru import logger
from fastapi import APIRouter, HTTPException, status

from ..llm.model_loader import VikhrRAG
from ..schemas.request import ReportRequest, ModelResponse
from ..prompts import report_prompt

# Инициализация
router = APIRouter()
vikhr = VikhrRAG()

@router.post("/generate/report",
             response_model=ModelResponse,
             summary="Генерация отчета за период для раздела с отчетами")
async def gen_report(request: ReportRequest):
    """
    Эндпоинт для генерации отчета по проекту за период.

    Принимает данные проекта в documents и параметры генерации.
    Готовый промпт для генерации отчета задается внутри ручки.
    Возвращает сгенерированный текст в поле text_response.
    """

    project_data = request.documents

    has_description = bool(
        project_data.description and project_data.description.strip()
    )

    has_tasks = bool(project_data.tasks)

    if not has_description and not has_tasks:
        return ModelResponse(
            text_response="Недостаточно данных для формирования описания проекта.",
            raw_answer=None,
        )

    documents_payload = project_data.model_dump(mode="json")

    try:
        report = vikhr.ask_vikhr(
            user_query=report_prompt(),
            documents=documents_payload,
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
    )