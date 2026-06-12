<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { authStore } from '$lib/stores/authStore.js';
  import { goto } from '$app/navigation';
  import { Bar } from 'svelte-chartjs';
  import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
  } from 'chart.js';

  ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

  let projectId = $derived($page.params.project_id);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://204.12.253.210:8078';

  // ----- состояние -----
  let projectName = $state('');
  let loadingProject = $state(true);
  let projectError = $state('');

  let activeTab = $state('description');

  let description = $state('');
  let descriptionLoading = $state(false);
  let descriptionError = $state('');

  let report = $state('');
  let reportLoading = $state(false);
  let reportError = $state('');

  let chartDataConfig = $state(null);
  let chartLoading = $state(false);
  let chartError = $state('');

  // ----- загрузка базовой информации о проекте -----
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
      const project = await res.json();
      projectName = project.name;
    } catch (e) {
      projectError = e.message;
    } finally {
      loadingProject = false;
    }
  });

  // ----- генерация описания -----
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

  // ----- генерация отчёта -----
  async function generateReport() {
    reportLoading = true;
    reportError = '';
    try {
      const res = await fetch(`${API_BASE}/report/${projectId}`, {
        method: 'POST',
        credentials: 'include'
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

  // ----- генерация графика -----
  async function generateChart() {
    chartLoading = true;
    chartError = '';
    try {
      const res = await fetch(`${API_BASE}/chart/${projectId}`, {
        method: 'POST',
        credentials: 'include'
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Ошибка генерации графика');
      }
      const data = await res.json();
      // data.chart_data = { labels, values, title, chart_type }
      if (data.chart_data) {
        const cd = data.chart_data;
        chartDataConfig = {
          labels: cd.labels,
          datasets: [{
            label: cd.title,
            data: cd.values,
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        };
      } else {
        chartError = 'Нет данных для графика';
      }
    } catch (e) {
      chartError = e.message;
    } finally {
      chartLoading = false;
    }
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
    <p class="text-gray-600 mb-6">{projectName}</p>

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
          onclick={() => activeTab = 'description'}
          class="px-4 py-2 rounded-lg font-medium transition {activeTab === 'description' ? 'bg-indigo-100 text-indigo-700' : 'bg-white text-gray-600 hover:bg-gray-50'}"
        >
          Описание
        </button>
        <button
          onclick={() => activeTab = 'report'}
          class="px-4 py-2 rounded-lg font-medium transition {activeTab === 'report' ? 'bg-indigo-100 text-indigo-700' : 'bg-white text-gray-600 hover:bg-gray-50'}"
        >
          Отчёт
        </button>
        <button
          onclick={() => activeTab = 'charts'}
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
            <button
              onclick={generateDescription}
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Сгенерировать описание
            </button>
          {:else if descriptionLoading}
            <p class="text-gray-500">Генерация описания...</p>
          {:else if descriptionError}
            <div class="bg-red-50 text-red-600 p-4 rounded-xl mb-4">{descriptionError}</div>
            <button
              onclick={generateDescription}
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Попробовать снова
            </button>
          {:else}
            <div class="prose max-w-none text-gray-700 whitespace-pre-wrap">{description}</div>
          {/if}

        {:else if activeTab === 'report'}
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Отчёт ИИ-ассистента</h2>
          {#if !report && !reportLoading}
            <p class="text-gray-500 mb-4">Отчёт ещё не сгенерирован.</p>
            <button
              onclick={generateReport}
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Сгенерировать отчёт
            </button>
          {:else if reportLoading}
            <p class="text-gray-500">Генерация отчёта...</p>
          {:else if reportError}
            <div class="bg-red-50 text-red-600 p-4 rounded-xl mb-4">{reportError}</div>
            <button
              onclick={generateReport}
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Попробовать снова
            </button>
          {:else}
            <div class="prose max-w-none text-gray-700 whitespace-pre-wrap">{report}</div>
          {/if}

                  {:else if activeTab === 'charts'}
                    <h2 class="text-xl font-semibold text-gray-800 mb-4">Графики проекта</h2>
                    {#if !chartDataConfig && !chartLoading}
                      <p class="text-gray-500 mb-4">График ещё не сгенерирован.</p>
                      <div class="flex gap-2">
                        <button
                          onclick={generateChart}
                          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                        >
                          Сгенерировать график (AI)
                        </button>
                        <button
                          onclick={() => {
                            chartDataConfig = {
                              labels: ['Backlog', 'In Progress', 'Done'],
                              datasets: [{
                                label: 'Тестовые данные',
                                data: [5, 3, 2],
                                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                                borderColor: 'rgba(75, 192, 192, 1)',
                                borderWidth: 1
                              }]
                            };
                          }}
                          class="px-4 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500"
                        >
                          Тестовый график
                        </button>
                      </div>
                    {:else if chartLoading}
                      <p class="text-gray-500">Генерация графика...</p>
                    {:else if chartError}
                      <div class="bg-red-50 text-red-600 p-4 rounded-xl mb-4">{chartError}</div>
                      <button
                        onclick={generateChart}
                        class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                      >
                        Попробовать снова
                      </button>
                    {:else}
                      <div class="w-full max-w-lg mx-auto">
                        <Bar data={chartDataConfig} options={{ responsive: true }} />
                      </div>
                      <button
                        onclick={() => chartDataConfig = null}
                        class="mt-4 text-sm text-gray-500 hover:text-gray-700"
                      >
                        Скрыть график
                      </button>
                    {/if}
                  {/if}
      </div>
    {/if}
  </div>
</div>