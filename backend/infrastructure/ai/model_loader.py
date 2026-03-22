import os
import json
from llama_cpp import Llama

# --- КОНФИГУРАЦИЯ ---

# Автоматический поиск пути к модели (относительно этого скрипта)
# Скрипт лежит в: backend/infrastructure/ai/
# Модель лежит в: backend/infrastructure/models/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CURRENT_DIR, "..", "models")  # Поднимаемся на уровень вверх и заходим в models
MODEL_FILENAME = "Vikhr-Llama3.1-8B-Instruct-R-21-09-24.Q4_K_M.gguf" # Рекомендую Q4 для 8GB VRAM
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)

# Системный промпт (обязателен для RAG из документации!!!)
GROUNDED_SYSTEM_PROMPT = (
    "Your task is to answer the user's questions using only the information "
    "from the provided documents. Give two answers to each question: one with "
    "a list of relevant document identifiers and the second with the answer "
    "to the question itself, using documents with these identifiers."
)

# --- ИНИЦИАЛИЗАЦИЯ ---
_llm_instance = None

def get_llm():
    """Загрузка модели при первом вызове"""
    global _llm_instance
    if _llm_instance is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Модель не найдена: {MODEL_PATH}\n"
                f"Скачайте модель и положите в папку: {os.path.abspath(MODEL_DIR)}"
            )

        print(f"Загрузка модели из {MODEL_PATH}...")
        _llm_instance = Llama(
            model_path=MODEL_PATH,
            n_gpu_layers=-1,    # Только видеокарта
            n_ctx=4096,         # Контекст
            verbose=False       # Убрать технический мусор в консоли
        )
        print("Модель загружена!")
    return _llm_instance

# --- ОСНОВНАЯ ФУНКЦИЯ ---
def ask_vikhr(user_query: str, documents: list) -> str:
    """
    Отправляет запрос к модели с использованием RAG.

    :param user_query: Вопрос пользователя (строка).
    :param documents: Список документов (список словарей с ключами doc_id, title, content).
    :return: Текстовый ответ модели.
    """
    llm = get_llm()

    # Примечание: llama-cpp-python поддерживает роль 'documents' для Llama 3.1
    messages_step1 = [
        {"role": "system", "content": GROUNDED_SYSTEM_PROMPT},
        {"role": "documents", "content": json.dumps(documents, ensure_ascii=False)},
        {"role": "user", "content": user_query}
    ]

    # Этап 1: Получение релевантных документов ---
    try:
        output_step1 = llm.create_chat_completion(
            messages=messages_step1,
            temperature=0.0,      # Нулевая температура для точного поиска ID
            max_tokens=256
        )
        relevant_indexes = output_step1['choices'][0]['message']['content']

        # print(f"[DEBUG] Relevant IDs: {relevant_indexes}")

    except Exception as e:
        print(f"Ошибка на этапе 1: {e}")
        return "Ошибка при поиске документов."

    # Этап 2: Генерация финального ответа
    # Добавляем результат этапа 1 как сообщение от ассистента
    messages_step2 = messages_step1 + [
        {"role": "assistant", "content": relevant_indexes}
    ]

    try:
        output_step2 = llm.create_chat_completion(
            messages=messages_step2,
            temperature=0.3,      # Чуть выше для естественности
            top_k=40,             # Рекомендовано авторами
            max_tokens=2048
        )
        final_answer = output_step2['choices'][0]['message']['content']
        return final_answer

    except Exception as e:
        print(f"Ошибка на этапе 2: {e}")
        return "Ошибка при генерации ответа."
