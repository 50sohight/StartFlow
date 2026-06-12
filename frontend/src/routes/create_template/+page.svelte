<script>
  import { goto } from '$app/navigation';
  import { addUserTemplate } from '$lib/data/templates.js';

  let name = $state('');
  let description = $state('');
  let columns = $state([{ id: 'col-1', name: '', tasks: [] }]);
  let error = $state('');

  // Уникальные id для новых колонок
  let nextColId = 2;

  function addColumn() {
    columns = [...columns, { id: `col-${nextColId++}`, name: '', tasks: [] }];
  }

  function removeColumn(index) {
    if (columns.length <= 1) return;
    columns = columns.filter((_, i) => i !== index);
  }

  function updateColumnName(index, newName) {
    columns = columns.map((col, i) => 
      i === index ? { ...col, name: newName } : col
    );
  }

  function saveTemplate() {
    // Валидация
    if (!name.trim()) {
      error = 'Введите название шаблона';
      return;
    }
    if (columns.some(col => !col.name.trim())) {
      error = 'Все колонки должны иметь название';
      return;
    }
    error = '';

    const newTemplate = {
      id: '', // будет присвоен в addUserTemplate
      name: name.trim(),
      description: description.trim(),
      columns: columns.map(col => ({ ...col, name: col.name.trim() }))
    };

    addUserTemplate(newTemplate);
    // Перенаправляем обратно на создание проекта
    goto('/create_new_project');
  }
</script>

<div class="min-h-screen bg-gray-50 py-10 px-4">
  <div class="max-w-2xl mx-auto bg-white rounded-2xl shadow p-6 md:p-8">
    <a href="/create_new_project" class="text-sm text-gray-500 hover:text-gray-700 mb-4 inline-block">
      ← Назад к созданию проекта
    </a>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Новый шаблон</h1>

    {#if error}
      <div class="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>
    {/if}

    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-1">Название шаблона *</label>
      <input
        type="text"
        bind:value={name}
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 outline-none"
        placeholder="Мой шаблон"
      />
    </div>
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-1">Описание</label>
      <textarea
        bind:value={description}
        rows="3"
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 outline-none"
        placeholder="Описание шаблона..."
      ></textarea>
    </div>

    <h2 class="text-lg font-semibold text-gray-800 mb-3">Колонки</h2>
    <div class="space-y-3 mb-4">
      {#each columns as col, index (col.id)}
        <div class="flex items-center gap-2">
          <input
            type="text"
            value={col.name}
            oninput={(e) => updateColumnName(index, e.target.value)}
            placeholder="Название колонки"
            class="flex-1 px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
          <button
            onclick={() => removeColumn(index)}
            disabled={columns.length <= 1}
            class="px-2 py-1 text-red-500 hover:text-red-700 disabled:opacity-30"
            title="Удалить колонку"
          >
            ✕
          </button>
        </div>
      {/each}
    </div>
    <button
      onclick={addColumn}
      class="text-green-600 hover:text-green-800 text-sm font-medium mb-6"
    >
      + Добавить колонку
    </button>

    <div class="flex justify-end">
      <button
        onclick={saveTemplate}
        class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition"
      >
        Сохранить шаблон
      </button>
    </div>
  </div>
</div>