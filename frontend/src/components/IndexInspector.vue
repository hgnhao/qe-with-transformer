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
  <div class="h-full bg-card-bg rounded-lg border border-divider p-8 shadow-none relative overflow-hidden flex flex-col">
    <div class="relative z-10 flex flex-col gap-6 h-full">
      
      <div>
        <h2 class="text-2xl font-semibold text-text-primary mb-2">
          Index Inspector
        </h2>
        <p class="text-text-secondary text-sm">View the exact inverted index entries for a specific document ID.</p>
      </div>

      <form @submit.prevent="inspectIndex" class="flex gap-4">
        <div class="relative flex-1 max-w-sm">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="w-5 h-5 text-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 21h7a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v11m0 5l4.879-4.879m0 0a3 3 0 104.243-4.242 3 3 0 00-4.243 4.242z" />
            </svg>
          </div>
          <input 
            v-model="docId" 
            type="number" 
            min="1"
            placeholder="Enter Document ID (e.g. 1)" 
            class="block w-full pl-10 pr-3 py-2 bg-card-bg border text-sm border-divider rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-indigo focus:border-transparent transition-all"
            :disabled="!store.config.dataset_loaded || loading"
          >
        </div>
        
        <button 
          type="submit" 
          class="px-6 bg-accent-indigo hover:bg-accent-hover text-white rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-accent-indigo disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          :disabled="!docId || !store.config.dataset_loaded || loading"
        >
          <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          {{ loading ? 'Inspecting...' : 'Inspect' }}
        </button>
      </form>

      <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
        {{ error }}
      </div>

      <!-- Results Table -->
      <div v-if="indexData" class="flex-1 overflow-hidden flex flex-col bg-card-bg border border-divider rounded-lg">
        <div class="px-6 py-4 border-b border-divider flex justify-between items-center bg-app-bg">
          <h3 class="font-semibold text-text-primary">Document {{ docId }} Index</h3>
          <span class="text-xs font-mono bg-card-bg border border-divider text-text-secondary px-2 py-1 rounded">Unique Terms: {{ indexData.length }}</span>
        </div>
        
        <div class="overflow-x-auto flex-1 custom-scrollbar">
          <table class="w-full text-sm text-left border-collapse">
            <thead class="text-xs text-text-secondary uppercase bg-app-bg sticky top-0 z-10 border-b border-divider">
              <tr>
                <th scope="col" class="px-6 py-3 font-mono text-[12px] font-semibold">Term</th>
                <th scope="col" class="px-6 py-3 font-mono text-[12px] font-semibold text-right">Frequency (TF)</th>
                <th scope="col" class="px-6 py-3 font-mono text-[12px] font-semibold text-right">Global Doc Freq (DF)</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-divider">
              <tr v-for="(item, idx) in indexData" :key="item.term" class="hover:bg-[#F3F4F6] transition-colors border-b border-divider last:border-0">
                <td class="px-6 py-3 font-mono text-text-primary">{{ item.term }}</td>
                <td class="px-6 py-3 text-right text-text-primary font-medium">{{ item.frequency }}</td>
                <td class="px-6 py-3 text-right text-text-secondary font-mono text-xs">{{ item.total_doc_frequency }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div v-else-if="!loading && !error" class="flex-1 flex items-center justify-center border-2 border-dashed border-divider rounded-lg opacity-70">
        <p class="text-text-secondary text-sm">Enter a Document ID to view its inverted index entries</p>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(107, 114, 128, 0.2);
  border-radius: 8px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(107, 114, 128, 0.4);
}
</style>
