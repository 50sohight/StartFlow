export interface Task {
  id: string;
  title: string;
}

export interface Column {
  id: string;
  title: string;
  tasks: Task[];
}

export interface BoardTemplate {
  id: string;
  name: string;
  description: string;
  columns: Column[];
}

// Массив готовых шаблонов
export const templates: BoardTemplate[] = [
  {
    id: 'kanban',
    name: 'Kanban',
    description: 'Классическая доска для управления задачами',
    columns: [
      {
        id: 'col-1',
        title: 'Backlog',
        tasks: [
          { id: 't1', title: 'Сделать дизайн главной' },
          { id: 't2', title: 'Настроить CI/CD' },
        ]
      },
      {
        id: 'col-2',
        title: 'In Progress',
        tasks: [
          { id: 't3', title: 'Реализовать Kanban доску' },
          { id: 't4', title: 'Интеграция ИИ' },
        ]
      },
      {
        id: 'col-3',
        title: 'Done',
        tasks: [
          { id: 't5', title: 'Верстка навигации' },
        ]
      }
    ]
  },
  {
    id: 'marketing',
    name: 'Маркетинг',
    description: 'Воронка контента и кампаний',
    columns: [
      {
        id: 'm-1',
        title: 'Идеи',
        tasks: [
          { id: 'm-t1', title: 'Статья про SEO' },
          { id: 'm-t2', title: 'Видео-обзор' },
        ]
      },
      {
        id: 'm-2',
        title: 'В работе',
        tasks: []
      },
      {
        id: 'm-3',
        title: 'На согласовании',
        tasks: []
      },
       {
        id: 'm-4',
        title: 'Опубликовано',
        tasks: []
      }
    ]
  },
  {
    id: 'empty',
    name: 'Пустая доска',
    description: 'Начни с чистого листа',
    columns: [
      { id: 'e-1', title: 'Нужно сделать', tasks: [] },
      { id: 'e-2', title: 'В процессе', tasks: [] },
      { id: 'e-3', title: 'Готово', tasks: [] },
    ]
  }
];