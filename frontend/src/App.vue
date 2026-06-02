<script setup>
import { ref } from 'vue'
import ConfigPanel from './components/ConfigPanel.vue'
import InteractiveSearch from './components/InteractiveSearch.vue'
import BatchProcessing from './components/BatchProcessing.vue'
import IndexInspector from './components/IndexInspector.vue'

const activeTab = ref('search') // search, batch, index
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-slate-200 font-sans selection:bg-indigo-500/30">
    <!-- Header with Glassmorphism -->
    <header class="sticky top-0 z-50 backdrop-blur-md bg-slate-900/70 border-b border-slate-700/50 shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400 tracking-tight">
            IR Engine + QE
          </h1>
        </div>
        
        <nav class="flex gap-1 bg-slate-800/50 p-1 rounded-lg border border-slate-700/50">
          <button 
            @click="activeTab = 'search'" 
            :class="['px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-300', activeTab === 'search' ? 'bg-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50']"
          >
            Interactive Search
          </button>
          <button 
            @click="activeTab = 'batch'" 
            :class="['px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-300', activeTab === 'batch' ? 'bg-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50']"
          >
            Batch Mode
          </button>
          <button 
            @click="activeTab = 'index'" 
            :class="['px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-300', activeTab === 'index' ? 'bg-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50']"
          >
            Index Inspector
          </button>
        </nav>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col lg:flex-row gap-8">
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
