from sqlalchemy import select
from src.repositories.base import BaseRepository
from src.models import UsersOrm
from src.schemas.users import User, UserWithHashedPassword

class UsersRepository(BaseRepository):
    model = UsersOrm
    schema = User

    async def get_user_with_hashed_password(self, login: str):
        stmt = select(self.model).filter_by(login=login)
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return UserWithHashedPassword.model_validate(model)

