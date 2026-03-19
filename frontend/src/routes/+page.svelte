<script>
  import Button from '$lib/components/ui/Button.svelte';
  import { ArrowRight, Sparkles, LayoutTemplate, Users } from 'lucide-svelte';
</script>

<!-- Hero Section -->
<section class="relative bg-gradient-to-b from-white to-green-50 pt-20 pb-24 sm:pt-32 sm:pb-32 overflow-hidden">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center lg:grid lg:grid-cols-2 lg:gap-8 lg:text-left items-center">
      <div class="mb-12 lg:mb-0 z-10 relative">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 mb-6">
          <Sparkles size="14" class="mr-2" /> ИИ-помощник нового поколения
        </span>
        <h1 class="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
          <span class="block">Организуйте проекты</span>
          <span class="block text-green-600">быстрее и умнее</span>
        </h1>
        <p class="mt-6 text-lg text-gray-600 sm:text-xl max-w-3xl mx-auto lg:mx-0">
          Kanban-доски с готовыми шаблонами и интегрированный ИИ, который поможет вам и вашей команде сориентироваться в любой задаче за минуты.
        </p>
        <div class="mt-8 flex justify-center lg:justify-start gap-4">
          <Button variant="primary" href="/auth">
            Начать бесплатно <ArrowRight size="18" class="ml-2" />
          </Button>
          <Button variant="secondary">Смотреть демо</Button>
        </div>
      </div>
      
      <!-- Декоративный элемент / Мокап интерфейса -->
      <div class="relative lg:opacity-90 transform lg:scale-110">
        <div class="bg-white p-2 rounded-2xl shadow-2xl border border-gray-200">
          <div class="h-64 sm:h-80 bg-gray-50 rounded-xl flex items-center justify-center relative overflow-hidden">
             <!-- Схематичный мокап доски -->
             <div class="absolute inset-0 grid grid-cols-3 gap-4 p-6 opacity-50">
                <div class="bg-white rounded-lg shadow h-full p-3 space-y-2">
                   <div class="h-3 bg-gray-200 rounded w-3/4"></div>
                   <div class="h-24 bg-gray-100 rounded"></div>
                   <div class="h-20 bg-green-100 rounded border-2 border-green-200"></div>
                </div>
                <div class="bg-white rounded-lg shadow h-full p-3 space-y-2">
                   <div class="h-3 bg-gray-200 rounded w-1/2"></div>
                   <div class="h-32 bg-blue-100 rounded border border-blue-200"></div>
                </div>
                <div class="bg-white rounded-lg shadow h-full p-3 space-y-2">
                   <div class="h-3 bg-gray-200 rounded w-2/3"></div>
                   <div class="h-16 bg-gray-100 rounded"></div>
                </div>
             </div>
             
             <!-- Всплывашка ИИ -->
             <div class="absolute bottom-8 right-8 bg-white p-4 rounded-xl shadow-xl border border-gray-100 text-left max-w-xs transform transition hover:scale-105">
               <div class="flex items-center mb-2 text-green-600">
                 <Sparkles size="16" class="mr-2" />
                 <span class="font-semibold text-xs uppercase tracking-wider">AI Подсказка</span>
               </div>
               <p class="text-sm text-gray-800">Судя по задачам в "In Progress", спринт завершен на 70%. Хотите сгенерировать отчет?</p>
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Features Section -->
<section id="features" class="py-20 bg-white">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-16">
      <h2 class="text-base text-green-600 font-semibold tracking-wide uppercase">Возможности</h2>
      <p class="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
        Все для эффективной работы
      </p>
    </div>

    <div class="grid md:grid-cols-3 gap-10">
      <!-- Card 1 -->
      <div class="bg-gray-50 p-8 rounded-2xl hover:shadow-lg transition group">
        <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center text-green-600 mb-6 group-hover:bg-green-600 group-hover:text-white transition">
          <LayoutTemplate size="24" />
        </div>
        <h3 class="text-xl font-bold text-gray-900 mb-3">Готовые шаблоны</h3>
        <p class="text-gray-600">Scrum, Kanban, Waterfall или кастомные шаблоны для вашего процесса. Разворачивайте структуру проекта в один клик.</p>
      </div>

      <!-- Card 2 -->
      <div class="bg-gray-50 p-8 rounded-2xl hover:shadow-lg transition group">
        <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center text-green-600 mb-6 group-hover:bg-green-600 group-hover:text-white transition">
          <Sparkles size="24" />
        </div>
        <h3 class="text-xl font-bold text-gray-900 mb-3">ИИ-навигация</h3>
        <p class="text-gray-600">Запутались в задачах? ИИ проанализирует контекст проекта и подскажет, за что взяться первым или где есть риски.</p>
      </div>

      <!-- Card 3 -->
      <div class="bg-gray-50 p-8 rounded-2xl hover:shadow-lg transition group">
        <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center text-green-600 mb-6 group-hover:bg-green-600 group-hover:text-white transition">
          <Users size="24" />
        </div>
        <h3 class="text-xl font-bold text-gray-900 mb-3">Командная работа</h3>
        <p class="text-gray-600">Удобный онбординг для новых участников. Вливайтесь в процесс без долгих объяснений, благодаря понятной структуре.</p>
      </div>
    </div>
  </div>
</section>

<!-- Templates Section -->
<section id="templates" class="py-20 bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
    <h2 class="text-3xl font-extrabold text-gray-900">Популярные шаблоны</h2>
    <p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">Выберите готовый сценарий или создайте свой. Идеальная отправная точка для любого проекта.</p>
    
    <div class="mt-12 grid grid-cols-2 md:grid-cols-4 gap-6">
      {#each ['Базовый Канбан', 'Scrum Sprint', 'Bug Tracker', 'Маркетинг'] as name, i}
        <div class="bg-white p-6 rounded-xl border border-gray-200 hover:border-green-500 cursor-pointer transition hover:shadow-md h-32 flex flex-col justify-between">
          <div class="h-12 w-12 mx-auto bg-green-50 rounded-lg mb-2 flex items-center justify-center text-green-600 font-bold">{i + 1}</div>
          <h4 class="font-semibold text-gray-800">{name}</h4>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- CTA -->
<section class="bg-green-600 py-16">
  <div class="max-w-4xl mx-auto text-center px-4">
    <h2 class="text-3xl font-bold text-white mb-4">Готовы упростить управление проектами?</h2>
    <p class="text-green-100 mb-8 text-lg">Присоединяйтесь к командам, которые экономят время на рутине.</p>
    <Button variant="secondary" href="/auth" class="bg-white text-green-600 hover:bg-gray-100 focus:ring-white">
      Создать проект бесплатно
    </Button>
  </div>
</section>