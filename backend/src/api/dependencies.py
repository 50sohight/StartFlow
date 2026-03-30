from typing import Annotated
import uuid

from fastapi import Depends, Request, HTTPException

from services.auth import AuthService


def get_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if access_token is None:
        raise HTTPException(401, "Не найден токен")
    return access_token

def get_current_user_id(access_token: Annotated[str, Depends(get_token)]) -> uuid.UUID:
    data = AuthService().decode_token(access_token)
    user_id = uuid.UUID(data["user_id"])
    return user_id


UserIdDep = Annotated[uuid.UUID, Depends(get_current_user_id)]
