<script lang="ts">
  import { flip } from 'svelte/animate';
  import { quintOut } from 'svelte/easing';
  import { Plus, X, MoreHorizontal, GripVertical } from 'lucide-svelte';
  import Navbar from '$lib/components/layout/Navbar.svelte'; 

  function initFocus(node: HTMLInputElement) {
    node.focus();
    node.select();
  }

  // --- Типы данных ---
  interface Task {
    id: string;
    title: string;
  }

  interface Column {
    id: string;
    title: string;
    tasks: Task[];
  }

  // --- Локальное состояние (Mock Data) ---
  let columns = $state<Column[]>([
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
  ]);

  // --- Логика D&D ---
  let draggedTask = $state<{ task: Task, sourceColId: string } | null>(null);

  function handleDragStart(e: DragEvent, task: Task, colId: string) {
    draggedTask = { task, sourceColId: colId };
    // Убираем стили перетаскивания через пару мс (стандартный трюк)
    if (e.dataTransfer) {
      e.dataTransfer.effectAllowed = 'move';
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault(); // Разрешаем дроп
    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = 'move';
    }
  }

  function handleDrop(targetColId: string) {
    if (!draggedTask) return;

    const { task, sourceColId } = draggedTask;

    // Если кидаем в ту же колонку - пока ничего не делаем (или можно реализовать сортировку)
    if (sourceColId === targetColId) return;

    // 1. Удаляем из старой колонки
    columns = columns.map(col => {
      if (col.id === sourceColId) {
        return { ...col, tasks: col.tasks.filter(t => t.id !== task.id) };
      }
      return col;
    });

    // 2. Добавляем в новую колонку
    columns = columns.map(col => {
      if (col.id === targetColId) {
        return { ...col, tasks: [...col.tasks, task] };
      }
      return col;
    });

    draggedTask = null;
  }

  // --- Логика редактирования ---
  let editingId = $state<string | null>(null);
  let currentText = $state('');

  function startEdit(id: string, text: string) {
    editingId = id;
    currentText = text;
  }

  function saveEdit(colId: string, taskId?: string) {
    if (!currentText.trim()) return;

    columns = columns.map(col => {
      if (col.id === colId) {
        if (taskId) {
          // Редактирование задачи
          return {
            ...col,
            tasks: col.tasks.map(t => t.id === taskId ? { ...t, title: currentText } : t)
          };
        } else {
          // Редактирование колонки
          return { ...col, title: currentText };
        }
      }
      return col;
    });
    
    editingId = null;
    currentText = '';
  }

  // --- CRUD операции ---
  function addColumn() {
    const newCol: Column = {
      id: `col-${Date.now()}`,
      title: 'Новая колонка',
      tasks: []
    };
    columns = [...columns, newCol];
    // Сразу начинаем редактирование названия
    setTimeout(() => startEdit(newCol.id, newCol.title), 50);
  }

  function addTask(colId: string) {
    const newTask: Task = { id: `task-${Date.now()}`, title: 'Новая задача' };
    columns = columns.map(col => 
      col.id === colId ? { ...col, tasks: [...col.tasks, newTask] } : col
    );
    // Сразу начинаем редактирование
    setTimeout(() => startEdit(newTask.id, newTask.title), 50);
  }

  function deleteTask(colId: string, taskId: string) {
    columns = columns.map(col => 
      col.id === colId ? { ...col, tasks: col.tasks.filter(t => t.id !== taskId) } : col
    );
  }

  function deleteColumn(colId: string) {
    columns = columns.filter(col => col.id !== colId);
  }

  // Функция для отмены редактирования при клике вне инпута
  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      // Имитируем сохранение: находим активный элемент и триггерим blur
      // Но проще просто сохранить текущее состояние
      // Для простоты используем window.event в html (см. onblur)
    }
    if (e.key === 'Escape') {
        editingId = null;
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<svelte:head>
  <title>Моя доска | StartFlow</title>
</svelte:head>

<div class="p-4 md:p-6 bg-gray-100 h-[calc(100vh-64px)] overflow-auto">
  <!-- Заголовок доски -->
  <div class="flex items-center justify-between mb-6">
    <h1 class="text-2xl font-bold text-gray-800">Мой проект</h1>
    <div class="flex items-center space-x-2 text-gray-500 text-sm">
        <span class="bg-green-100 text-green-800 px-2 py-1 rounded font-medium">Kanban</span>
    </div>
  </div>

  <!-- Контейнер колонок -->
  <div class="flex gap-4 items-start overflow-x-auto pb-4 h-full">
    
    {#each columns as col (col.id)}
      <div 
        class="flex-shrink-0 w-72 bg-gray-200/50 rounded-xl flex flex-col max-h-full border border-transparent hover:border-gray-300 transition"
        ondragover={handleDragOver}
        ondrop={() => handleDrop(col.id)}
      >
        <!-- Шапка колонки -->
        <div class="p-3 flex items-center justify-between border-b border-gray-200/50">
          <div class="flex items-center w-full">
             {#if editingId === col.id}
                <input 
                  type="text" 
                  class="w-full bg-white border border-green-500 rounded px-2 py-1 text-sm font-semibold focus:outline-none"
                  bind:value={currentText}
                  onblur={() => saveEdit(col.id)}
                  use:initFocus
                />
             {:else}
                <h3 
                  class="font-semibold text-gray-700 cursor-pointer flex-1"
                  ondblclick={() => startEdit(col.id, col.title)}
                >
                  {col.title}
                </h3>
             {/if}
             
             <span class="text-xs text-gray-500 ml-2 bg-gray-200 px-1.5 py-0.5 rounded-full">{col.tasks.length}</span>
             
             <button 
                class="p-1 hover:bg-gray-300/50 rounded ml-1 text-gray-400 hover:text-red-500 transition"
                onclick={() => deleteColumn(col.id)}
             >
                <X size="14" />
             </button>
          </div>
        </div>

        <!-- Список задач -->
        <div class="flex-1 overflow-y-auto p-2 space-y-2 min-h-[100px]">
          {#each col.tasks as task (task.id)}
            <div 
              class="bg-white p-3 rounded-lg shadow-sm border border-gray-200 cursor-grab active:cursor-grabbing group relative hover:shadow-md transition animate:flip={{ duration: 200, easing: quintOut }}"
              draggable="true"
              ondragstart={(e) => handleDragStart(e, task, col.id)}
            >
              <!-- Контент задачи -->
              {#if editingId === task.id}
                <input 
                  type="text" 
                  class="w-full text-sm text-gray-700 bg-gray-50 border border-green-500 rounded px-1 py-0.5 focus:outline-none"
                  bind:value={currentText}
                  onblur={() => saveEdit(col.id, task.id)}
                  use:initFocus
                />
              {:else}
                <p 
                  class="text-sm text-gray-700 pr-4"
                  ondblclick={() => startEdit(task.id, task.title)}
                >
                  {task.title}
                </p>
              {/if}

              <!-- Иконка удаления -->
              <button 
                class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition text-gray-300 hover:text-red-500"
                onclick={() => deleteTask(col.id, task.id)}
              >
                <X size="12" />
              </button>
              
              <!-- Иконка перетаскивания (для красоты) -->
              <div class="absolute bottom-1 right-1 text-gray-200">
                 <GripVertical size="12" />
              </div>
            </div>
          {/each}
        </div>

        <!-- Кнопка добавления задачи -->
        <div class="p-2">
          <button 
            class="w-full text-left text-sm text-gray-500 hover:text-gray-800 hover:bg-gray-200/50 p-2 rounded-md transition flex items-center"
            onclick={() => addTask(col.id)}
          >
            <Plus size="16" class="mr-1" /> Добавить задачу
          </button>
        </div>
      </div>
    {/each}

    <!-- Кнопка добавления колонки -->
    <div class="flex-shrink-0 w-72">
      <button 
        class="w-full bg-white/50 hover:bg-white border-2 border-dashed border-gray-300 text-gray-500 font-semibold p-3 rounded-xl flex items-center justify-center transition hover:border-green-500 hover:text-green-600"
        onclick={addColumn}
      >
        <Plus size="20" class="mr-2" /> Добавить колонку
      </button>
    </div>

  </div>
</div>
