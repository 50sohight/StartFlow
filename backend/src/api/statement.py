from typing import Annotated

import uuid

from fastapi import APIRouter
from fastapi.responses import Response

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import UserIdDep
from src.utils import admin_checker
from src.services.statement import StatementService
from src.api.dependencies import SessionDep

router = APIRouter(prefix="/statement", tags=["Отчет"])

@router.post("/{project_id}")
@admin_checker
async def send_statement_data(
        user_id: UserIdDep,
        session: SessionDep,
        project_id: uuid.UUID
):
    statement = await StatementService(session).create_statement(project_id, user_id)
    filename = await StatementService(session).get_file_name(project_id)

    return Response(
        content=statement,
        media_type="application/pdf",
        headers={f"Content-Disposition": f"attachment; filename={filename}.pdf"}
    )
