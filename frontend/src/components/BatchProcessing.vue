<script setup>
import { ref } from 'vue'
import { api, store } from '../store'

const file = ref(null)
const loading = ref(false)
const resultText = ref(null)
const dragOver = ref(false)

const handleFileDrop = (e) => {
  dragOver.value = false
  const droppedFile = e.dataTransfer.files[0]
  if (droppedFile) {
    file.value = droppedFile
  }
}

const handleFileSelect = (e) => {
  const selectedFile = e.target.files[0]
  if (selectedFile) {
    file.value = selectedFile
  }
}

const processBatch = async () => {
  if (!file.value || !store.config.dataset_loaded) return
  
  loading.value = true
  resultText.value = null
  
  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('weight_scheme', store.searchParams.weight_scheme)
  formData.append('tf_variant', store.searchParams.tf_variant)
  formData.append('top_k_expansion', store.searchParams.top_k_expansion)
  formData.append('all_expansion_terms', store.searchParams.all_expansion_terms)
  
  try {
    const res = await api.post('/search/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    resultText.value = res.data.result_text
  } catch (e) {
    console.error(e)
    alert("Error processing batch file.")
  } finally {
    loading.value = false
  }
}

const downloadResults = () => {
  if (!resultText.value) return
  
  const blob = new Blob([resultText.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `batch_results_${new Date().getTime()}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="h-full bg-slate-800/60 backdrop-blur-lg rounded-2xl border border-slate-700/50 p-8 shadow-xl relative overflow-hidden">
    <div class="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
    
    <div class="relative z-10 max-w-3xl mx-auto flex flex-col gap-8 h-full">
      
      <div class="text-center">
        <h2 class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 mb-2">
          Batch Processing
        </h2>
        <p class="text-slate-400">Upload a file containing multiple queries to process them all at once.</p>
      </div>

      <!-- Upload Zone -->
      <div 
        @dragover.prevent="dragOver = true"
        @dragleave.prevent="dragOver = false"
        @drop.prevent="handleFileDrop"
        :class="['border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300', dragOver ? 'border-indigo-500 bg-indigo-500/10' : 'border-slate-600 hover:border-slate-500 bg-slate-900/50']"
      >
        <svg class="w-16 h-16 mx-auto mb-4 text-slate-400" :class="{ 'text-indigo-400 animate-bounce': dragOver }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        
        <div v-if="!file">
          <p class="text-lg font-medium text-slate-300 mb-1">Drag and drop your query file here</p>
          <p class="text-sm text-slate-500 mb-4">or</p>
          <label class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg cursor-pointer transition-colors border border-slate-700">
            Browse Files
            <input type="file" class="hidden" @change="handleFileSelect" accept=".txt">
          </label>
        </div>
        
        <div v-else class="flex flex-col items-center">
          <div class="p-3 bg-indigo-500/20 rounded-lg border border-indigo-500/30 mb-3">
            <svg class="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p class="text-indigo-300 font-medium">{{ file.name }}</p>
          <p class="text-xs text-slate-500 mt-1">{{ (file.size / 1024).toFixed(2) }} KB</p>
          
          <button @click="file = null" class="mt-4 text-xs text-slate-400 hover:text-red-400 underline decoration-slate-600 underline-offset-4">
            Remove file
          </button>
        </div>
      </div>

      <!-- Action Button -->
      <div class="flex justify-center">
        <button 
          @click="processBatch"
          class="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-bold shadow-lg shadow-indigo-500/25 transition-all focus:ring-4 focus:ring-indigo-500/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-lg"
          :disabled="!file || !store.config.dataset_loaded || loading"
        >
          <span v-if="loading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          {{ loading ? 'Processing Batch...' : 'Process Queries' }}
        </button>
      </div>
      
      <!-- Results Area -->
      <div v-if="resultText" class="flex flex-col gap-4 mt-4 animate-fade-in flex-1 min-h-[200px]">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-emerald-400 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Processing Complete
          </h3>
          <button 
            @click="downloadResults"
            class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2 border border-slate-600"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download Results
          </button>
        </div>
        
        <textarea 
          readonly 
          class="w-full flex-1 bg-slate-900 border border-slate-700 rounded-xl p-4 text-sm font-mono text-slate-300 focus:outline-none resize-none custom-scrollbar"
          v-model="resultText"
        ></textarea>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(71, 85, 105, 0.5);
  border-radius: 8px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(71, 85, 105, 0.8);
}
</style>
