import os
import json
import re
from collections import Counter
from typing import List, Literal
from loguru import logger
from .prompts import RAG_SYSTEM_PROMPT, CHART_SYSTEM_PROMPT

try:
    from llama_cpp import Llama as LlamaCpp  # pyright: ignore[reportMissingImports]
except Exception:
    LlamaCpp = None


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning(f"Invalid integer for {name}={raw!r}. Using default={default}.")
        return default


class MockLlama:
    """Deterministic fallback backend used when local model is unavailable."""

    STATUS_WORDS = ["done", "in progress", "todo", "to do", "blocked", "review"]

    def create_chat_completion(self, messages, **_kwargs):
        system_text = "\n".join(
            m.get("content", "") for m in messages if m.get("role") == "system"
        ).lower()

        if "valid json" in system_text:
            content = self._chart_response(messages)
            return {"choices": [{"message": {"content": content}}]}

        content = self._rag_response(messages)
        return {"choices": [{"message": {"content": content}}]}

    def _rag_response(self, messages) -> str:
        docs_json = next(
            (m.get("content", "[]") for m in messages if m.get("role") == "documents"),
            "[]",
        )
        try:
            docs = json.loads(docs_json)
        except Exception:
            docs = []

        has_assistant = any(m.get("role") == "assistant" for m in messages)
        if not has_assistant:
            indexes = list(range(len(docs)))
            return str(indexes)

        user_query = next(
            (m.get("content", "") for m in reversed(messages) if m.get("role") == "user"),
            "",
        )
        user_query_lower = user_query.lower()

        if not docs:
            return (
                "SOURCES: []\n"
                "ANSWER: Недостаточно данных в документах для точного ответа.\n"
                "CONFIDENCE: low"
            )

        # Heuristic: owner question without owner markers is considered insufficient data.
        owner_question = any(x in user_query_lower for x in ["владел", "owner"])
        owner_markers = ["owner", "владел", "собствен", "project owner"]
        has_owner_data = any(
            any(marker in str(d).lower() for marker in owner_markers) for d in docs
        )
        if owner_question and not has_owner_data:
            return (
                f"SOURCES: {list(range(len(docs)))}\n"
                "ANSWER: Недостаточно данных в документах, чтобы определить владельца проекта.\n"
                "CONFIDENCE: low"
            )

        # Heuristic: deadline question with multiple different dates means conflict.
        deadline_question = any(x in user_query_lower for x in ["дедлайн", "deadline"])
        all_dates = []
        for doc in docs:
            all_dates.extend(re.findall(r"\b\d{4}-\d{2}-\d{2}\b", str(doc)))
        unique_dates = sorted(set(all_dates))
        if deadline_question and len(unique_dates) > 1:
            return (
                f"SOURCES: {list(range(len(docs)))}\n"
                f"ANSWER: Найден конфликт (conflict) данных по дедлайну: {', '.join(unique_dates)}.\n"
                "CONFIDENCE: low"
            )

        preview = " | ".join(str(d) for d in docs[:2])
        return (
            f"SOURCES: {list(range(len(docs)))}\n"
            f"ANSWER: По запросу '{user_query}' использованы документы: {preview}.\n"
            "CONFIDENCE: medium"
        )

    def _chart_response(self, messages) -> str:
        user_text = "\n".join(
            m.get("content", "") for m in messages if m.get("role") == "user"
        )
        lowered = user_text.lower()

        statuses = re.findall(r"\(([^)]+)\)", user_text)
        if statuses:
            counts = Counter(statuses)
        else:
            counts = Counter()
            for word in self.STATUS_WORDS:
                matches = re.findall(rf"\b{re.escape(word)}\b", lowered)
                if matches:
                    counts[word.title()] = len(matches)

        labels = list(counts.keys())
        values = [counts[k] for k in labels]
        title = "Status Chart" if labels else "Недостаточно данных для графика"
        payload = {
            "title": title,
            "chart_type": "bar",
            "labels": labels,
            "values": values,
        }
        return json.dumps(payload, ensure_ascii=False)


