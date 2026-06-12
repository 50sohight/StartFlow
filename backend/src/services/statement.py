import uuid
import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.api.api.description import get_project_info
from src.schemas.project import ProjectForDescription
from src.repositories.project import ProjectRepository
from src.schemas.description import ML_request
from src.utils import PDF

class StatementService:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session

    async def create_statement(
            self,
            project_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> PDF:
        # Собрать данные нужные для отчета
        project = await get_project_info(project_id, user_id)
        print(project)

        project_schema = ProjectForDescription.model_validate(project)

        print(project_schema)

        # Получить данные
        description = await self._get_description(project_schema)

        print(description)

        # Преобразовать в файл
        pdf = self._create_file(description)
        # Вернуть файл
        return pdf

    async def get_file_name(
            self,
            project_id: uuid.UUID,
    ) -> str:
        name = await ProjectRepository(self.session).get_project_name(project_id)

        return name

    async def _get_description(self, project: ProjectForDescription):
        payload = ML_request(
            documents=project,
            temperature=0.4,
            top_k=40,
            max_tokens=2048
        )
        timeout = httpx.Timeout(600.0, read=600.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f'{settings.PUBLIC_AI_URL}/ai/generate/report',
                json=payload.model_dump(mode='json'))
            return response.json()["text_response"]

    def _create_file(self, text):
        pdf = PDF()

        pdf.add_page()

        pdf.set_font("dejavu_sans", style="B", size=24)
        pdf.cell(0, 10, 'Отчет по проекту', 0, 1, 'C')
        pdf.ln(8)

        pdf.set_font("dejavu_sans", style="", size=16)

        pdf.multi_cell(0, 10, text, markdown=True)

        pdf_bytes = bytes(pdf.output(dest="S"))

        return pdf_bytes
