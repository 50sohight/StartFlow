from sqlalchemy import select

from src.repositories.base import BaseRepository
from src.models.projects import ProjectsOrm

class ProjectRepository(BaseRepository):
    model = ProjectsOrm

    async def get_project_name(self, project_id) -> str:
        stmt = (
            select(self.model.name)
            .where(self.model.id == project_id)
        )

        name_raw = await self.session.execute(stmt)
        name = name_raw.scalar()

        return name
