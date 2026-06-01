from typing import Annotated

from fastapi import APIRouter, HTTPException, Response

from src.config import settings
from src.database import async_session_maker
from src.schemas.users import UserRequestAdd, UserAdd, UserRequestLogin
from src.repositories.users import UsersRepository
from src.services.auth import HashService, TokenService, ValidationPasswordService
from src.api.dependencies import UserIdDep

router = APIRouter(prefix="/auth", tags=["Аутентификация"])

@router.post("/register")
async def register(
        data: UserRequestAdd,
        response: Response
):
    """
    Генерирует хэш пароля, записывает login + hash_password в БД, генерирует jwt_token и возвращает его по куки
    """

    errors = ValidationPasswordService().validate_password(data.password)
    if errors:
        raise HTTPException(400, detail={"body": "Пароль не прошел проверку", "detail": errors})

    password_hash = HashService().get_password_hash(data.password)
    user_info = UserAdd(login=data.login, fullname=data.fullname, password_hash=password_hash)

    async with async_session_maker() as session:
        user = await UsersRepository(session).get_one_or_none(login=user_info.login)
        if user:
            raise HTTPException(409, "Пользователь уже зарегестрирован")
        create_user = await UsersRepository(session).add(user_info)
        await session.commit()

    access_token = TokenService().create_access_token({"user_id": str(create_user.id)})
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS
    )

    return {"success": True}


@router.post("/login")
async def login(
        data: UserRequestLogin,
        response: Response
):
    """
    Генерирует хэш по паролю который ввел клиент, возвращает jwt токен в куки
    """
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(login=data.login)

    if user is None:
        raise HTTPException(401, "Пользователь с таким логином не зарегистрирован")
    if not HashService().verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Введен неверный логин")

    access_token = TokenService().create_access_token({"user_id": str(user.id)})
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS
    )

    return {"success": True}

@router.post("/logout")
async def logout(response: Response):
    """
    Удаляет jwt токен из куки
    """
    response.delete_cookie("access_token")
    return {"success": True}

@router.get("/me")
async def get_me(
        user_id: UserIdDep
):
    """
    Возращает текущего пользователя клиента по jwt токену
    """
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_one_or_none(id=user_id)
        return user