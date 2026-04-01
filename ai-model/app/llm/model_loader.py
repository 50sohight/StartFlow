import os
import json
from typing import List, Literal
from llama_cpp import Llama
from loguru import logger

class VikhrRAG:
    # Классовые атрибуты для загрузки модели
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(CURRENT_DIR, "../../models")
    MODEL_FILENAME = "Vikhr-Llama3.1-8B-Instruct-R-21-09-24.Q4_K_M.gguf"
    MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
    _llm_instance = None

    # Системный промпт для генерации текста (обязателен для RAG)
    GROUNDED_SYSTEM_PROMPT = (
        "Your task is to answer the user's questions using only the information "
        "from the provided documents. Give two answers to each question: one with "
        "a list of relevant document identifiers and the second with the answer "
        "to the question itself, using documents with these identifiers."
    )

    # Системный промпт для работы с графиками (только JSON)
    CHART_SYSTEM_PROMPT = (
        "You are a professional data analyst. Your task is to analyze the provided text "
        "and extract structured data for visualization. "
        "Return the result STRICTLY as a valid JSON object. "
        "DO NOT add any introductory text, explanations, or markdown formatting (like `\`json). "
        "Return ONLY the JSON object."
    )

    def __init__(self, systemprompt=GROUNDED_SYSTEM_PROMPT, n_gpu_layers=0, n_ctx=2048, verbose=False):
        """
        Инициализация экземпляра. Параметры загрузки модели берутся из классовых атрибутов.
        :param systemprompt: Системный промпт (если None, используется GROUNDED_SYSTEM_PROMPT)
        :param n_gpu_layers: Количество слоев на GPU (переопределяет классовое значение)
        :param n_ctx: Контекстное окно (переопределяет классовое значение)
        :param verbose: Логирование в консоль
        """
        self.systemprompt = systemprompt if systemprompt is not None else self.GROUNDED_SYSTEM_PROMPT
        self.n_gpu_layers = n_gpu_layers
        self.n_ctx = n_ctx
        self.verbose = verbose
        logger.info(f"Initializing VikhrRAG with n_gpu_layers={n_gpu_layers}, n_ctx={n_ctx}")

    @classmethod
    def get_llm(cls):
        """
        Класс-метод для получения/создания единственного экземпляра модели.
        Использует классовые атрибуты для загрузки модели.
        """
        if cls._llm_instance is None:
            if not os.path.exists(cls.MODEL_PATH):
                raise FileNotFoundError(
                    f"Модель не найдена: {cls.MODEL_PATH}\n"
                    f"Скачайте модель и положите в папку: {os.path.abspath(cls.MODEL_DIR)}"
                )

            logger.info(f"Загрузка модели из {cls.MODEL_PATH}...")

            cls._llm_instance = Llama(
                model_path=cls.MODEL_PATH,
                n_gpu_layers=20,
                n_ctx=2048,  # Контекст
                verbose=False
            )
            logger.success("Модель успешно загружена")

        return cls._llm_instance

    def ask_vikhr(
            self,
            user_query: str,
            documents: List,
            # Параметры генерации для ЭТАПА 2 (финальный ответ)
            temperature: float = 0.3,
            top_k: int = 40,
            max_tokens: int = 2048,
            mode: Literal["rag", "chart"] = "rag"
            ) -> str:
        """
        Метод экземпляра для выполнения RAG-запросов с настраиваемыми параметрами.

        :param user_query: Запрос пользователя
        :param documents: Список документов для RAG
        :param temperature: Температура генерации для финального ответа (0.1 - точно, 0.7 - творчески)
        :param top_k: Ограничение выборки токенов
        :param max_tokens: Макс длина ответа
        :return: Ответ модели
        """

        # Получаем модель (она одна на всех, загружается при первом вызове)
        llm = VikhrRAG.get_llm()

        if mode == "chart":
            messages = [
                {"role": "system", "content": self.CHART_SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ]

            try:
                output = llm.create_chat_completion(
                    messages=messages,
                    temperature=max(0.1, temperature),  # Для качества лучше низкая
                    top_k=top_k,
                    max_tokens=max_tokens
                )
                return output['choices'][0]['message']['content']
            except Exception as e:
                logger.exception(f"Chart generation failed: {e}")
                raise

        else:
            messages_step1 = [
                {"role": "system", "content": self.systemprompt},
                {"role": "documents", "content": json.dumps(documents, ensure_ascii=False)},
                {"role": "user", "content": user_query}
            ]

            # ЭТАП 1: Поиск документов
            try:
                output_step1 = llm.create_chat_completion(
                    messages=messages_step1,
                    temperature=0.0,
                    max_tokens=256
                )
                relevant_indexes = output_step1['choices'][0]['message']['content']
            except Exception as e:
                logger.exception("RAG Step 1 failed")
                raise

            messages_step2 = messages_step1 + [
                {"role": "assistant", "content": relevant_indexes}
            ]

            # ЭТАП 2: Генерация ответа (как было)
            try:
                output_step2 = llm.create_chat_completion(
                    messages=messages_step2,
                    temperature=temperature,
                    top_k=top_k,
                    max_tokens=max_tokens
                )
                final_answer = output_step2['choices'][0]['message']['content']
                return final_answer
            except Exception as e:
                logger.error(f"RAG Step 2 error: {e}")
                return "Ошибка при генерации ответа."