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
    <!-- Search Bar Area -->
    <div class="bg-slate-800/60 backdrop-blur-lg rounded-2xl border border-slate-700/50 p-6 shadow-xl relative overflow-hidden">
      <div class="absolute -bottom-20 -left-20 w-60 h-60 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div class="relative z-10 flex flex-col gap-4">
        <h2 class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
          Interactive Search
        </h2>
        
        <form @submit.prevent="performSearch" class="relative group">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <svg class="w-5 h-5 text-slate-400 group-focus-within:text-indigo-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input 
            v-model="query" 
            type="text" 
            placeholder="Enter your search query..." 
            class="block w-full pl-12 pr-32 py-4 bg-slate-900/50 border border-slate-700/50 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all shadow-inner"
            :disabled="!store.config.dataset_loaded || loading"
          >
          <button 
            type="submit" 
            class="absolute inset-y-2 right-2 px-6 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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
      <div class="bg-slate-800/40 backdrop-blur-sm rounded-2xl border border-slate-700/50 p-6 flex flex-col h-[600px] shadow-lg relative overflow-hidden">
        <div class="absolute top-0 right-0 p-4 opacity-10">
          <svg class="w-24 h-24 text-slate-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/></svg>
        </div>
        
        <div class="relative z-10 border-b border-slate-700/50 pb-4 mb-4">
          <h3 class="text-lg font-semibold flex items-center gap-2">
            Original Query
            <span class="px-2 py-0.5 rounded text-xs font-mono bg-slate-700 text-slate-300">Tokens: {{ results.original.query.length }}</span>
          </h3>
          <p class="text-sm text-slate-400 mt-1 font-mono bg-slate-900/50 p-2 rounded-lg break-words">
            [{{ results.original.query.join(', ') }}]
          </p>
        </div>
        
        <div class="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar relative z-10">
          <div v-if="results.original.results.length === 0" class="text-center py-10 text-slate-500">
            No documents found.
          </div>
          
          <div v-for="(doc, idx) in results.original.results" :key="doc.doc_id" class="bg-slate-900/40 border border-slate-700/30 rounded-xl p-4 hover:bg-slate-800/60 transition-colors group">
            <div class="flex justify-between items-start mb-2">
              <span class="inline-flex items-center justify-center w-6 h-6 rounded-md bg-slate-800 text-xs font-bold text-slate-400 border border-slate-700 group-hover:border-indigo-500/50 group-hover:text-indigo-400 transition-colors">
                {{ idx + 1 }}
              </span>
              <span class="text-xs font-mono px-2 py-1 bg-slate-800 rounded border border-slate-700 text-slate-400">
                Score: {{ doc.score.toFixed(4) }}
              </span>
            </div>
            <h4 class="text-sm font-medium text-slate-200 mb-1 line-clamp-2">{{ doc.title || 'Untitled Document' }}</h4>
            <div class="text-xs text-slate-500 font-mono">Doc ID: {{ doc.doc_id }}</div>
          </div>
        </div>
      </div>

      <!-- Expanded Results -->
      <div class="bg-slate-800/40 backdrop-blur-sm rounded-2xl border border-indigo-500/20 p-6 flex flex-col h-[600px] shadow-lg shadow-indigo-500/5 relative overflow-hidden">
        <div class="absolute top-0 right-0 p-4 opacity-10">
          <svg class="w-24 h-24 text-indigo-400" fill="currentColor" viewBox="0 0 24 24"><path d="M13 2.05v3.03c3.39.49 6 3.39 6 6.92 0 .9-.18 1.75-.48 2.54l2.6 1.53c.56-1.24.88-2.62.88-4.07 0-5.18-3.95-9.45-9-9.95zM12 19c-3.87 0-7-3.13-7-7 0-3.53 2.61-6.43 6-6.92V2.05c-5.06.5-9 4.76-9 9.95 0 5.52 4.47 10 9.99 10 3.31 0 6.24-1.61 8.06-4.09l-2.6-1.53C16.17 17.98 14.21 19 12 19z"/></svg>
        </div>

        <div class="relative z-10 border-b border-indigo-500/20 pb-4 mb-4">
          <h3 class="text-lg font-semibold flex items-center gap-2 text-indigo-300">
            Expanded Query
            <span class="px-2 py-0.5 rounded text-xs font-mono bg-indigo-500/20 text-indigo-300">Tokens: {{ results.expanded.query.length }}</span>
          </h3>
          
          <div class="mt-2 flex flex-wrap gap-1.5 max-h-24 overflow-y-auto custom-scrollbar">
            <span 
              v-for="term in results.original.query" 
              :key="term" 
              class="px-2 py-1 text-xs font-medium bg-slate-700/50 text-slate-300 border border-slate-600 rounded-md"
            >
              {{ term }}
            </span>
            <span 
              v-for="(weight, term) in results.expanded.expansion_weights" 
              :key="'exp'+term" 
              class="px-2 py-1 text-xs font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-md flex items-center gap-1"
            >
              {{ term }} <span class="opacity-50 text-[10px]">{{ weight.toFixed(2) }}</span>
            </span>
          </div>
        </div>
        
        <div class="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar relative z-10">
          <div v-if="results.expanded.results.length === 0" class="text-center py-10 text-slate-500">
            No documents found.
          </div>
          
          <div v-for="(doc, idx) in results.expanded.results" :key="'e'+doc.doc_id" class="bg-indigo-900/10 border border-indigo-500/20 rounded-xl p-4 hover:bg-indigo-900/20 transition-colors group">
            <div class="flex justify-between items-start mb-2">
              <span class="inline-flex items-center justify-center w-6 h-6 rounded-md bg-indigo-950 text-xs font-bold text-indigo-400 border border-indigo-500/30 group-hover:border-indigo-400 group-hover:text-indigo-300 transition-colors">
                {{ idx + 1 }}
              </span>
              <span class="text-xs font-mono px-2 py-1 bg-indigo-950 rounded border border-indigo-500/30 text-indigo-300">
                Score: {{ doc.score.toFixed(4) }}
              </span>
            </div>
            <h4 class="text-sm font-medium text-slate-200 mb-1 line-clamp-2">{{ doc.title || 'Untitled Document' }}</h4>
            <div class="text-xs text-slate-500 font-mono">Doc ID: {{ doc.doc_id }}</div>
          </div>
        </div>
      </div>
      
    </div>
    
    <!-- Empty State -->
    <div v-else class="flex-1 flex flex-col items-center justify-center p-12 border-2 border-dashed border-slate-700/50 rounded-2xl opacity-50">
      <svg class="w-16 h-16 text-slate-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z M10 7v3m0 0v3m0-3h3m-3 0H7" />
      </svg>
      <p class="text-lg font-medium text-slate-400">Enter a query to see retrieval results</p>
      <p class="text-sm text-slate-500 mt-1 max-w-md text-center">The system will display a side-by-side comparison of the document rankings before and after query expansion.</p>
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
  background: rgba(148, 163, 184, 0.2);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.4);
}
</style>
