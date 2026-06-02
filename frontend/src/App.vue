<script setup>
import { ref } from 'vue'
import ConfigPanel from './components/ConfigPanel.vue'
import InteractiveSearch from './components/InteractiveSearch.vue'
import BatchProcessing from './components/BatchProcessing.vue'
import IndexInspector from './components/IndexInspector.vue'

const activeTab = ref('search') // search, batch, index
</script>

<template>
  <div class="min-h-screen bg-app-bg text-text-primary font-sans selection:bg-accent-indigo/20">
    <!-- Header: Pure white, clean border, no shadows or gradients -->
    <header class="sticky top-0 z-50 bg-card-bg border-b border-divider">
      <div class="max-w-[1200px] mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <h1 class="text-lg font-semibold text-text-primary tracking-tight">
            Query Expansion with Transformer
          </h1>
        </div>
        
        <nav class="flex gap-1 bg-app-bg p-1 rounded-md border border-divider">
          <button 
            @click="activeTab = 'search'" 
            :class="['px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-150', activeTab === 'search' ? 'bg-accent-indigo text-white' : 'text-text-secondary hover:text-text-primary hover:bg-[#F3F4F6]']"
          >
            Interactive Search
          </button>
          <button 
            @click="activeTab = 'batch'" 
            :class="['px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-150', activeTab === 'batch' ? 'bg-accent-indigo text-white' : 'text-text-secondary hover:text-text-primary hover:bg-[#F3F4F6]']"
          >
            Batch Mode
          </button>
          <button 
            @click="activeTab = 'index'" 
            :class="['px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-150', activeTab === 'index' ? 'bg-accent-indigo text-white' : 'text-text-secondary hover:text-text-primary hover:bg-[#F3F4F6]']"
          >
            Index Inspector
          </button>
        </nav>
      </div>
    </header>

    <main class="max-w-[1200px] mx-auto px-4 py-8 flex flex-col lg:flex-row gap-8">
      <!-- Config Panel Sidebar -->
      <aside class="w-full lg:w-80 shrink-0">
        <ConfigPanel />
      </aside>

      <!-- Main Content Area -->
      <div class="flex-1 min-w-0 transition-all duration-500">
        <Transition name="fade" mode="out-in">
          <InteractiveSearch v-if="activeTab === 'search'" />
          <BatchProcessing v-else-if="activeTab === 'batch'" />
          <IndexInspector v-else-if="activeTab === 'index'" />
        </Transition>
      </div>
    </main>
  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
