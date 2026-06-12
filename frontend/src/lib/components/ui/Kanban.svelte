<script lang="ts">
  import { flip } from 'svelte/animate';
  import { quintOut } from 'svelte/easing';
  import { Plus, X } from 'lucide-svelte';
  import type { Column, Task } from '$lib/data/templates';

  let {
    columns = $bindable<Column[]>(),
    projectMembers = [] as { id: string; login: string; fullname: string }[],
    assignUser = async (taskId: string, userId: string) => {},
    unassignUser = async (taskId: string, userId: string) => {},
  } = $props();

  function initFocus(node: HTMLInputElement) {
    node.focus();
    node.select();
  }

  // --- D&D Logic ---
  let draggedTask = $state<{ taskId: string; sourceColId: string } | null>(null);

  function handleDragStart(e: DragEvent, taskId: string, colId: string) {
    draggedTask = { taskId, sourceColId: colId };
    if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move';
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
  }

  function handleDrop(e: DragEvent, targetColId: string) {
    e.preventDefault();
    if (!draggedTask) return;

    const { taskId, sourceColId } = draggedTask;
    if (sourceColId === targetColId) {
      draggedTask = null;
      return;
    }

    let taskToMove: Task | undefined;
    for (const col of columns) {
      if (col.id === sourceColId) {
        taskToMove = col.tasks.find(t => t.id === taskId);
        break;
      }
    }
    if (!taskToMove) {
      draggedTask = null;
      return;
    }

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

  // --- Editing ---
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
          return {
            ...col,
            tasks: col.tasks.map(t =>
              t.id === taskId ? { ...t, title: currentText } : t
            ),
          };
        } else {
          return { ...col, name: currentText };
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
      id: crypto.randomUUID(),
      name: 'Новая колонка',
      position: columns.length,
      tasks: [],
    };
    columns = [...columns, newCol];
    setTimeout(() => startEdit(newCol.id, newCol.name), 50);
  }

  function addTask(colId: string) {
    const newTask: Task = {
      id: crypto.randomUUID(),
      title: 'Новая задача',
      column_id: colId,
      assignees: [],
    };
    columns = columns.map(col =>
      col.id === colId ? { ...col, tasks: [...col.tasks, newTask] } : col
    );
    setTimeout(() => startEdit(newTask.id, newTask.title), 50);
  }

  function deleteTask(colId: string, taskId: string) {
    columns = columns.map(col =>
      col.id === colId
        ? { ...col, tasks: col.tasks.filter(t => t.id !== taskId) }
        : col
    );
  }

  function deleteColumn(colId: string) {
    columns = columns.filter(col => col.id !== colId);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      editingId = null;
      assignModalTask = null;
    }
  }

  // --- Назначение исполнителей ---
  let assignModalTask = $state<Task | null>(null);

  function openAssignModal(task: Task) {
    assignModalTask = task;
  }

  function closeAssignModal() {
    assignModalTask = null;
  }

  function selectUser(event: Event) {
    const select = event.target as HTMLSelectElement;
    const userId = select.value;
    if (!userId || !assignModalTask) return;
    assignUser(assignModalTask.id, userId);
    closeAssignModal();
  }

  function availableMembers(task: Task) {
    if (!projectMembers) return [];
    const assignedIds = new Set((task.assignees || []).map(a => a.user_id));
    return projectMembers.filter(m => !assignedIds.has(m.id));
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="flex gap-4 items-start overflow-x-auto pb-4 h-full">
  {#each columns as col (col.id)}
    <div
      class="flex-shrink-0 w-72 bg-gray-200/50 rounded-xl flex flex-col max-h-full border border-transparent hover:border-gray-300 transition"
      role="group"
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
              ondblclick={() => startEdit(col.id, col.name)}
            >
              {col.name}
            </h3>
          {/if}

          <span class="text-xs text-gray-500 ml-2 bg-gray-200 px-1.5 py-0.5 rounded-full">
            {col.tasks.length}
          </span>

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
            role="group"
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

            <!-- Исполнители -->
            <div class="mt-2 flex flex-wrap gap-1 items-center">
              {#each task.assignees || [] as user (user.user_id)}
                <button
                  class="bg-green-100 text-green-800 px-1.5 py-0.5 rounded text-xs hover:bg-red-100 hover:text-red-800 transition"
                  title={`Убрать ${user.fullname}`}
                  onclick={(e) => {
                    e.stopPropagation();
                    unassignUser(task.id, user.user_id);
                  }}
                >
                  {user.login}
                </button>
              {/each}
              {#if projectMembers.length > 0}
                <button
                  class="text-gray-400 hover:text-gray-600 text-sm"
                  title="Назначить исполнителя"
                  onclick={(e) => {
                    e.stopPropagation();
                    openAssignModal(task);
                  }}
                >
                  <Plus size="14" />
                </button>
              {/if}
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

<!-- Модальное окно выбора исполнителя -->
{#if assignModalTask}
  <div class="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
    <div class="bg-white p-4 rounded-lg shadow w-64">
      <h4 class="font-medium mb-2">Назначить на «{assignModalTask.title}»</h4>
      {#if availableMembers(assignModalTask).length > 0}
        <select class="w-full border rounded p-1" onchange={selectUser}>
          <option value="">Выберите...</option>
          {#each availableMembers(assignModalTask) as member (member.id)}
            <option value={member.id}>{member.fullname} ({member.login})</option>
          {/each}
        </select>
      {:else}
        <p class="text-sm text-gray-500">Все участники уже назначены</p>
      {/if}
      <button
        class="mt-3 w-full text-center text-gray-500 hover:text-gray-700"
        onclick={closeAssignModal}
      >
        Отмена
      </button>
    </div>
  </div>
{/if}