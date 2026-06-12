<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import KanbanBoard from '$lib/components/ui/Kanban.svelte';
  import { goto } from '$app/navigation';
  import type { Column, Task } from '$lib/data/templates';

  let projectId = $derived($page.params.project_id);
  const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8078';

  // ----- состояние колонок и задач -----
  let columns = $state<Column[]>([]);
  let initialColumns = $state<Column[]>([]);
  let projectName = $state('');
  let loading = $state(true);
  let saving = $state(false);
  let error = $state<string | null>(null);
  let unsavedChanges = $derived(JSON.stringify(columns) !== JSON.stringify(initialColumns));

  // ----- состояние для назначений -----
  let projectMembers: { id: string; login: string; fullname: string }[] = $state([]);
  // Мапа task_id -> массив исполнителей
  let assignments = $state<Record<string, { user_id: string; login: string; fullname: string }[]>>({});

  // ----- инвайт -----
  let inviteToken = $state('');
  let showInvite = $state(false);
  let copied = $state(false);
  let inviteError = $state('');

  // ===================== Загрузка данных =====================
  async function loadProject() {
    loading = true;
    error = null;
    try {
      const res = await fetch(`${BASE_URL}/projects/${projectId}`, { credentials: 'include' });
      if (!res.ok) throw new Error(`Ошибка ${res.status}`);
      const project = await res.json();
      projectName = project.name;
      columns = project.columns.map((col: any) => ({
        id: col.id,
        name: col.name,
        position: col.position,
        tasks: col.tasks.map((task: any) => ({
          id: task.id,
          title: task.title,
          description: task.description,
          deadline: task.deadline,
          column_id: task.column_id,
          project_id: task.project_id,
          assignees: [], // заполним позже
        })),
      }));
      await loadAssignmentsAndMembers();
      initialColumns = $state.snapshot(columns);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function loadMembers() {
    try {
      const res = await fetch(`${BASE_URL}/projects/${projectId}/members`, { credentials: 'include' });
      if (res.ok) {
        const membersRaw = await res.json(); // [{ user: { id, login, fullname } }, ...]
        projectMembers = membersRaw.map((m: any) => ({
          id: m.user.id,
          login: m.user.login,
          fullname: m.user.fullname,
        }));
      }
    } catch (e) {
      console.error('Ошибка загрузки участников', e);
    }
  }

  async function loadAssignmentsAndMembers() {
    await loadMembers();
    try {
      const res = await fetch(`${BASE_URL}/projects/${projectId}/assignments`, { credentials: 'include' });
      if (res.ok) {
        const data = await res.json(); // массив { task_id, user_id, login, fullname }
        const grouped: Record<string, any[]> = {};
        for (const a of data) {
          if (!grouped[a.task_id]) grouped[a.task_id] = [];
          grouped[a.task_id].push({ user_id: a.user_id, login: a.login, fullname: a.fullname });
        }
        // применить назначения к задачам
        columns = columns.map(col => ({
          ...col,
          tasks: col.tasks.map(task => ({
            ...task,
            assignees: grouped[task.id] || [],
          })),
        }));
        assignments = grouped;
      }
    } catch (e) {
      console.error('Ошибка загрузки назначений', e);
    }
  }

  // ===================== Назначение / снятие =====================
  async function assignUser(taskId: string, userId: string) {
    try {
      const res = await fetch(`${BASE_URL}/tasks/${taskId}/assign?user_id=${userId}`, {
        method: 'POST',
        credentials: 'include',
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Ошибка назначения');
      }
      // Оптимистичное обновление UI
      const user = projectMembers.find(m => m.id === userId);
      if (user) {
        columns = columns.map(col => ({
          ...col,
          tasks: col.tasks.map(task => {
            if (task.id !== taskId) return task;
            const already = task.assignees.some(a => a.user_id === userId);
            if (already) return task;
            return {
              ...task,
              assignees: [...task.assignees, { user_id: user.id, login: user.login, fullname: user.fullname }],
            };
          }),
        }));
      }
    } catch (e: any) {
      error = e.message;
    }
  }

  async function unassignUser(taskId: string, userId: string) {
    try {
      const res = await fetch(`${BASE_URL}/tasks/${taskId}/unassign?user_id=${userId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Ошибка снятия');
      }
      // Оптимистичное обновление
      columns = columns.map(col => ({
        ...col,
        tasks: col.tasks.map(task => {
          if (task.id !== taskId) return task;
          return {
            ...task,
            assignees: task.assignees.filter(a => a.user_id !== userId),
          };
        }),
      }));
    } catch (e: any) {
      error = e.message;
    }
  }

  // ===================== Сохранение доски =====================
  async function save() {
    if (saving) return;
    saving = true;
    error = null;
    try {
      // Удаление колонок
      const initialIds = new Set(initialColumns.map(c => c.id));
      const currentIds = new Set(columns.map(c => c.id));
      for (const col of initialColumns) {
        if (!currentIds.has(col.id)) {
          await fetch(`${BASE_URL}/columns/${col.id}`, { method: 'DELETE', credentials: 'include' });
        }
      }
      // Создание/обновление колонок
      for (const col of columns) {
        const isNew = col.id.startsWith('temp-') || !initialIds.has(col.id);
        if (isNew) {
          const res = await fetch(`${BASE_URL}/columns`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
              project_id: projectId,
              name: col.name,
              position: col.position,
            }),
          });
          if (!res.ok) throw new Error('Не удалось создать колонку');
          const created = await res.json();
          col.id = created.id;
        } else {
          const initial = initialColumns.find(c => c.id === col.id);
          if (initial && (initial.name !== col.name || initial.position !== col.position)) {
            await fetch(`${BASE_URL}/columns/${col.id}`, {
              method: 'PATCH',
              headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
              body: JSON.stringify({ name: col.name, position: col.position }),
            });
          }
        }
      }

      // Задачи: собираем текущее состояние
      const currentTasks: { task: Task; columnId: string }[] = [];
      for (const col of columns) {
        for (const task of col.tasks) {
          currentTasks.push({ task, columnId: col.id });
        }
      }
      const initialTasks = new Map<string, Task>();
      for (const col of initialColumns) {
        for (const t of col.tasks) {
          initialTasks.set(t.id, t);
        }
      }
      const currentTaskIds = new Set(currentTasks.map(t => t.task.id));

      // Удаление задач
      for (const [id, task] of initialTasks) {
        if (!currentTaskIds.has(id)) {
          await fetch(`${BASE_URL}/tasks/${id}`, { method: 'DELETE', credentials: 'include' });
        }
      }

      // Создание/обновление задач
      for (const { task, columnId } of currentTasks) {
        const isNew = task.id.startsWith('temp-') || !initialTasks.has(task.id);
        if (isNew) {
          const res = await fetch(`${BASE_URL}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
              title: task.title,
              description: task.description || '',
              deadline: task.deadline || new Date().toISOString(),
              project_id: projectId,
              column_id: columnId,
            }),
          });
          if (!res.ok) throw new Error('Не удалось создать задачу');
          const created = await res.json();
          task.id = created.id;
        } else {
          const initial = initialTasks.get(task.id);
          if (initial) {
            const changes: any = {};
            if (initial.title !== task.title) changes.title = task.title;
            if (initial.description !== task.description) changes.description = task.description;
            if (initial.deadline !== task.deadline) changes.deadline = task.deadline;
            if (initial.column_id !== columnId) changes.column_id = columnId;
            if (Object.keys(changes).length > 0) {
              await fetch(`${BASE_URL}/tasks/${task.id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(changes),
              });
            }
          }
        }
      }

      await loadProject(); // перезагрузить для актуализации
    } catch (e: any) {
      error = e.message;
    } finally {
      saving = false;
    }
  }

  // ===================== Приглашения =====================
  async function generateInviteLink() {
    inviteError = '';
    try {
      const res = await fetch(`${BASE_URL}/link/generate_link/${projectId}`, {
        method: 'POST',
        credentials: 'include',
      });
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || `Ошибка ${res.status}`);
      }
      inviteToken = await res.text();
      showInvite = true;
      copied = false;
    } catch (e: any) {
      inviteError = e.message;
    }
  }

  async function copyLink() {
    const joinUrl = inviteToken;
    try {
      await navigator.clipboard.writeText(joinUrl);
      copied = true;
      setTimeout(() => copied = false, 2000);
    } catch {
      const input = document.createElement('input');
      input.value = joinUrl;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      copied = true;
      setTimeout(() => copied = false, 2000);
    }
  }

  onMount(loadProject);
</script>

<div class="p-4 md:p-6 bg-gray-100 h-[calc(100vh-64px)] overflow-auto flex flex-col">
  <!-- Шапка -->
  <div class="mb-4 flex items-center gap-4 flex-wrap border-b border-gray-200 pb-4">
    <h1 class="text-2xl font-bold text-gray-800">{projectName}</h1>
    <div class="flex gap-2 ml-auto">
      {#if unsavedChanges}
        <span class="text-sm text-amber-600 bg-amber-50 px-3 py-1 rounded-full self-center">
          Есть несохранённые изменения
        </span>
      {/if}
      <button
        class="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition"
        onclick={() => goto(`/projects/${projectId}/analytics`)}
      >
        Аналитика
      </button>
      <button
        class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
        onclick={save}
        disabled={saving || !unsavedChanges}
      >
        {saving ? 'Сохранение...' : 'Сохранить'}
      </button>
      <button
        class="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
        onclick={generateInviteLink}
      >
        Пригласить
      </button>
    </div>
  </div>

  <!-- Модалка приглашения -->
  {#if showInvite}
    <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-3">Ссылка для приглашения</h3>
        <p class="text-sm text-gray-500 mb-4">
          Отправьте эту ссылку участнику, чтобы он присоединился к проекту.
        </p>
        <div class="flex items-center gap-2">
          <input
            readonly
            value={inviteToken.replace(/^["']|["']$/g, '')}
            class="flex-1 px-3 py-2 border border-gray-300 rounded bg-gray-50 text-sm"
          />
          <button
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onclick={copyLink}
          >
            {copied ? 'Скопировано' : 'Копировать'}
          </button>
        </div>
        {#if inviteError}
          <p class="text-red-500 text-sm mt-2">{inviteError}</p>
        {/if}
        <button
          class="mt-4 text-gray-500 hover:text-gray-700"
          onclick={() => { showInvite = false; inviteToken = ''; }}
        >
          Закрыть
        </button>
      </div>
    </div>
  {/if}

  {#if error}
    <div class="mb-4 p-3 bg-red-100 border border-red-300 text-red-800 rounded-lg">
      {error}
      <button class="ml-2 underline" onclick={() => error = null}>✕</button>
    </div>
  {/if}

  {#if loading}
    <div class="flex-1 flex items-center justify-center text-gray-500">Загрузка...</div>
  {:else}
    <KanbanBoard
      bind:columns
      projectMembers={projectMembers}
      {assignUser}
      {unassignUser}
    />
  {/if}
</div>