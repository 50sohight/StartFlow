<script>
  let {
    variant = 'primary',
    type = 'button',
    loading = false,
    href = null,
    class: className = '',
    children,
    ...restProps
  } = $props();

  const baseClasses = 'px-6 py-2.5 rounded-lg font-semibold transition-all duration-200 inline-flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 shadow-sm',
    secondary: 'bg-gray-100 text-gray-800 hover:bg-gray-200 focus:ring-gray-300',
    outline: 'border-2 border-green-600 text-green-600 hover:bg-green-50 focus:ring-green-500'
  };
</script>

{#if href}
  <a 
    href={href} 
    class="{baseClasses} {variantClasses[variant]} {className}" 
    {...restProps}
  >
    {#if loading}
      <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {/if}
    {@render children()}
  </a>
{:else}
  <button 
    {type} 
    class="{baseClasses} {variantClasses[variant]} {className}" 
    disabled={loading}
    {...restProps}
  >
    {#if loading}
      <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {/if}
    {@render children()}
  </button>
{/if}