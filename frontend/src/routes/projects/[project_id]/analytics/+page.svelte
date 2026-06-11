<!-- Очевидно я не могу обратиться к модели потому что CORS 
 и протестить функционал не могу -->

<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { authStore } from '$lib/stores/authStore.js';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';

  // ----- состояние -----
  let project = $state(null);            // данные проекта
  let activeTab = $state('description'); // текущая вкладка

  let description = $state('');
  let descriptionLoading = $state(false);
  let descriptionError = $state('');

  let report = $state('');
  let reportLoading = $state(false);
  let reportError = $state('');

  let chartData = $state(null);          // { labels, values, title, chart_type }
  let chartLoading = $state(false);

  let loadingProject = $state(true);
  let projectError = $state('');

  // ID проекта – в реальном приложении брать из $page.params.project_id
  const projectId = '513b1268-5907-43a2-9c09-7bd75ee3c345';

  // Базовый URL локального API (прокси)
  const API_BASE = 'http://localhost:8080';
  // URL AI‑сервиса (для прямых вызовов из фронта – только для отладки)
  const AI_BASE = 'http://204.12.253.210:8077';

  // ----- загрузка проекта -----
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
    } catch (e) {
      projectError = e.message;
    } finally {
      loadingProject = false;
    }
  });

  // ----- генерация описания (через бэкенд-прокси) -----
  async function generateDescription() {
    descriptionLoading = true;
    descriptionError = '';
    try {
      const res = await fetch(`${API_BASE}/description/${projectId}`, {
        method: 'POST',
        credentials: 'include'
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Ошибка генерации описания');
      }
      const data = await res.json();
      description = data.text_response || 'Пустой ответ от модели';
    } catch (e) {
      descriptionError = e.message;
    } finally {
      descriptionLoading = false;
    }
  }

  // ----- вспомогательная функция: превращаем проект в InfoForGenerate -----
  function buildInfoForGenerate(project) {
    // Задачи лежат внутри колонок – собираем в плоский список
    const tasks = [];
    if (project.columns) {
      for (const col of project.columns) {
        if (col.tasks) {
          tasks.push(...col.tasks);
        }
      }
    }
    // Приводим к формату TaskRead (поля должны совпадать)
    const mappedTasks = tasks.map(t => ({
      title: t.title,
      description: t.description || '',
      deadline: t.deadline,
      project_id: t.project_id,
      column_id: t.column_id,
      id: t.id,
      created_at: t.created_at,
      updated_at: t.updated_at
    }));

    return {
      name: project.name,
      description: project.description || null,
      status: project.status,
      created_at: project.created_at,
      updated_at: project.updated_at,
      tasks: mappedTasks
    };
  }

  // ----- генерация отчёта (вызов AI напрямую, временно) -----
  async function generateReport() {
    if (!project) return;
    reportLoading = true;
    reportError = '';
    try {
      const payload = {
        documents: buildInfoForGenerate(project),
        temperature: 0.3,
        top_k: 40,
        max_tokens: 2048
      };
      const res = await fetch(`${AI_BASE}/ai/generate/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Ошибка генерации отчёта');
      }
      const data = await res.json();
      report = data.text_response || 'Пустой ответ';
    } catch (e) {
      reportError = e.message;
    } finally {
      reportLoading = false;
    }
  }

  // ----- (опционально) загрузка данных для графика -----
  async function loadChart() {
    // В будущем можно запросить chart_data у AI‑сервиса,
    // передав response_type: 'chart'. Пока заглушка.
    chartLoading = true;
    // ... вызов endpoint, который вернёт { chart_data: ... }
    chartLoading = false;
  }

  // ----- переключение вкладок -----
  function switchTab(tab) {
    activeTab = tab;
    // При переключении на графики можно дёрнуть loadChart(), если нужно
    if (tab === 'charts' && !chartData) loadChart();
  }
</script>

<div class="min-h-screen bg-gray-50 py-8 px-4">
  <div class="max-w-4xl mx-auto">
    <!-- Шапка -->
    <div class="mb-6 flex items-center justify-between">
      <a
        href={`/projects/${projectId}/board`}
        class="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
      >
        ← Назад к доске
      </a>
    </div>

    <h1 class="text-3xl font-bold text-gray-900 mb-2">Аналитика проекта</h1>
    {#if project}
      <p class="text-gray-600 mb-6">{project.name}</p>
    {/if}

    {#if loadingProject}
      <div class="bg-white rounded-xl shadow p-6 text-center text-gray-500">
        Загрузка проекта...
      </div>
    {:else if projectError}
      <div class="bg-red-50 text-red-600 p-4 rounded-xl">{projectError}</div>
    {:else}
      <!-- Переключатель вкладок -->
      <div class="flex space-x-2 mb-8">
        <button
          onclick={() => switchTab('description')}
          class="px-4 py-2 rounded-lg font-medium transition {activeTab === 'description' ? 'bg-indigo-100 text-indigo-700' : 'bg-white text-gray-600 hover:bg-gray-50'}"
        >
          Описание
        </button>
        <button
          onclick={() => switchTab('report')}
          class="px-4 py-2 rounded-lg font-medium transition {activeTab === 'report' ? 'bg-indigo-100 text-indigo-700' : 'bg-white text-gray-600 hover:bg-gray-50'}"
        >
          Отчёт
        </button>
        <button
          onclick={() => switchTab('charts')}
          class="px-4 py-2 rounded-lg font-medium transition {activeTab === 'charts' ? 'bg-indigo-100 text-indigo-700' : 'bg-white text-gray-600 hover:bg-gray-50'}"
        >
          Графики
        </button>
      </div>

      <!-- Содержимое вкладок -->
      <div class="bg-white rounded-xl shadow p-6">
        {#if activeTab === 'description'}
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Описание проекта</h2>
          {#if !description && !descriptionLoading}
            <p class="text-gray-500 mb-4">Описание ещё не сгенерировано.</p>
            <Button on:click={generateDescription}>
              Сгенерировать описание
            </Button>
          {:else if descriptionLoading}
            <p class="text-gray-500">Генерация описания...</p>
          {:else if descriptionError}
            <div class="bg-red-50 text-red-600 p-4 rounded-xl mb-4">{descriptionError}</div>
          {:else}
            <div class="prose max-w-none text-gray-700 whitespace-pre-wrap">{description}</div>
          {/if}

        {:else if activeTab === 'report'}
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Отчёт ИИ-ассистента</h2>
          {#if !report && !reportLoading}
            <p class="text-gray-500 mb-4">Отчёт ещё не сгенерирован.</p>
            <Button on:click={generateReport}>
              Сгенерировать отчёт
            </Button>
          {:else if reportLoading}
            <p class="text-gray-500">Генерация отчёта...</p>
          {:else if reportError}
            <div class="bg-red-50 text-red-600 p-4 rounded-xl mb-4">{reportError}</div>
          {:else}
            <div class="prose max-w-none text-gray-700 whitespace-pre-wrap">{report}</div>
          {/if}

        {:else if activeTab === 'charts'}
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Графики</h2>
          {#if chartData}
            <!-- Здесь можно вставить компонент графика (Chart.js и т.п.) -->
            <p>Тип: {chartData.chart_type}</p>
            <pre>{JSON.stringify(chartData, null, 2)}</pre>
          {:else}
            <p class="text-gray-500">
              Графики станут доступны после запроса к аналитическому модулю.
            </p>
          {/if}
        {/if}
      </div>
    {/if}
  </div>
</div>