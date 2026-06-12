<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';          // reactive page object (rune)
  import KanbanBoard from '$lib/components/ui/Kanban.svelte';
  import { goto } from '$app/navigation';
  import type { Column, Task } from '$lib/data/templates';

  let projectId = page.params.project_id;    // derived from rune, no $ needed
  const BASE_URL = 'http://localhost:8078';

  let columns = $state<Column[]>([]);
  let initialColumns = $state<Column[]>([]);
  let projectName = $state('');
  let loading = $state(true);
  let saving = $state(false);
  let error = $state<string | null>(null);
  let unsavedChanges = $derived(JSON.stringify(columns) !== JSON.stringify(initialColumns));
  let inviteToken = $state('');
  let showInvite = $state(false);
  let copied = $state(false);
  let inviteError = $state('');

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
      // Эндпоинт возвращает только строку токена, не JSON
      inviteToken = await res.text();
      showInvite = true;
      copied = false;
    } catch (e: any) {
      inviteError = e.message;
    }
  }

  async function copyLink() {
    const joinUrl = `${window.location.origin}/join?code=${inviteToken}`;
    try {
      await navigator.clipboard.writeText(joinUrl);
      copied = true;
      setTimeout(() => copied = false, 2000);
    } catch {
      // fallback для старых браузеров
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

  async function loadProject() {
    loading = true;
    error = null;
    try {
      const res = await fetch(`${BASE_URL}/projects/${projectId}`, {
        credentials: 'include',
      });
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
        })),
      }));
      initialColumns = $state.snapshot(columns);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(loadProject);

  async function save() {
    if (saving) return;
    saving = true;
    error = null;
    try {
      // Columns
      const initialIds = new Set(initialColumns.map(c => c.id));
      const currentIds = new Set(columns.map(c => c.id));

      for (const col of initialColumns) {
        if (!currentIds.has(col.id)) {
          await fetch(`${BASE_URL}/columns/${col.id}`, { method: 'DELETE', credentials: 'include' });
        }
      }

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

      // Tasks
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

      for (const [id, task] of initialTasks) {
        if (!currentTaskIds.has(id)) {
          await fetch(`${BASE_URL}/tasks/${id}`, { method: 'DELETE', credentials: 'include' });
        }
      }

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

      await loadProject();    // reload clean state
    } catch (e: any) {
      error = e.message;
    } finally {
      saving = false;
    }
  }
</script>

<div class="p-4 md:p-6 bg-gray-100 h-[calc(100vh-64px)] overflow-auto flex flex-col">
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
            value={`${window.location.origin}/join?code=${inviteToken}`}
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
    <KanbanBoard bind:columns />
  {/if}
</div>