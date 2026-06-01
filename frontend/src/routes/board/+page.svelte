<script lang="ts">
  import KanbanBoard from '$lib/components/ui/Kanban.svelte';
  import { templates, type Column } from '$lib/data/templates';

  let currentColumns = $state<Column[]>([]);
  let activeTemplateName = $state<string>('Выберите шаблон');

  function loadTemplate(templateId: string) {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      // Важно: делаем глубокую копию, чтобы не ломать исходные данные
      currentColumns = structuredClone(template.columns);
      activeTemplateName = template.name;
    }
  }
</script>

<div class="p-4 md:p-6 bg-gray-100 h-[calc(100vh-64px)] overflow-auto flex flex-col">
  
  <!-- Верхняя панель -->
  <div class="mb-4 flex items-center gap-4 flex-wrap border-b border-gray-200 pb-4">
    <h1 class="text-2xl font-bold text-gray-800">{activeTemplateName}</h1>
    
    <div class="flex gap-2">
      {#each templates as t}
        <button 
          class="px-4 py-2 text-sm rounded-lg border transition
            {activeTemplateName === t.name 
              ? 'bg-blue-600 text-white border-blue-600' 
              : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'}"
          onclick={() => loadTemplate(t.id)}
        >
          {t.name}
        </button>
      {/each}
    </div>
  </div>

  <!-- Контент -->
  {#if currentColumns.length > 0}
    <KanbanBoard bind:columns={currentColumns} />
  {:else}
    <div class="flex-1 flex items-center justify-center">
      <div class="text-center grid grid-cols-1 md:grid-cols-3 gap-4">
         {#each templates as t}
           <button 
             class="p-6 bg-white rounded-xl shadow-sm hover:shadow-lg border hover:border-blue-500 transition text-left"
             onclick={() => loadTemplate(t.id)}
           >
             <h3 class="font-bold text-lg mb-1">{t.name}</h3>
             <p class="text-sm text-gray-400">{t.description}</p>
           </button>
         {/each}
      </div>
    </div>
  {/if}

</div>