<script setup>
import { ref } from 'vue'
import { api, store } from '../store'

const query = ref('')
const loading = ref(false)
const results = ref(null)

const performSearch = async () => {
  if (!query.value.trim() || !store.config.dataset_loaded) return
  
  loading.value = true
  results.value = null
  
  try {
    const res = await api.post('/search/interactive', {
      query: query.value,
      query_id: 1, // Defaulting to 1 for MAP demonstration if applicable, but usually user enters text
      weight_scheme: store.searchParams.weight_scheme,
      tf_variant: store.searchParams.tf_variant,
      top_k_expansion: store.searchParams.top_k_expansion,
      all_expansion_terms: store.searchParams.all_expansion_terms
    })
    
    results.value = res.data
  } catch (e) {
    console.error(e)
    alert("Error performing search. Is the backend running?")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-6 h-full">
    <!-- Search Bar Area: Light-themed, minimal borders, no background blur/gradients/shadows -->
    <div class="bg-card-bg rounded-lg border border-divider p-6 shadow-none relative overflow-hidden">
      <div class="relative z-10 flex flex-col gap-4">
        <h2 class="text-xl font-semibold text-text-primary">
          Interactive Search
        </h2>
        
        <form @submit.prevent="performSearch" class="relative group">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <svg class="w-5 h-5 text-text-secondary group-focus-within:text-accent-indigo transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input 
            v-model="query" 
            type="text" 
            placeholder="Enter your search query..." 
            class="block w-full pl-12 pr-32 py-2.5 bg-card-bg border border-divider rounded-lg text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-indigo transition-all"
            :disabled="!store.config.dataset_loaded || loading"
          >
          <button 
            type="submit" 
            class="absolute inset-y-1.5 right-2 px-4 text-sm bg-accent-indigo hover:bg-accent-hover text-white rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-accent-indigo disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            :disabled="!query.trim() || !store.config.dataset_loaded || loading"
          >
            <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            {{ loading ? 'Searching...' : 'Search' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Results Area -->
    <div v-if="results" class="flex-1 grid grid-cols-1 xl:grid-cols-2 gap-6 min-h-0">
      
      <!-- Original Results -->
      <div class="bg-card-bg rounded-lg border border-divider p-6 flex flex-col h-[600px] shadow-none relative overflow-hidden">
        <div class="relative z-10 border-b border-divider pb-4 mb-4">
          <h3 class="text-md font-semibold text-text-primary flex items-center gap-2">
            Original Query
            <span class="px-2 py-0.5 rounded text-xs font-mono bg-app-bg border border-divider text-text-secondary">Tokens: {{ results.original.query.length }}</span>
          </h3>
          <p class="text-sm text-text-primary mt-2 font-mono bg-app-bg border border-divider p-2.5 rounded-md break-words">
            [{{ results.original.query.join(', ') }}]
          </p>
        </div>
        
        <div class="flex-1 overflow-y-auto pr-2 space-y-1 custom-scrollbar relative z-10">
          <div v-if="results.original.results.length === 0" class="text-center py-10 text-text-secondary text-sm">
            No documents found.
          </div>
          
          <div v-for="(doc, idx) in results.original.results" :key="doc.doc_id" class="border-b border-divider/60 py-3.5 px-1 hover:bg-[#F3F4F6] transition-colors duration-150 group">
            <div class="flex justify-between items-start mb-2">
              <span class="inline-flex items-center justify-center w-6 h-6 rounded bg-app-bg text-xs font-bold text-text-secondary border border-divider group-hover:border-accent-indigo/50 group-hover:text-accent-indigo transition-colors">
                {{ idx + 1 }}
              </span>
              <span class="text-[11px] font-mono px-2 py-0.5 bg-app-bg rounded border border-divider text-text-secondary">
                Score: {{ doc.score.toFixed(4) }}
              </span>
            </div>
            <h4 class="text-sm font-medium text-text-primary mb-1 line-clamp-2">{{ doc.title || 'Untitled Document' }}</h4>
            <div class="text-[10px] text-text-secondary font-mono">Doc ID: {{ doc.doc_id }}</div>
          </div>
        </div>
      </div>

      <!-- Expanded Results -->
      <div class="bg-card-bg rounded-lg border border-divider p-6 flex flex-col h-[600px] shadow-none relative overflow-hidden">
        <div class="relative z-10 border-b border-divider pb-4 mb-4">
          <h3 class="text-md font-semibold text-accent-indigo flex items-center gap-2">
            Expanded Query
            <span class="px-2 py-0.5 rounded text-xs font-mono bg-indigo-50 border border-indigo-100 text-accent-indigo">Tokens: {{ results.expanded.query.length }}</span>
          </h3>
          
          <div class="mt-2 flex flex-wrap gap-1.5 max-h-24 overflow-y-auto custom-scrollbar">
            <span 
              v-for="term in results.original.query" 
              :key="term" 
              class="px-2 py-1 text-[11px] font-medium bg-[#F3F4F6] text-text-secondary border border-divider rounded"
            >
              {{ term }}
            </span>
            <span 
              v-for="(weight, term) in results.expanded.expansion_weights" 
              :key="'exp'+term" 
              class="px-2 py-1 text-[11px] font-medium bg-indigo-50 text-accent-indigo border border-indigo-100 rounded flex items-center gap-1"
            >
              {{ term }} <span class="opacity-60 text-[10px]">{{ weight.toFixed(2) }}</span>
            </span>
          </div>
        </div>
        
        <div class="flex-1 overflow-y-auto pr-2 space-y-1 custom-scrollbar relative z-10">
          <div v-if="results.expanded.results.length === 0" class="text-center py-10 text-text-secondary text-sm">
            No documents found.
          </div>
          
          <div v-for="(doc, idx) in results.expanded.results" :key="'e'+doc.doc_id" class="border-b border-divider/60 py-3.5 px-1 hover:bg-[#F3F4F6] transition-colors duration-150 group">
            <div class="flex justify-between items-start mb-2">
              <span class="inline-flex items-center justify-center w-6 h-6 rounded bg-app-bg text-xs font-bold text-text-secondary border border-divider group-hover:border-accent-indigo/50 group-hover:text-accent-indigo transition-colors">
                {{ idx + 1 }}
              </span>
              <span class="text-[11px] font-mono px-2 py-0.5 bg-app-bg rounded border border-divider text-text-secondary">
                Score: {{ doc.score.toFixed(4) }}
              </span>
            </div>
            <h4 class="text-sm font-medium text-text-primary mb-1 line-clamp-2">{{ doc.title || 'Untitled Document' }}</h4>
            <div class="text-[10px] text-text-secondary font-mono">Doc ID: {{ doc.doc_id }}</div>
          </div>
        </div>
      </div>
      
    </div>
    
    <!-- Empty State -->
    <div v-else class="flex-1 flex flex-col items-center justify-center p-12 border-2 border-dashed border-divider rounded-lg opacity-70">
      <svg class="w-12 h-12 text-text-secondary mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z M10 7v3m0 0v3m0-3h3m-3 0H7" />
      </svg>
      <p class="text-md font-medium text-text-primary">Enter a query to see retrieval results</p>
      <p class="text-xs text-text-secondary mt-1.5 max-w-sm text-center">The system will display a side-by-side comparison of the document rankings before and after query expansion.</p>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(107, 114, 128, 0.2);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(107, 114, 128, 0.4);
}
</style>
