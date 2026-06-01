from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from pwdlib import PasswordHash
import jwt
import re

from src.config import settings

class TokenService:
    """
    Сервис для взаимодействия с jwt токеном
    """
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        except jwt.exceptions.JWSDecodeError:
            raise HTTPException(401, "Неверный токен")

class HashService:
    """
    Сервис для взаимодействия с хешем пароля
    """
    password_hash = PasswordHash.recommended()

    def verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.password_hash.hash(password)

class ValidationPasswordService:
    """
    Сервис для валидации пароля
    """
    MIN_LENGTH = 8
    MAX_LENGTH = 64

    ALLOWED_PATTERN = r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:,.<>?/|\\]+$'

    def __init__(self):
        self.errors = []

    def _check_avaible_poll(self, password):
        if not re.fullmatch(self.ALLOWED_PATTERN, password):
            self.errors.append("Используйте только латинские буквы (A-Z, a-z), цифры (0-9) и спецсимволы")

    def _check_min_length(self, password):
        if len(password) < self.MIN_LENGTH:
            self.errors.append("Минимум 8 символов")

    def _check_max_length(self, password):
        if len(password) > self.MAX_LENGTH:
            self.errors.append("Максимум 64 символов")

    def _check_capital_letters(self, password):
        if not re.search(r"[A-Z]", password):
            self.errors.append("Хотя бы одна заглавная")

    def _check_lowercase_letters(self, password):
        if not re.search(r"[a-z]", password):
            self.errors.append("Хотя бы одна строчная")

    def _check_numbers(self, password):
        if not re.search(r"\d", password):
            self.errors.append("Хотя бы одна цифра")

    def _check_symbols(self, password):
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            self.errors.append("Хотя бы один спецсимвол")

    def validate_password(self, password):
        """
        Получает пароль и возвращает все ошибки валидации найденные в пароле
        """
        self._check_min_length(password)
        self._check_max_length(password)
        self._check_avaible_poll(password)
        self._check_capital_letters(password)
        self._check_lowercase_letters(password)
        self._check_numbers(password)
        self._check_symbols(password)

        return self.errors


