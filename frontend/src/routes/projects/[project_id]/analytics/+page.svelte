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
    BarController,
    LineController,
    BarElement,
    LineElement,
    PointElement,
    Title,
    Tooltip,
    Legend
  } from 'chart.js';

  ChartJS.register(
    CategoryScale,
    LinearScale,
    BarController,
    LineController,
    BarElement,
    LineElement,
    PointElement,
    Title,
    Tooltip,
    Legend
  );

  let projectId = $derived($page.params.project_id);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8078';

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

  // ----- состояния для графиков -----
  let burndownConfig = $state(null);
  let burndownLoading = $state(false);
  let burndownError = $state('');

  let teamLoadConfig = $state(null);
  let teamLoadLoading = $state(false);
  let teamLoadError = $state('');

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
      const res = await fetch(`${API_BASE}/statement/${projectId}`, {
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

  // ----- загрузка Burndown -----
  async function loadBurndown() {
    burndownLoading = true;
    burndownError = '';
    try {
      const [ideal, actual] = await Promise.all([
        fetch(`${API_BASE}/charts/burndown/${projectId}/ideal`, { credentials: 'include' }).then(r => {
          if (!r.ok) throw new Error(`Ideal: ${r.status}`);
          return r.json();
        }),
        fetch(`${API_BASE}/charts/burndown/${projectId}/actual`, { credentials: 'include' }).then(r => {
          if (!r.ok) throw new Error(`Actual: ${r.status}`);
          return r.json();
        })
      ]);

      // Собираем все даты, сортируем
      const allDates = [...new Set([
        ...ideal.map(d => d.date),
        ...actual.map(d => d.date)
      ])].sort();

      const idealMap = Object.fromEntries(ideal.map(d => [d.date, d.count]));
      const actualMap = Object.fromEntries(actual.map(d => [d.date, d.count]));

      burndownConfig = {
        labels: allDates,
        datasets: [
          {
            type: 'line',
            label: 'Идеальный план (кумулятивно)',
            data: allDates.map(d => idealMap[d] ?? null),
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.2,
            fill: false,
            pointRadius: 4,
          },
          {
            type: 'bar',
            label: 'Выполнено за день',
            data: allDates.map(d => actualMap[d] ?? 0),
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
          }
        ]
      };
    } catch (e) {
      burndownError = e.message;
      burndownConfig = null;
    } finally {
      burndownLoading = false;
    }
  }

  // ----- загрузка Team Load -----
  async function loadTeamLoad() {
    teamLoadLoading = true;
    teamLoadError = '';
    try {
      const [done, assigned] = await Promise.all([
        fetch(`${API_BASE}/charts/teamload/${projectId}/done`, { credentials: 'include' }).then(r => {
          if (!r.ok) throw new Error(`Done: ${r.status}`);
          return r.json();
        }),
        fetch(`${API_BASE}/charts/teamload/${projectId}/assigned`, { credentials: 'include' }).then(r => {
          if (!r.ok) throw new Error(`Assigned: ${r.status}`);
          return r.json();
        })
      ]);

      // Уникальный список пользователей с сохранением порядка
      const userMap = new Map();
      for (const u of [...done, ...assigned]) {
        if (!userMap.has(u.user_id)) {
          userMap.set(u.user_id, { id: u.user_id, login: u.login, fullname: u.fullname });
        }
      }
      const allUsers = Array.from(userMap.values());

      const doneMap = Object.fromEntries(done.map(u => [u.user_id, u.count]));
      const assignedMap = Object.fromEntries(assigned.map(u => [u.user_id, u.count]));

      teamLoadConfig = {
        labels: allUsers.map(u => u.fullname || u.login),
        datasets: [
          {
            label: 'Завершённые задачи',
            data: allUsers.map(u => doneMap[u.id] ?? 0),
            backgroundColor: 'rgba(75, 192, 192, 0.7)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
          },
          {
            label: 'Задачи в работе',
            data: allUsers.map(u => assignedMap[u.id] ?? 0),
            backgroundColor: 'rgba(144, 238, 144, 0.7)',
            borderColor: 'rgba(144, 238, 144, 1)',
            borderWidth: 1,
          }
        ]
      };
    } catch (e) {
      teamLoadError = e.message;
      teamLoadConfig = null;
    } finally {
      teamLoadLoading = false;
    }
  }

  // Автоматически загружаем графики при переходе на вкладку
  $effect(() => {
    if (activeTab === 'charts') {
      if (!burndownConfig && !burndownLoading) loadBurndown();
      if (!teamLoadConfig && !teamLoadLoading) loadTeamLoad();
    }
  });
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
          class="px-4 py-2 rounded-lg font-medium transition {activeTab === 'description' ? 'bg-green-100 text-green-700' : 'bg-white text-gray-600 hover:bg-gray-50'}"
        >
          Описание
        </button>
        <button
          onclick={() => activeTab = 'report'}
          class="px-4 py-2 rounded-lg font-medium transition {activeTab === 'report' ? 'bg-green-100 text-green-700' : 'bg-white text-gray-600 hover:bg-gray-50'}"
        >
          Отчёт
        </button>
        <button
          onclick={() => activeTab = 'charts'}
          class="px-4 py-2 rounded-lg font-medium transition {activeTab === 'charts' ? 'bg-green-100 text-green-700' : 'bg-white text-gray-600 hover:bg-gray-50'}"
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
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Сгенерировать описание
            </button>
          {:else if descriptionLoading}
            <p class="text-gray-500">Генерация описания...</p>
          {:else if descriptionError}
            <div class="bg-red-50 text-red-600 p-4 rounded-xl mb-4">{descriptionError}</div>
            <button
              onclick={generateDescription}
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
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
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Сгенерировать отчёт
            </button>
          {:else if reportLoading}
            <p class="text-gray-500">Генерация отчёта...</p>
          {:else if reportError}
            <div class="bg-red-50 text-red-600 p-4 rounded-xl mb-4">{reportError}</div>
            <button
              onclick={generateReport}
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Попробовать снова
            </button>
          {:else}
            <div class="prose max-w-none text-gray-700 whitespace-pre-wrap">{report}</div>
          {/if}

        {:else if activeTab === 'charts'}
          <h2 class="text-xl font-semibold text-gray-800 mb-6">Графики проекта</h2>

          <!-- Burndown Chart -->
          <div class="mb-10">
            <h3 class="text-lg font-medium text-gray-700 mb-3">Динамика выполнения задач (Burndown)</h3>
            {#if burndownLoading}
              <p class="text-gray-500">Загрузка графика Burndown...</p>
            {:else if burndownError}
              <div class="bg-red-50 text-red-600 p-4 rounded-xl mb-4">
                Ошибка загрузки Burndown: {burndownError}
                <button
                  onclick={loadBurndown}
                  class="ml-4 underline text-red-700 hover:text-red-800"
                >
                  Повторить
                </button>
              </div>
            {:else if burndownConfig}
              <div class="w-full max-w-3xl mx-auto bg-white p-4 rounded-lg shadow-sm border">
                <Bar data={burndownConfig} options={{ 
                  responsive: true,
                  plugins: { legend: { position: 'bottom' } },
                  scales: {
                    x: { title: { display: true, text: 'Дата' } },
                    y: { title: { display: true, text: 'Количество задач' } }
                  }
                }} />
              </div>
            {:else}
              <p class="text-gray-500">Нет данных для графика Burndown</p>
            {/if}
          </div>

          <!-- Team Load Chart -->
          <div>
            <h3 class="text-lg font-medium text-gray-700 mb-3">Загрузка участников</h3>
            {#if teamLoadLoading}
              <p class="text-gray-500">Загрузка графика загрузки команды...</p>
            {:else if teamLoadError}
              <div class="bg-red-50 text-red-600 p-4 rounded-xl mb-4">
                Ошибка загрузки Team Load: {teamLoadError}
                <button
                  onclick={loadTeamLoad}
                  class="ml-4 underline text-red-700 hover:text-red-800"
                >
                  Повторить
                </button>
              </div>
            {:else if teamLoadConfig}
              <div class="w-full max-w-2xl mx-auto bg-white p-4 rounded-lg shadow-sm border">
                <Bar data={teamLoadConfig} options={{ 
                  indexAxis: 'y',   // горизонтальные столбцы
                  responsive: true,
                  plugins: { legend: { position: 'bottom' } },
                  scales: {
                    x: { 
                      title: { display: true, text: 'Количество задач' },
                      ticks: { stepSize: 1 }
                    },
                    y: { title: { display: true, text: 'Участник' } }
                  }
                }} />
              </div>
            {:else}
              <p class="text-gray-500">Нет данных о загрузке команды</p>
            {/if}
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>