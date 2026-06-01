<script>
  import Navbar from '$lib/components/layout/Navbar.svelte';
  import '../app.css'; 
  import { authStore } from '$lib/stores/authStore.js';
  import { onMount } from 'svelte';

  let sessionChecked = false;

  onMount(async () => {
    // Если пользователя ещё нет в сторе – пробуем восстановить сессию
    if (!$authStore) {
      await authStore.fetchUser();
    }
    sessionChecked = true;
  });
</script>

<div class="min-h-screen bg-white flex flex-col">
  <Navbar />
  <main class="flex-grow">
    <slot />
  </main>
</div>