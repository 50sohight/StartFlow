// src/lib/data/templates.ts

// ---------- API-compatible interfaces (used by Kanban and real board) ----------
export interface Task {
  id: string;
  title: string;
  description?: string;
  deadline?: string;       // ISO datetime string
  column_id: string;
  project_id?: string;     // optional, always set after load
}

export interface Column {
  id: string;
  name: string;            // API and Kanban use "name"
  position: number;
  tasks: Task[];
}

// ---------- Template-specific types (lightweight, no position/column_id) ----------
export interface TaskTemplate {
  id: string;
  title: string;
}

export interface ColumnTemplate {
  id: string;
  name: string;            // templates now also use "name"
  tasks: TaskTemplate[];
}

export interface BoardTemplate {
  id: string;
  name: string;
  description: string;
  columns: ColumnTemplate[];
}

// ---------- Pre-made templates ----------
export const templates: BoardTemplate[] = [
  {
    id: 'kanban',
    name: 'Kanban',
    description: 'Классическая доска для управления задачами',
    columns: [
      {
        id: 'col-1',
        name: 'Backlog',
        tasks: [
          { id: 't1', title: 'Сделать дизайн главной' },
          { id: 't2', title: 'Настроить CI/CD' },
        ],
      },
      {
        id: 'col-2',
        name: 'In Progress',
        tasks: [
          { id: 't3', title: 'Реализовать Kanban доску' },
          { id: 't4', title: 'Интеграция ИИ' },
        ],
      },
      {
        id: 'col-3',
        name: 'Done',
        tasks: [{ id: 't5', title: 'Верстка навигации' }],
      },
    ],
  },
  {
    id: 'marketing',
    name: 'Маркетинг',
    description: 'Воронка контента и кампаний',
    columns: [
      {
        id: 'm-1',
        name: 'Идеи',
        tasks: [
          { id: 'm-t1', title: 'Статья про SEO' },
          { id: 'm-t2', title: 'Видео-обзор' },
        ],
      },
      { id: 'm-2', name: 'В работе', tasks: [] },
      { id: 'm-3', name: 'На согласовании', tasks: [] },
      { id: 'm-4', name: 'Опубликовано', tasks: [] },
    ],
  },
  {
    id: 'empty',
    name: 'Пустая доска',
    description: 'Начни с чистого листа',
    columns: [
      { id: 'e-1', name: 'Нужно сделать', tasks: [] },
      { id: 'e-2', name: 'В процессе', tasks: [] },
      { id: 'e-3', name: 'Готово', tasks: [] },
    ],
  },
  {
    id: 'ss',
    name: 'SyropyatovSpecial',
    description:
      'Специальный шаблон от Егора Сыропятова (TM), призванный в разы ускорить разработку продуктов',
    columns: [
      { id: 'd-1', name: 'Начать', tasks: [{ id: 'col-1', title: 'Делайть бабки' }] },
      { id: 'd-2', name: 'Сделать', tasks: [] },
      { id: 'd-3', name: 'Кончить', tasks: [] },
    ],
  },
];