<script lang="ts">
  import { flip } from 'svelte/animate';
  import { quintOut } from 'svelte/easing';
  import { Plus, X, GripVertical } from 'lucide-svelte';
  // Импортируем И Column, И Task
  import type { Column, Task } from '$lib/data/templates';

  let { columns = $bindable<Column[]>() } = $props();

  function initFocus(node: HTMLInputElement) {
    node.focus();
    node.select();
  }

  // --- D&D Логика ---
  let draggedTask = $state<{ taskId: string, sourceColId: string } | null>(null);

  function handleDragStart(e: DragEvent, taskId: string, colId: string) {
    draggedTask = { taskId, sourceColId: colId };
    if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move';
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
  }

  // Добавил аргумент e (хотя он не обязателен, если dragover работает, но для порядка пусть будет)
  function handleDrop(e: DragEvent, targetColId: string) {
    e.preventDefault(); // На всякий случай
    
    if (!draggedTask) return;

    const { taskId, sourceColId } = draggedTask;
    
    // Если кидаем в ту же колонку - выходим
    if (sourceColId === targetColId) {
        draggedTask = null;
        return;
    }

    // Поиск задачи для переноса
    let taskToMove: Task | undefined;
    for (const col of columns) {
        if (col.id === sourceColId) {
            // Теперь тип Task известен, ошибки не будет
            taskToMove = col.tasks.find(t => t.id === taskId);
            break;
        }
    }

    if (!taskToMove) {
        draggedTask = null;
        return;
    }

    // Атомарное обновление state
    columns = columns.map(col => {
        if (col.id === sourceColId) {
            return { ...col, tasks: col.tasks.filter(t => t.id !== taskId) };
        }
        if (col.id === targetColId) {
            return { ...col, tasks: [...col.tasks, taskToMove!] };
        }
        return col;
    });

    draggedTask = null;
  }

  // --- Редактирование ---
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
    const newTask: Task = { id: `task-${Date.now()}`, title: 'Новая задача' };
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

<svelte:window onkeydown={handleKeydown} />

<div class="flex gap-4 items-start overflow-x-auto pb-4 h-full">
  
  {#each columns as col (col.id)}
    <div 
      class="flex-shrink-0 w-72 bg-gray-200/50 rounded-xl flex flex-col max-h-full border border-transparent hover:border-gray-300 transition"
      ondragover={handleDragOver}
      ondrop={(e) => handleDrop(e, col.id)} 
    >
      <!-- Header -->
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

      <!-- Tasks List -->
      <div class="flex-1 overflow-y-auto p-2 space-y-2 min-h-[100px]">
        {#each col.tasks as task (task.id)}
          <div 
            class="bg-white p-3 rounded-lg shadow-sm border border-gray-200 cursor-grab active:cursor-grabbing group relative hover:shadow-md transition"
            draggable="true"
            ondragstart={(e) => handleDragStart(e, task.id, col.id)}
            animate:flip={{ duration: 200, easing: quintOut }}
          >
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

            <button 
              class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition text-gray-300 hover:text-red-500"
              onclick={() => deleteTask(col.id, task.id)}
            >
              <X size="12" />
            </button>
            
            <div class="absolute bottom-1 right-1 text-gray-200">
               <GripVertical size="12" />
            </div>
          </div>
        {/each}
      </div>

      <!-- Add Task Button -->
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

  <!-- Add Column Button -->
  <div class="flex-shrink-0 w-72">
    <button 
      class="w-full bg-white/50 hover:bg-white border-2 border-dashed border-gray-300 text-gray-500 font-semibold p-3 rounded-xl flex items-center justify-center transition hover:border-green-500 hover:text-green-600"
      onclick={addColumn}
    >
      <Plus size="20" class="mr-2" /> Добавить колонку
    </button>
  </div>

</div>