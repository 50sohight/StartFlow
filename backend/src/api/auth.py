from typing import Annotated

from fastapi import APIRouter, HTTPException, Response

from src.database import async_session_maker
from src.schemas.users import UserRequestAdd, UserAdd, UserRequestLogin
from src.repositories.users import UsersRepository
from src.services.auth import AuthService
from src.api.dependencies import get_current_user_id, UserIdDep

router = APIRouter(prefix="/auth", tags=["Аутентификация"])

@router.post("/register")
async def register(
        data: UserRequestAdd
):
    password_hash = AuthService().get_password_hash(data.password)
    user_info = UserAdd(login=data.login, fullname=data.fullname, password_hash=password_hash)
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_one_or_none(login=user_info.login)
        if user:
            raise HTTPException(409, "Пользователь уже зарегестрирован")
        await UsersRepository(session).add(user_info)
        await session.commit()

    return {"status": 200}


@router.post("/login")
async def login(
        data: UserRequestLogin,
        response: Response
):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(login=data.login)
        if user is None:
            raise HTTPException(401, "Пользователь с таким логином не зарегистрирован")
        if not AuthService().verify_password(data.password, user.password_hash):
            raise HTTPException(401, "Введен неверный логин")
        access_token = AuthService().create_access_token({"user_id": str(user.id)})
        response.set_cookie("access_token", access_token)

        return {"status": 200}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": 200}

@router.get("/me")
async def get_me(
        user_id: UserIdDep
):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_one_or_none(id=user_id)
        return user



