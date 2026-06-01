<script>
  let { show = false, onClose = () => {} } = $props();
</script>

{#if show}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4">
      <div class="flex justify-end">
        <button
          onclick={onClose}
          class="text-gray-400 hover:text-gray-600 text-xl leading-none"
        >
          ×
        </button>
      </div>
      <div>
        <slot />
      </div>
    </div>
  </div>
{/if}