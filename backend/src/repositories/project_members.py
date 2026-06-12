import uuid

from sqlalchemy import select, case

from src.repositories.base import BaseRepository
from src.models.project_members import ProjectMembersOrm

class ProjectMembersRepositories(BaseRepository):
    model = ProjectMembersOrm

    async def check_admin(
            self,
            user_id: uuid.UUID,
            project_id: uuid.UUID
    ):
        stmt = (
            select(
                case(
                    (self.model.role == "admin", True),
                    else_ = False
                )
            )
            .where(
                self.model.project_id == project_id,
                self.model.user_id == user_id
            )
        )

        is_admin_raw = await self.session.execute(stmt)
        is_admin = is_admin_raw.scalar()

        return is_admin