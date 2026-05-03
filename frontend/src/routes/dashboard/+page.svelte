<script>
  import { authStore } from '$lib/stores/authStore';
  import { goto } from '$app/navigation'; 
  import Button from '$lib/components/ui/Button.svelte';
  import { Plus, Sparkles, Settings, Users } from 'lucide-svelte';

  // Мок проектов
  const projects = [
    { id: 1, name: 'Редизайн сайта', tasks: 12, progress: 60, members: 3 },
    { id: 2, name: 'Мобильное приложение', tasks: 24, progress: 30, members: 5 },
    { id: 3, name: 'Маркетинг Q4', tasks: 5, progress: 90, members: 2 },
  ];

  $effect(() => {
    if (!$authStore.id) {
      goto('/auth');
    }
  });

  function askAI() {
    alert('ИИ подсказка: "Проект Редизайн сайта близок к завершению. Рекомендую проверить задачи в колонке Review."');
  }
</script>

{#if $authStore.id}
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Добро пожаловать, {$authStore.name}!</h1>
        <p class="text-gray-500">Ваши активные проекты.</p>
      </div>
      <Button variant="primary" href="/board">
        <Plus size="18" class="mr-2" /> Новый проект
      </Button>
    </div>

    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each projects as project}
        <div class="bg-white border border-gray-100 rounded-2xl p-6 hover:shadow-md transition group">
          <div class="flex justify-between items-start mb-4">
            <h3 class="font-bold text-lg text-gray-800 group-hover:text-green-600 transition">{project.name}</h3>
            <button class="text-gray-300 hover:text-gray-600"><Settings size="18" /></button>
          </div>
          <div class="mb-4">
            <div class="flex justify-between text-xs text-gray-500 mb-1">
              <span>Прогресс</span>
              <span>{project.progress}%</span>
            </div>
            <div class="w-full bg-gray-100 h-2 rounded-full">
              <div class="bg-green-500 h-2 rounded-full transition-all" style="width: {project.progress}%"></div>
            </div>
          </div>
          <div class="flex justify-between items-center text-sm text-gray-500">
            <span>{project.tasks} задач</span>
            <div class="flex items-center text-gray-400">
              <Users size="14" class="mr-1" /> {project.members}
            </div>
          </div>
        </div>
      {/each}
    </div>

    <div class="fixed bottom-8 right-8 z-50">
      <button 
        onclick={askAI}
        class="bg-green-600 text-white p-4 rounded-full shadow-lg hover:bg-green-700 transition flex items-center justify-center group relative"
      >
        <Sparkles size="24" />
        <span class="absolute right-full mr-3 px-3 py-1.5 bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition">
          Спросить ИИ
        </span>
      </button>
    </div>
  </div>
{/if}