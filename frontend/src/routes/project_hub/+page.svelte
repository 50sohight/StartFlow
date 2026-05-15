<script>
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/authStore.js';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';

  let code = $state('');
  let message = $state('');
  let messageType = $state(''); // 'success' | 'error'

  onMount(async () => {
    await authStore.fetchUser();
    if (!$authStore) {
      goto('/auth/register');
    }
  });

  async function handleJoin() {
    if (!code.trim()) {
      message = 'Введите код приглашения';
      messageType = 'error';
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/link/use_link/${encodeURIComponent(code.trim())}`, {
        method: 'POST',
        credentials: 'include'
      });
      if (res.ok) {
        message = 'Вы успешно присоединились к проекту!';
        messageType = 'success';
      } else {
        const err = await res.text();
        message = err || 'Не удалось присоединиться';
        messageType = 'error';
      }
    } catch (e) {
      message = 'Ошибка сети';
      messageType = 'error';
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center px-4">
  <div class="max-w-md w-full bg-white rounded-2xl shadow-lg p-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Управление проектами</h1>

    <div class="mb-8">
      <Button variant="primary" onclick={() => goto('/create_new_project')} class="w-full">
        Создать новый проект
      </Button>
    </div>

    <div class="border-t pt-6">
      <h2 class="text-lg font-medium text-gray-800 mb-3">Присоединиться к проекту</h2>
      <label for="code" class="block text-sm text-gray-600 mb-1">Код приглашения</label>
      <input
        id="code"
        type="text"
        bind:value={code}
        placeholder="например, a1b2c3d4..."
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 outline-none"
      />
      <div class="mt-3">
        <Button variant="secondary" onclick={handleJoin} class="w-full">
          Присоединиться
        </Button>
      </div>
      <div class="mt-3">
        <Button variant="secondary" onclick={() => goto('/projects')} class="w-full">
          Перейти к проектам
        </Button>
      </div>

      {#if message}
        <div
          class={`mt-4 p-3 rounded-lg text-sm
          ${messageType === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'}`}
        >
          {message}
          {#if messageType === 'success'}
            <div class="mt-2">
              <Button variant="primary" onclick={() => goto('/projects')}>
                Перейти к проектам
              </Button>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>