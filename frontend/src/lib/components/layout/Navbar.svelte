<script>
  import { fly, fade } from 'svelte/transition';
  import { authStore } from '$lib/stores/authStore';
  import Button from '$lib/components/ui/Button.svelte';
  import { User, LogOut, LayoutDashboard, ChevronDown, Menu, X } from 'lucide-svelte';
  
  let dropdownOpen = $state(false);
  let mobileMenuOpen = $state(false);
  
  const toggleDropdown = () => dropdownOpen = !dropdownOpen;
  const closeDropdown = () => dropdownOpen = false;

  const toggleMobile = () => mobileMenuOpen = !mobileMenuOpen;
  const closeMobile = () => mobileMenuOpen = false;
  
  const handleLogout = () => {
    authStore.logout();
    dropdownOpen = false;
    window.location.href = '/'; 
  };
</script>

<!-- Навигация -->
<nav class="bg-white border-b border-gray-100 sticky top-0 z-40">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16 items-center">
      
      <!-- Логотип -->
      <div class="flex items-center">
        <a href="/" class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-lg">SF</span>
          </div>
          <span class="text-xl font-bold text-gray-900">StartFlow</span>
        </a>
      </div>

      <!-- Десктоп меню -->
      <div class="hidden md:flex items-center space-x-8">
        <a href="/#features" class="text-gray-600 hover:text-gray-900 transition">Возможности</a>
        <a href="/#templates" class="text-gray-600 hover:text-gray-900 transition">Шаблоны</a>
        <a href="#" class="text-gray-600 hover:text-gray-900 transition">Цены</a>
      </div>

      <!-- Правая часть: Кнопки / Профиль -->
      <div class="hidden md:flex items-center space-x-4">
        {#if $authStore.id}
          <!-- Кнопка открытия панели профиля -->
          <button 
            onclick={toggleDropdown} 
            class="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-50 transition"
          >
            <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-semibold text-sm">
              {$authStore.avatar}
            </div>
            <span class="text-gray-700 font-medium">{$authStore.name}</span>
            <ChevronDown size="16" class="text-gray-400" />
          </button>
        {:else}
          <Button variant="secondary" href="/auth">Войти</Button>
          <Button variant="primary" href="/auth">Регистрация</Button>
        {/if}
      </div>

      <!-- Мобильный бургер -->
      <div class="md:hidden flex items-center">
        <button onclick={() => mobileMenuOpen = true} class="text-gray-600 p-2">
           <Menu size="24" />
        </button>
      </div>
    </div>
  </div>
</nav>

<!-- Панель профиля (Drawer) - Десктоп -->
{#if dropdownOpen}
  <!-- Затемнение фона -->
  <div 
    class="fixed inset-0 bg-black/40 z-40" 
    onclick={closeDropdown}
    transition:fade={{ duration: 150 }}
  ></div>

  <!-- Выдвигающаяся панель справа -->
  <div 
    class="fixed top-0 right-0 h-full w-72 bg-white shadow-2xl z-50 flex flex-col"
    transition:fly={{ x: 300, duration: 250 }}
    role="dialog"
    aria-modal = "true"
    onkeydown = {(e) => e.key === "Escape" && closeDropdown()}
    tabindex = "-1"
  >
    <!-- Шапка панели -->
    <div class="flex items-center justify-between p-4 border-b border-gray-100">
      <h2 class="font-bold text-lg text-gray-800">Профиль</h2>
      <button onclick={closeDropdown} class="p-1 rounded hover:bg-gray-100 text-gray-500">
        <X size="20" />
      </button>
    </div>

    <!-- Информация о пользователе -->
    <div class="p-4 border-b border-gray-100">
      <div class="flex items-center space-x-3 mb-3">
        <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-bold">
          {$authStore.avatar}
        </div>
        <div>
          <p class="font-semibold text-gray-900">{$authStore.name}</p>
          <p class="text-sm text-gray-500 truncate">{$authStore.email}</p>
        </div>
      </div>
    </div>

    <!-- Навигация панели -->
    <nav class="flex-1 p-2">
      <a 
        href="/dashboard" 
        onclick={closeDropdown}
        class="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg transition group"
      >
        <LayoutDashboard size="20" class="mr-3 text-gray-400 group-hover:text-green-600" />
        <span>Мои проекты</span>
      </a>
    </nav>

    <!-- Кнопка выхода -->
    <div class="p-4 border-t border-gray-100">
      <button 
        onclick={handleLogout} 
        class="w-full flex items-center justify-center px-4 py-2.5 text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition font-medium"
      >
        <LogOut size="18" class="mr-2" />
        Выйти из аккаунта
      </button>
    </div>
  </div>
{/if}

<!-- Мобильное меню (Drawer) -->
{#if mobileMenuOpen}
  <!-- Затемнение фона -->
  <div 
    class="fixed inset-0 bg-black/40 z-40" 
    onclick={closeMobile}
    transition:fade={{ duration: 150 }}
  ></div>

  <!-- Выдвигающаяся панель слева -->
  <div 
    class="fixed top-0 left-0 h-full w-72 bg-white shadow-2xl z-50 flex flex-col"
    transition:fly={{ x: -300, duration: 250 }}
    role="dialog"
    aria-modal="true"
    tabindex = "-1"
  >
    <!-- Шапка -->
    <div class="flex items-center justify-between p-4 border-b border-gray-100">
      <span class="font-bold text-lg text-gray-800">Меню</span>
      <button onclick={() => mobileMenuOpen = false} class="p-1 rounded hover:bg-gray-100 text-gray-500">
        <X size="20" />
      </button>
    </div>

    <!-- Ссылки -->
    <div class="flex-1 p-4 space-y-2">
      <a href="/#features" class="block px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50 font-medium" onclick = {closeMobile}>Возможности</a>
      <a href="/#templates" class="block px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50 font-medium" onclick = {closeMobile}>Шаблоны</a>
      <a href="#" class="block px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50 font-medium" onclick = {closeMobile}>Цены</a>
    </div>

    <!-- Блок авторизации внизу -->
    <div class="p-4 border-t border-gray-100 mt-auto">
      {#if $authStore.id}
        <a href="/dashboard" class="block w-full text-center px-4 py-2.5 mb-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium" onclick = {closeMobile}>
          Дашборд
        </a>
        <button onclick={handleLogout} class="block w-full text-center px-4 py-2.5 rounded-lg text-red-600 border border-red-200 hover:bg-red-50 font-medium">
          Выйти
        </button>
      {:else}
        <Button variant="primary" href="/auth" class="w-full">Войти</Button>
      {/if}
    </div>
  </div>
{/if}