// src/lib/data/templates.ts

// ---------- API-совместимые интерфейсы ----------
export interface Task {
  id: string;
  title: string;
  description?: string;
  deadline?: string;       // ISO datetime string
  column_id: string;
  project_id?: string;
}

export interface Column {
  id: string;
  name: string;
  position: number;
  tasks: Task[];
}

// ---------- Типы для шаблонов ----------
export interface TaskTemplate {
  id: string;
  title: string;
}

export interface ColumnTemplate {
  id: string;
  name: string;            // шаблоны используют "name"
  tasks: TaskTemplate[];
}

export interface BoardTemplate {
  id: string;
  name: string;
  description: string;
  columns: ColumnTemplate[];
}

// ---------- Встроенные шаблоны ----------
const builtInTemplates: BoardTemplate[] = [
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

// ---------- Пользовательские шаблоны (localStorage) ----------
const STORAGE_KEY = 'userTemplates';

function loadUserTemplates(): BoardTemplate[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed;
    }
  } catch (e) {
    console.error('Ошибка загрузки пользовательских шаблонов:', e);
  }
  return [];
}

function saveUserTemplates(templates: BoardTemplate[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
}

// Функция для добавления нового пользовательского шаблона
export function addUserTemplate(template: BoardTemplate) {
  const userTemplates = loadUserTemplates();
  // Генерируем уникальный id
  const newTemplate: BoardTemplate = {
    ...template,
    id: `user-${Date.now()}`,
  };
  userTemplates.push(newTemplate);
  saveUserTemplates(userTemplates);
  // Обновляем хранилище
  allTemplates.set([...builtInTemplates, ...userTemplates]);
}

// ---------- Реактивное хранилище всех шаблонов ----------
import { writable } from 'svelte/store';

export const allTemplates = writable<BoardTemplate[]>([
  ...builtInTemplates,
  ...loadUserTemplates(),
]);