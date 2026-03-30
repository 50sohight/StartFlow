<script>
  import Navbar from '$lib/components/layout/Navbar.svelte';
  import '../app.css'; 
</script>

<div class="min-h-screen bg-white flex flex-col">
  <Navbar />
  <main class="flex-grow">
    <slot />
  </main>
</div>