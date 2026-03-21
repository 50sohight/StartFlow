<script lang="ts">
  import KanbanBoard from '$lib/components/ui/Kanban.svelte';
  import { templates, type Column } from '$lib/data/templates';

  // Состояние текущей доски
  let currentColumns = $state<Column[]>([]);
  let activeTemplateName = $state<string>('Выберите шаблон');

  // Функция загрузки шаблона
  function loadTemplate(templateId: string) {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      // ГЛУБОКОЕ КОПИРОВАНИЕ! Иначе мы испортим исходные данные
      currentColumns = structuredClone(template.columns);
      activeTemplateName = template.name;
    }
  }
</script>

<svelte:head>
  <title>Доска | StartFlow</title>
</svelte:head>

<div class="p-4 md:p-6 bg-gray-100 h-[calc(100vh-64px)] overflow-auto flex flex-col">
  
  <!-- Панель управления шаблоном -->
  <div class="mb-4 flex items-center gap-4 flex-wrap">
    <h1 class="text-2xl font-bold text-gray-800">{activeTemplateName}</h1>
  </div>

  <!-- Рендер доски -->
  {#if currentColumns.length > 0}
    <!-- bind:columns связывает стейт страницы с инпутами доски -->
    <KanbanBoard bind:columns={currentColumns} />
  {:else}
    <div class="flex-1 flex items-center justify-center text-gray-400">
      <div class="text-center">
        <p class="text-lg mb-4">Выберите шаблон для начала работы</p>
        <div class="flex gap-4">
           {#each templates as t}
             <button 
               class="p-4 bg-white rounded-xl shadow-sm hover:shadow-md border hover:border-blue-500 transition w-48"
               onclick={() => loadTemplate(t.id)}
             >
               <h3 class="font-bold mb-1">{t.name}</h3>
               <p class="text-xs text-gray-400">{t.description}</p>
             </button>
           {/each}
        </div>
      </div>
    </div>
  {/if}

</div>