class VikhrRAG:
    # Классовые атрибуты для загрузки модели
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(CURRENT_DIR, "../../models")
    DEFAULT_MODEL_FILENAME = "Vikhr-Llama3.1-8B-Instruct-R-21-09-24.Q4_K_M.gguf"
    _llm_instance = None
    _backend_name = "uninitialized"

    @classmethod
    def get_model_path(cls) -> str:
        model_path = os.getenv("STARTFLOW_MODEL_PATH")
        if model_path:
            return model_path

        filename = os.getenv("STARTFLOW_MODEL_FILENAME", cls.DEFAULT_MODEL_FILENAME)
        return os.path.join(cls.MODEL_DIR, filename)

    def __init__(
        self, systemprompt=RAG_SYSTEM_PROMPT, n_gpu_layers=0, n_ctx=2048, verbose=False
    ):
        """
        Инициализация экземпляра. Параметры загрузки модели берутся из классовых атрибутов.
        :param systemprompt: Системный промпт (если None, используется RAG_SYSTEM_PROMPT)
        :param n_gpu_layers: Количество слоев на GPU (переопределяет классовое значение)
        :param n_ctx: Контекстное окно (переопределяет классовое значение)
        :param verbose: Логирование в консоль
        """
        self.systemprompt = (
            systemprompt if systemprompt is not None else RAG_SYSTEM_PROMPT
        )
        self.n_gpu_layers = n_gpu_layers
        self.n_ctx = n_ctx
        self.verbose = verbose
        logger.info(
            f"Initializing VikhrRAG with n_gpu_layers={n_gpu_layers}, n_ctx={n_ctx}"
        )

    @classmethod
    def get_llm(cls):
        """
        Класс-метод для получения/создания единственного экземпляра модели.
        Использует классовые атрибуты для загрузки модели.
        """
        if cls._llm_instance is None:
            force_mock = _env_flag("STARTFLOW_MOCK_LLM", default=False)
            allow_fallback = _env_flag("STARTFLOW_ALLOW_MOCK_FALLBACK", default=True)
            model_path = cls.get_model_path()

            if force_mock:
                cls._llm_instance = MockLlama()
                cls._backend_name = "mock"
                logger.warning("STARTFLOW_MOCK_LLM enabled. Using mock backend.")
                return cls._llm_instance

            if LlamaCpp is None:
                if not allow_fallback:
                    raise RuntimeError("llama_cpp не установлен, а fallback отключен")

                cls._llm_instance = MockLlama()
                cls._backend_name = "mock"
                logger.warning("llama_cpp unavailable. Using mock backend.")
                return cls._llm_instance

            if not os.path.exists(model_path):
                if not allow_fallback:
                    raise FileNotFoundError(
                        f"Модель не найдена: {model_path}\n"
                        f"Скачайте модель и положите в папку: {os.path.abspath(cls.MODEL_DIR)}"
                    )

                cls._llm_instance = MockLlama()
                cls._backend_name = "mock"
                logger.warning(
                    "Model file is missing. Using mock backend until model is provided."
                )
                return cls._llm_instance

            n_gpu_layers = _env_int("STARTFLOW_N_GPU_LAYERS", 20)
            n_ctx = _env_int("STARTFLOW_N_CTX", 2048)
            verbose = _env_flag("STARTFLOW_VERBOSE", default=False)

            logger.info(f"Загрузка модели из {model_path}...")

            cls._llm_instance = LlamaCpp(
                model_path=model_path,
                n_gpu_layers=n_gpu_layers,
                n_ctx=n_ctx,
                verbose=verbose,
            )
            cls._backend_name = "llama_cpp"
            logger.success("Модель успешно загружена")

        return cls._llm_instance

    @classmethod
    def get_backend_name(cls) -> str:
        if cls._llm_instance is None:
            cls.get_llm()
        return cls._backend_name

    def ask_vikhr(
        self,
        user_query: str,
        documents: List,
        # Параметры генерации для ЭТАПА 2 (финальный ответ)
        temperature: float = 0.3,
        top_k: int = 40,
        max_tokens: int = 2048,
        mode: Literal["rag", "chart"] = "rag",
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
            context = ""
            if documents:
                context = "\n\nData from document:\n" + "\n".join(documents)

            messages = [
                {"role": "system", "content": CHART_SYSTEM_PROMPT},
                {"role": "user", "content": user_query + context},
            ]

            try:
                output = llm.create_chat_completion(
                    messages=messages,
                    temperature=max(0.1, temperature),  # Для качества лучше низкая
                    top_k=top_k,
                    max_tokens=max_tokens,
                )
                return output["choices"][0]["message"]["content"]
            except Exception as e:
                logger.exception(f"Chart generation failed: {e}")
                raise

        else:
            messages_step1 = [
                {"role": "system", "content": self.systemprompt},
                {
                    "role": "documents",
                    "content": json.dumps(documents, ensure_ascii=False),
                },
                {"role": "user", "content": user_query},
            ]

            # ЭТАП 1: Поиск документов
            try:
                output_step1 = llm.create_chat_completion(
                    messages=messages_step1, temperature=0.0, max_tokens=256
                )
                relevant_indexes = output_step1["choices"][0]["message"]["content"]
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
                    max_tokens=max_tokens,
                )
                final_answer = output_step2["choices"][0]["message"]["content"]
                return final_answer
            except Exception as e:
                logger.error(f"RAG Step 2 error: {e}")
                return "Ошибка при генерации ответа."
