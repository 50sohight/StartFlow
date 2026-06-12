<script>
  let { template, selected = false, onSelect = () => {} } = $props();
</script>

<button
  onclick={() => onSelect(template)}
  class={`p-4 border rounded-xl text-left transition cursor-pointer w-full
    ${selected ? 'border-green-500 ring-2 ring-green-200 bg-green-50' : 'border-gray-200 hover:border-green-400 hover:shadow'}`}
>
  <h3 class="font-semibold text-gray-900">{template.name}</h3>
  <p class="text-sm text-gray-600 mt-1">{template.description}</p>
  <div class="mt-2 text-xs text-gray-500">
    {#if template.columns.length > 0}
      Колонки: {template.columns.map(c => c.name).join(', ')}
    {:else}
      Пустая доска
    {/if}
  </div>
</button>