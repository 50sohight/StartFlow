"""Pydantic модели для запросов"""

from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ModelRequest(BaseModel):
    user_query: str
    documents: List[str]
    temparature: float = 0.3
    top_k: int = 40
    max_tokens: int = 2048

class ModelResponse(BaseModel):
    parsed: Optional[Dict[str, Any]]
    raw: Optional[Any] = None  # На случай, если не получится распарсить
    error: Optional[str] = None  # В случае, если будут ошибки

    # def ask_vikhr(
    #         self,
    #         user_query: str,
    #         documents: List,
    #         # Параметры генерации для ЭТАПА 2 (финальный ответ)
    #         temperature: float = 0.3,
    #         top_k: int = 40,
    #         max_tokens: int = 2048
    #         ) -> str:
    #     """
    #     Метод экземпляра для выполнения RAG-запросов с настраиваемыми параметрами.
    #
    #     :param user_query: Запрос пользователя
    #     :param documents: Список документов для RAG
    #     :param temperature: Температура генерации для финального ответа (0.1 - точно, 0.7 - творчески)
    #     :param top_k: Ограничение выборки токенов
    #     :param max_tokens: Макс длина ответа
    #     :return: Ответ модели
    #     """