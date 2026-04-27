from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    login: str = Field(..., max_length=100)
    fullname: str = Field(..., max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=1, max_length=255)


class UserUpdate(BaseModel):
    login: str | None = Field(None, max_length=100)
    fullname: str | None = Field(None, max_length=100)
    password: str | None = Field(None, min_length=1, max_length=255)


class UserRead(UserBase):
    """Ответ API: без секретов."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID


class UserInDB(UserBase):
    """Соответствует полям UsersOrm (в т.ч. для чтения из сессии)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    password_hash: str
