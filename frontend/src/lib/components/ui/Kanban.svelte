<script lang="ts">
  import { flip } from 'svelte/animate';
  import { quintOut } from 'svelte/easing';
  import { Plus, X, GripVertical } from 'lucide-svelte';
  import type { Column } from '$lib/data/templates'; // Импортируем типы

  // --- Пропсы ---
  // bind:columns позволяет менять данные прямо из родителя
  let { columns = $bindable<Column[]>() } = $props();

  // --- Вспомогательные функции (остаются как были) ---
  function initFocus(node: HTMLInputElement) {
    node.focus();
    node.select();
  }

  // --- Логика D&D ---
  let draggedTask = $state<{ taskId: string, sourceColId: string } | null>(null);

  function handleDragStart(e: DragEvent, taskId: string, colId: string) {
    draggedTask = { taskId, sourceColId: colId };
    if (e.dataTransfer) {
      e.dataTransfer.effectAllowed = 'move';
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = 'move';
    }
  }

  function handleDrop(targetColId: string) {
    if (!draggedTask) return;

    const { taskId, sourceColId } = draggedTask;
    if (sourceColId === targetColId) return;

    // Логика перемещения меняет локальный стейт, который проброшен через bindable
    let movedTask: any = null;

    // 1. Находим и удаляем задачу
    columns = columns.map(col => {
      if (col.id === sourceColId) {
        movedTask = col.tasks.find(t => t.id === taskId);
        return { ...col, tasks: col.tasks.filter(t => t.id !== taskId) };
      }
      return col;
    });

    // 2. Добавляем в новую
    if (movedTask) {
      columns = columns.map(col => {
        if (col.id === targetColId) {
          return { ...col, tasks: [...col.tasks, movedTask] };
        }
        return col;
      });
    }

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
          return { ...col, tasks: col.tasks.map(t => t.id === taskId ? { ...t, title: currentText } : t) };
        } else {
          return { ...col, title: currentText };
        }
      }
      return col;
    });
    
    editingId = null;
    currentText = '';
  }

  // --- CRUD ---
  function addColumn() {
    const newCol: Column = {
      id: `col-${Date.now()}`,
      title: 'Новая колонка',
      tasks: []
    };
    columns = [...columns, newCol];
    setTimeout(() => startEdit(newCol.id, newCol.title), 50);
  }

  function addTask(colId: string) {
    const newTask = { id: `task-${Date.now()}`, title: 'Новая задача' };
    columns = columns.map(col => 
      col.id === colId ? { ...col, tasks: [...col.tasks, newTask] } : col
    );
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

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') editingId = null;
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<!-- Весь HTML код доски остается практически без изменений -->
<!-- Просто копируй его сюда из своего файла -->
<!-- Я сократил HTML для краткости, но структура та же -->
<div class="flex gap-4 items-start overflow-x-auto pb-4 h-full">
  {#each columns as col (col.id)}
    <div 
      class="flex-shrink-0 w-72 bg-gray-200/50 rounded-xl flex flex-col max-h-full border border-transparent hover:border-gray-300 transition"
      ondragover={handleDragOver}
      ondrop={() => handleDrop(col.id)}
    >
      <!-- Шапка -->
      <div class="p-3 flex items-center justify-between border-b border-gray-200/50">
        <!-- ... Инпут или заголовок ... -->
      </div>

      <!-- Задачи -->
      <div class="flex-1 overflow-y-auto p-2 space-y-2 min-h-[100px]">
        {#each col.tasks as task (task.id)}
           <!-- ... Карточка задачи ... -->
        {/each}
      </div>

      <!-- Добавить задачу -->
      <div class="p-2">
        <button onclick={() => addTask(col.id)}>
          + Добавить задачу
        </button>
      </div>
    </div>
  {/each}

  <!-- Добавить колонку -->
  <div class="flex-shrink-0 w-72">
    <button onclick={addColumn}>
      + Добавить колонку
    </button>
  </div>
</div>