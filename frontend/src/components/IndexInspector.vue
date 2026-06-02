<script setup>
import { ref } from 'vue'
import { api, store } from '../store'

const docId = ref('')
const loading = ref(false)
const indexData = ref(null)
const error = ref(null)

const inspectIndex = async () => {
  if (!docId.value || !store.config.dataset_loaded) return
  
  loading.value = true
  indexData.value = null
  error.value = null
  
  try {
    const res = await api.get(`/index/${docId.value}`)
    indexData.value = res.data.inverted_file
  } catch (e) {
    if (e.response && e.response.status === 404) {
      error.value = "Document not found or empty."
    } else {
      error.value = "Error fetching index data."
    }
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="h-full bg-slate-800/60 backdrop-blur-lg rounded-2xl border border-slate-700/50 p-8 shadow-xl relative overflow-hidden flex flex-col">
    <div class="absolute bottom-0 right-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
    
    <div class="relative z-10 flex flex-col gap-6 h-full">
      
      <div>
        <h2 class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400 mb-2">
          Index Inspector
        </h2>
        <p class="text-slate-400 text-sm">View the exact inverted index entries for a specific document ID.</p>
      </div>

      <form @submit.prevent="inspectIndex" class="flex gap-4">
        <div class="relative flex-1 max-w-sm">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="w-5 h-5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 21h7a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v11m0 5l4.879-4.879m0 0a3 3 0 104.243-4.242 3 3 0 00-4.243 4.242z" />
            </svg>
          </div>
          <input 
            v-model="docId" 
            type="number" 
            min="1"
            placeholder="Enter Document ID (e.g. 1)" 
            class="block w-full pl-10 pr-3 py-3 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-inner"
            :disabled="!store.config.dataset_loaded || loading"
          >
        </div>
        
        <button 
          type="submit" 
          class="px-6 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          :disabled="!docId || !store.config.dataset_loaded || loading"
        >
          <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          {{ loading ? 'Inspecting...' : 'Inspect' }}
        </button>
      </form>

      <div v-if="error" class="p-4 bg-red-900/20 border border-red-500/30 rounded-lg text-red-400 text-sm">
        {{ error }}
      </div>

      <!-- Results Table -->
      <div v-if="indexData" class="flex-1 overflow-hidden flex flex-col bg-slate-900/50 border border-slate-700/50 rounded-xl">
        <div class="px-6 py-4 border-b border-slate-700/50 flex justify-between items-center bg-slate-800/50">
          <h3 class="font-semibold text-slate-300">Document {{ docId }} Index</h3>
          <span class="text-xs font-mono bg-slate-700 text-slate-300 px-2 py-1 rounded">Unique Terms: {{ indexData.length }}</span>
        </div>
        
        <div class="overflow-x-auto flex-1 custom-scrollbar">
          <table class="w-full text-sm text-left">
            <thead class="text-xs text-slate-400 uppercase bg-slate-800/80 sticky top-0 z-10 shadow-sm">
              <tr>
                <th scope="col" class="px-6 py-3 font-medium">Term</th>
                <th scope="col" class="px-6 py-3 font-medium text-right">Frequency (TF)</th>
                <th scope="col" class="px-6 py-3 font-medium text-right">Global Doc Freq (DF)</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/50">
              <tr v-for="(item, idx) in indexData" :key="item.term" class="hover:bg-slate-800/50 transition-colors">
                <td class="px-6 py-3 font-mono text-blue-300">{{ item.term }}</td>
                <td class="px-6 py-3 text-right text-slate-300 font-medium">{{ item.frequency }}</td>
                <td class="px-6 py-3 text-right text-slate-400">{{ item.total_doc_frequency }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div v-else-if="!loading && !error" class="flex-1 flex items-center justify-center border-2 border-dashed border-slate-700/50 rounded-xl opacity-50">
        <p class="text-slate-500">Enter a Document ID to view its inverted index entries</p>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(71, 85, 105, 0.5);
  border-radius: 8px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(71, 85, 105, 0.8);
}
</style>
