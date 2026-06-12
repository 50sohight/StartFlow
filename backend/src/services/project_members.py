import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.project_members import ProjectMembersRepositories



class ProjectMembersService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_admin(
            self,
            user_id: uuid.UUID,
            project_id: uuid.UUID
    ):
        return await ProjectMembersRepositories(self.session).check_admin(user_id, project_id)



