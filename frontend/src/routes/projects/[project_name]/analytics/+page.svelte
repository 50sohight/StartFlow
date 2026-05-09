<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { authStore } from '$lib/stores/authStore.js';
  import { goto } from '$app/navigation';
  import { generateProjectReport } from '$lib/ai.js';
  import Button from '$lib/components/ui/Button.svelte';

  let project = null;
  let report = '';
  let loading = true;
  let error = '';

  const API_BASE = 'http://localhost:8000';

  $: projectId = $page.params.project_id;

  onMount(async () => {
    await authStore.fetchUser();
    if (!$authStore) {
      goto('/auth/login');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/projects/${projectId}`, {
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Проект не найден');
      project = await res.json();

      // Формируем документы для AI
      const docs = [];
      docs.push(`Проект: "${project.name}". Описание: ${project.description || 'нет'}`);

      for (const col of project.columns) {
        if (col.tasks && col.tasks.length > 0) {
          const taskList = col.tasks.map((t, i) => `${i + 1}. ${t.title}`).join('; ');
          docs.push(`Колонка «${col.name}»: ${taskList}`);
        } else {
          docs.push(`Колонка «${col.name}»: нет задач`);
        }
      }

      report = await generateProjectReport(docs);
    } catch (e) {
      error = e.message || 'Ошибка загрузки';
    } finally {
      loading = false;
    }
  });
</script>

<div class="min-h-screen bg-gray-50 py-8 px-4">
  <div class="max-w-4xl mx-auto">
    <div class="mb-6 flex items-center justify-between">
      <a
        href={`/projects/${projectId}/board`}
        class="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
      >
        ← Назад к доске
      </a>
    </div>

    <h1 class="text-3xl font-bold text-gray-900 mb-2">
      Аналитика проекта
    </h1>
    {#if project}
      <p class="text-gray-600 mb-8">{project.name}</p>
    {/if}

    {#if loading}
      <div class="bg-white rounded-xl shadow p-6 text-center text-gray-500">
        Загрузка аналитики...
      </div>
    {:else if error}
      <div class="bg-red-50 text-red-600 p-4 rounded-xl">{error}</div>
    {:else}
      <div class="bg-white rounded-xl shadow p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Отчёт ИИ-ассистента</h2>
        <div class="prose max-w-none text-gray-700 whitespace-pre-wrap">
          {report}
        </div>
      </div>

      <div class="bg-white rounded-xl shadow p-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Графики</h2>
        <p class="text-gray-500">
          Аналитика по графикам появится позже (Cumulative Flow Diagram, распределение задач по участникам).
        </p>
      </div>
    {/if}
  </div>
</div>