# Prompt Baseline Scenarios

Этот файл содержит минимальный набор сценариев для ручной проверки `/api/generate`.

## Режим text (RAG)

### Case T1: Достаточно данных

Request:

```json
{
	"user_query": "Сколько задач в статусе Done?",
	"documents": ["Task A - Done", "Task B - In Progress", "Task C - Done"],
	"response_type": "text"
}
```

Expected:

- Ответ содержит блок `SOURCES`.
- Ответ содержит блок `ANSWER` на русском.
- Ответ содержит `CONFIDENCE`.
- В ответе нет выдуманных сущностей.

### Case T2: Недостаточно данных

Request:

```json
{
	"user_query": "Кто владелец проекта?",
	"documents": ["Project timeline: Q2 release"],
	"response_type": "text"
}
```

Expected:

- Явная формулировка о нехватке данных.
- Нет выдуманного имени владельца.

### Case T3: Конфликт в документах

Request:

```json
{
	"user_query": "Какой дедлайн у релиза?",
	"documents": ["Release deadline: 2026-05-20", "Release deadline: 2026-05-25"],
	"response_type": "text"
}
```

Expected:

- Отмечен конфликт данных.
- Указаны индексы/источники из документов.

## Режим chart

### Case C1: Агрегация по статусам

Request:

```json
{
	"user_query": "Построй график по статусам задач",
	"documents": ["Tasks: Task A (Done), Task B (Done), Task C (In Progress)"],
	"response_type": "chart"
}
```

Expected:

- `chart_data` заполнен.
- `labels` это категории (`Done`, `In Progress`), а не названия задач.
- `values` соответствует количеству категорий.

### Case C2: Пустой/недостаточный набор данных

Request:

```json
{
	"user_query": "Сделай график по приоритетам",
	"documents": [],
	"response_type": "chart"
}
```

Expected:

- Валидный JSON в `raw_answer` или валидный `chart_data` с пустыми массивами.
- Нет markdown и лишнего текста.

## Базовый чек-лист после изменений

- API контракт `/api/generate` не сломан.
- Для `response_type=chart` приходит валидный `ChartData` или понятный `error`.
- Для `response_type=text` соблюдается структура ответа из системного промпта.
