import os
import json
from typing import List
from llama_cpp import Llama


class VikhrRAG:
    # Классовые атрибуты для загрузки модели
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(CURRENT_DIR, "../../models")
    MODEL_FILENAME = "Vikhr-Llama3.1-8B-Instruct-R-21-09-24.Q4_K_M.gguf"
    MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
    _llm_instance = None

    # Системный промпт (обязателен для RAG)
    GROUNDED_SYSTEM_PROMPT = (
        "Your task is to answer the user's questions using only the information "
        "from the provided documents. Give two answers to each question: one with "
        "a list of relevant document identifiers and the second with the answer "
        "to the question itself, using documents with these identifiers."
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

            print(f"Загрузка модели из {cls.MODEL_PATH}...")

            cls._llm_instance = Llama(
                model_path=cls.MODEL_PATH,
                n_gpu_layers=20,
                n_ctx=2048,  # Контекст
                verbose=False
            )
            print("Модель загружена!")

        return cls._llm_instance

    def ask_vikhr(
            self,
            user_query: str,
            documents: List,
            # Параметры генерации для ЭТАПА 2 (финальный ответ)
            temperature: float = 0.3,
            top_k: int = 40,
            max_tokens: int = 2048
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

        # Формируем сообщения для RAG
        messages_step1 = [
            {"role": "system", "content": self.systemprompt},
            {"role": "documents", "content": json.dumps(documents, ensure_ascii=False)},
            {"role": "user", "content": user_query}
        ]

        # --- ЭТАП 1: Поиск документов (всегда точный) ---
        # Для поиска ID документов всегда используем нулевую температуру,
        # чтобы модель не выдумывала несуществующие ID.
        try:
            output_step1 = llm.create_chat_completion(
                messages=messages_step1,
                temperature=0.0,  # Фиксировано для точности
                max_tokens=256
            )
            relevant_indexes = output_step1['choices'][0]['message']['content']
        except Exception as e:
            print(f"Ошибка на этапе 1 (поиск): {e}")
            return "Ошибка при поиске документов."

        # Настройка параметров для генерации
        messages_step2 = messages_step1 + [
            {"role": "assistant", "content": relevant_indexes}
        ]

        try:
            output_step2 = llm.create_chat_completion(
                messages=messages_step2,
                temperature=temperature,  # Из аргументов функции
                top_k=top_k,  # Из аргументов функции
                max_tokens=max_tokens  # Из аргументов функции
            )
            final_answer = output_step2['choices'][0]['message']['content']
            return final_answer

        except Exception as e:
            print(f"Ошибка на этапе 2 (генерация): {e}")
            return "Ошибка при генерации ответа."


if __name__ == "__main__":
    print("--- Запуск теста модели VikhrRAG ---")

    # 1. Инициализация (создаст объект, но модель загрузится только при первом запросе)
    # Проверьте, чтобы в классе __init__ было n_gpu_layers=0 !!!
    rag_bot = VikhrRAG()

    # 2. Эмуляция базы данных проектов
    # У вас это будет лежать в PostgreSQL/MySQL, здесь пример для теста
    project_db = {
        101: {
            "name": "Сайт доставки пиццы",
            "description": """
                Проект: Сайт доставки пиццы 'Маргарита'.
                Стек: Python, Django, PostgreSQL.
                Особенности: Интеграция с картами, онлайн-оплата.
                Статус: В разработке. Дедлайн: 15 декабря.
                Ответственный: Иван Иванов.
            """
        },
        102: {
            "name": "Мобильное приложение банка",
            "description": """
                Проект: Банковский клиент для iOS/Android.
                Стек: Flutter, Dart.
                Текущая задача: Редизайн экрана авторизации.
                Бюджет: 2 млн рублей.
            """
        }
    }


    # 3. Функция, которая "достает" данные и спрашивает модель
    def ask_project_question(project_id, question):
        print(f"\n[Запрос по проекту ID {project_id}]")

        # Достаем данные из "БД"
        project_data = project_db.get(project_id)
        if not project_data:
            return "Проект не найден."

        # Формируем документы для модели (она ожидает формат JSON)
        # Обратите внимание: content до 4000 символов
        docs = [
            {
                "doc_id": 0,
                "title": project_data["name"],
                "content": project_data["description"]
            }
        ]

        # Задаем вопрос
        return rag_bot.ask_vikhr(user_query=question, documents=docs, temperature=0.1)


    # 4. Тестовые кейсы

    # Вопрос по первому проекту
    ans1 = ask_project_question(101, "Какой дедлайн у проекта?")
    print(f"Ответ модели: {ans1}")

    # Вопрос по второму проекту (проверка контекста)
    ans2 = ask_project_question(102, "На чем пишем приложение?")
    print(f"Ответ модели: {ans2}")

    # Вопрос, ответа на который нет
    ans3 = ask_project_question(101, "Кто директор компании?")
    print(f"Ответ модели: {ans3}")