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

  <!-- Правая декоративная часть — можно скопировать такую же, как в логине -->
  <div class="hidden lg:block lg:w-1/2 relative bg-green-600">
    <!-- ... такой же декор, как в login/+page.svelte -->
  </div>
</div>