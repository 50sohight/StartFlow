<script>
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/authStore.js';
  import { goto } from '$app/navigation';
  import { allTemplates } from '$lib/data/templates.js';
  import Button from '$lib/components/ui/Button.svelte';
  import TemplateCard from '$lib/components/TemplateCard.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';

  let templates = $state([]);
    onMount(() => {
      const unsubscribe = allTemplates.subscribe(value => {
        templates = value;
      });
      return unsubscribe;
    });

  let name = $state('');
  let description = $state('');
  let selectedTemplate = $derived(templates.find(t => t.id === 'empty') || templates[0]);
  let loading = $state(false);
  let error = $state('');
  let showSuccess = $state(false);
  let inviteCode = $state('');

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8078';

  onMount(async () => {
    await authStore.fetchUser();
    if (!$authStore) {
      goto('/auth/login');
    }
  });

  function selectTemplate(tpl) {
    selectedTemplate = tpl;   // теперь реактивно
  }

  async function createProject() {
    if (!name.trim()) return;
    loading = true;           // теперь реактивно
    error = '';

    try {
      // 1. Создать проект
      const projRes = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim(),
          status: 'активный'
        })
      });
      if (!projRes.ok) throw new Error('Не удалось создать проект');
      const project = await projRes.json();
      const projectId = project.id;

      // 2. Создать колонки и задачи по шаблону
      if (selectedTemplate.columns.length > 0) {
        for (const [index, colTemplate] of selectedTemplate.columns.entries()) {
          const colRes = await fetch(`${API_BASE}/columns`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
              project_id: projectId,
              name: colTemplate.name,
              position: index
            })
          });
          if (!colRes.ok) throw new Error('Ошибка создания колонки');
          const column = await colRes.json();

          for (const task of colTemplate.tasks) {
            await fetch(`${API_BASE}/tasks`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
              body: JSON.stringify({
                title: task.title,
                description: '',
                deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
                project_id: projectId,
                column_id: column.id
              })
            });
          }
        }
      }

      // 3. Сгенерировать пригласительный код
      const linkRes = await fetch(`${API_BASE}/link/generate_link/${projectId}`, {
        method: 'POST',
        credentials: 'include'
      });
      if (!linkRes.ok) throw new Error('Не удалось сгенерировать ссылку');
      const linkData = await linkRes.json();
      inviteCode = linkData;


      showSuccess = true;     // реактивно
    } catch (e) {
      error = e.message || 'Произошла ошибка';
    } finally {
      loading = false;        // реактивно
    }
  }

  function closeSuccess() {
    showSuccess = false;
  }

  function goToProjects() {
    goto('/projects');
  }
</script>

<div class="min-h-screen bg-gray-50 py-10 px-4">
  <div class="max-w-4xl mx-auto bg-white rounded-2xl shadow p-6 md:p-8">
    <a href="/project_hub" class="text-sm text-gray-500 hover:text-gray-700 mb-4 inline-block">
      ← Назад
    </a>
    <h1 class="text-3xl font-bold text-gray-900 mb-6">Новый проект</h1>

    {#if error}
      <div class="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>
    {/if}

    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-1">Название проекта *</label>
      <input
        type="text"
        bind:value={name}
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 outline-none"
        placeholder="Мой проект"
      />
    </div>
    <div class="mb-8">
      <label class="block text-sm font-medium text-gray-700 mb-1">Описание</label>
      <textarea
        bind:value={description}
        rows="3"
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 outline-none"
        placeholder="Краткое описание..."
      ></textarea>
    </div>

    <h2 class="text-lg font-semibold text-gray-800 mb-3">Выберите шаблон</h2>
      <button
          onclick={() => goto('/create_template')}
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          + Новый шаблон
      </button>
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-8">
      {#each templates as tpl (tpl.id)}
        <TemplateCard
          template={tpl}
          selected={selectedTemplate.id === tpl.id}
          onSelect={selectTemplate}
        />
      {/each}
    </div>

    <div class="flex justify-end">
    <button
      type="button"
      onclick={createProject}
      disabled={!name.trim() || loading}
      class="inline-flex items-center justify-center px-6 py-3 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition"
    >
      {#if loading}
        Создание...
      {:else}
        Создать проект
      {/if}
    </button>
    </div>
  </div>
</div>

<Modal show={showSuccess} onClose={closeSuccess}>
  <div class="text-center">
    <h2 class="text-xl font-bold text-green-700 mb-2">Проект успешно создан!</h2>
    <p class="text-gray-600 mb-4">
      Код приглашения для участников:
    </p>
    <div class="bg-gray-100 p-3 rounded-lg font-mono text-sm break-all select-all">
      {inviteCode}
    </div>
    <div class="mt-4 flex gap-3 justify-center">
      <button
        onclick={() => navigator.clipboard.writeText(inviteCode)}
        class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
      >
        Скопировать
      </button>
      <button
        onclick={goToProjects}
        class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
      >
        К списку проектов
      </button>
    </div>
  </div>
</Modal>