<!-- src/routes/auth/register/+page.svelte -->
<script>
  import { authStore } from '$lib/stores/authStore.js';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';

  let fullname = '';
  let login = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleRegister() {
    error = '';
    if (!fullname || !login || !password) {
      error = 'Заполните все поля';
      return;
    }
    loading = true;
    try {
      await authStore.register(fullname, login, password);
      goto('/dashboard');
    } catch (e) {
      error = 'Ошибка регистрации. Возможно, логин уже занят.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-[calc(100vh-64px)] flex">
  <div class="w-full lg:w-1/2 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 xl:px-24">
    <div class="mx-auto w-full max-w-sm">
      <a href="/" class="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-8">
        Назад на главную
      </a>
      <h2 class="text-3xl font-bold text-gray-900">Регистрация</h2>
      <p class="mt-2 text-gray-600">Создайте аккаунт для управления проектами.</p>

      <form on:submit|preventDefault={handleRegister} class="mt-8 space-y-6">
        {#if error}
          <div class="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
        {/if}

        <div>
          <label for="fullname" class="block text-sm font-medium text-gray-700">Полное имя</label>
          <input
            id="fullname"
            type="text"
            bind:value={fullname}
            required
            class="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 outline-none transition"
            placeholder="Иван Иванов"
          />
        </div>

        <div>
          <label for="login" class="block text-sm font-medium text-gray-700">Логин</label>
          <input
            id="login"
            type="text"
            bind:value={login}
            required
            class="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 outline-none transition"
            placeholder="your_login"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">Пароль</label>
          <input
            id="password"
            type="password"
            bind:value={password}
            required
            class="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 outline-none transition"
            placeholder="••••••••"
          />
        </div>

        <Button type="submit" {loading} variant="primary" class="w-full py-3 text-base">
          {#if loading}Регистрация...{:else}Зарегистрироваться{/if}
        </Button>
      </form>

      <p class="mt-4 text-center text-sm text-gray-600">
        Уже есть аккаунт? <a href="/auth/login" class="text-green-600 hover:underline">Войти</a>
      </p>
    </div>
  </div>

  <div class="hidden lg:block lg:w-1/2 relative bg-green-600">
    <div class="absolute inset-0 flex flex-col items-center justify-center p-12 text-white">
      <div class="w-20 h-20 bg-white/10 rounded-2xl flex items-center justify-center mb-8 backdrop-blur">
        <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
      </div>
      <h3 class="text-2xl font-bold mb-4">Управляйте с умом</h3>
      <p class="max-w-md text-green-100 text-center">
        Наши инструменты и ИИ-помощник помогут вам сосредоточиться на важном, автоматизируя рутину.
      </p>
    </div>
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden opacity-20">
      <div class="absolute -top-10 -left-20 w-96 h-96 bg-white rounded-full filter blur-3xl"></div>
      <div class="absolute -bottom-20 -right-20 w-80 h-80 bg-green-300 rounded-full filter blur-3xl"></div>
    </div>
  </div>
</div>