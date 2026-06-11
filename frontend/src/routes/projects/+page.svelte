<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { useInviteLink } from '$lib/joinProject';

  let projects = $state([]);
  let loading = $state(true);
  let error = $state('');

  // 🆕 Join form state
  let joinCode = $state('');
  let joinMessage = $state('');
  let joinMessageType = $state(''); // 'success' | 'error'
  let showJoinForm = $state(false);

  onMount(async () => {
    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

      const res = await fetch(`${API_BASE_URL}/users/my_projects`, {
      credentials: 'include'
    });
      if (!res.ok) throw new Error('Ошибка загрузки проектов');
      projects = await res.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  function openProject(project) {
    goto(`/projects/${encodeURIComponent(project.id)}/board`);
  }

  async function handleJoin() {
    const result = await useInviteLink(joinCode);
    if (result.ok) {
      joinMessage = 'Вы успешно присоединились к проекту!';
      joinMessageType = 'success';
      setTimeout(() => window.location.reload(), 1500);
    } else {
      joinMessage = result.message;
      joinMessageType = 'error';
    }
  }
</script>

<div class="min-h-[calc(100vh-64px)] flex flex-col lg:flex-row">
  <!-- Основная часть -->
  <div class="w-full lg:w-1/2 flex flex-col justify-center py-12 px-6 lg:px-20 xl:px-24">
    <div class="max-w-md mx-auto w-full">
      <a href="/" class="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-8">
        ← На главную
      </a>
      <h2 class="text-3xl font-bold text-gray-900">Мои проекты</h2>
      <p class="mt-2 text-gray-600">Проекты, в которых вы участвуете.</p>

      <div class="mt-8">
        {#if loading}
          <div class="text-center py-12 text-gray-500">Загрузка...</div>
        {:else if error}
          <div class="bg-red-50 text-red-600 p-4 rounded-lg text-sm">{error}</div>
        {:else if projects.length === 0}
          <div class="text-center py-12">
            <p class="text-gray-800 font-medium text-lg mb-4">Нет активных проектов</p>
            <a
              href="/create_new_project"
              class="inline-block py-3 px-6 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition shadow-md mb-3"
            >
              Создать проект
            </a>

            <!-- 🆕 Присоединиться (показываем форму) -->
            {#if !showJoinForm}
              <button
                onclick={() => showJoinForm = true}
                class="block w-full py-3 px-6 border border-green-600 text-green-600 font-semibold rounded-lg hover:bg-green-50 transition"
              >
                Присоединиться
              </button>
            {:else}
              <div class="mt-4 bg-gray-50 p-4 rounded-lg text-left">
                <label for="joinCode" class="block text-sm text-gray-600 mb-1">Код приглашения</label>
                <input
                  id="joinCode"
                  type="text"
                  bind:value={joinCode}
                  placeholder="например, a1b2c3d4..."
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 outline-none"
                />
                <div class="mt-3 flex gap-2">
                  <button
                    onclick={handleJoin}
                    class="flex-1 py-2 px-4 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition"
                  >
                    Присоединиться
                  </button>
                  <button
                    onclick={() => { showJoinForm = false; joinMessage = ''; }}
                    class="py-2 px-4 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition"
                  >
                    Отмена
                  </button>
                </div>
                {#if joinMessage}
                  <div
                    class={`mt-3 p-2 rounded text-sm ${joinMessageType === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'}`}
                  >
                    {joinMessage}
                  </div>
                {/if}
              </div>
            {/if}
          </div>
        {:else}
          <div class="grid grid-cols-1 gap-4">
            {#each projects as project}
              <button
                onclick={() => openProject(project)}
                class="text-left bg-white rounded-xl shadow-md p-5 border border-gray-100 hover:border-green-300 transition hover:shadow-lg focus:outline-none"
              >
                <h3 class="text-lg font-semibold text-gray-900">{project.name}</h3>
                {#if project.description}
                  <p class="text-sm text-gray-600 mt-1 line-clamp-2">{project.description}</p>
                {/if}
                <div class="flex gap-4 mt-3 text-xs text-gray-500">
                  <span>{project.tasks?.length ?? 0} задач(и)</span>
                  <span>{project.members?.length ?? 0} участников</span>
                </div>
              </button>
            {/each}
          </div>
        {/if}

        {#if !loading && !error && projects.length > 0}
          <div class="mt-8 border-t pt-6">
            <a
              href="/create_new_project"
              class="w-full inline-flex items-center justify-center py-3 px-6 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition shadow-md"
            >
              Создать проект
            </a>
          </div>
        {/if}
    </div>
  </div>
</div>

  <!-- Декоративная правая часть -->
  <div class="hidden lg:block lg:w-1/2 relative bg-green-600">
    z<div class="absolute inset-0 flex flex-col items-center justify-center p-12 text-white">
      <div class="w-20 h-20 bg-white/10 rounded-2xl flex items-center justify-center mb-8 backdrop-blur">
        <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
      </div>
      <h3 class="text-2xl font-bold mb-4">Ваши рабочие пространства</h3>
      <p class="max-w-md text-green-100 text-center">
        Все проекты под контролем. Открывайте доски, управляйте задачами и получайте аналитику.
      </p>
    </div>
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden opacity-20">
      <div class="absolute -top-10 -left-20 w-96 h-96 bg-white rounded-full filter blur-3xl"></div>
      <div class="absolute -bottom-20 -right-20 w-80 h-80 bg-green-300 rounded-full filter blur-3xl"></div>
    </div>
  </div>
</div>