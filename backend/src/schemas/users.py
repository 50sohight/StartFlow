from pydantic import BaseModel, ConfigDict

import uuid

class UserRequestLogin(BaseModel):
    login: str
    password: str

class UserRequestAdd(BaseModel):
    login: str
    fullname: str
    password: str

class UserAdd(BaseModel):
    login: str
    fullname: str
    password_hash: str

class User(BaseModel):
    id: uuid.UUID
    login: str
    fullname: str

    model_config = ConfigDict(from_attributes=True)


class UserWithHashedPassword(User):
    password_hash: str