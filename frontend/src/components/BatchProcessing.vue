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
  <div class="h-full bg-card-bg rounded-lg border border-divider p-8 shadow-none relative overflow-hidden flex flex-col">
    <div class="relative z-10 max-w-[720px] w-full mx-auto flex flex-col gap-6 h-full">
      
      <div class="text-left">
        <h2 class="text-2xl font-semibold text-text-primary mb-2">
          Batch Processing
        </h2>
        <p class="text-text-secondary text-sm">Upload a file containing multiple queries to process them all at once.</p>
      </div>

      <!-- Upload Zone -->
      <div 
        @dragover.prevent="dragOver = true"
        @dragleave.prevent="dragOver = false"
        @drop.prevent="handleFileDrop"
        :class="['border-2 border-dashed rounded-lg p-10 text-center transition-all duration-200', dragOver ? 'border-accent-indigo bg-indigo-50/30' : 'border-divider hover:border-accent-indigo/60 bg-app-bg']"
      >
        <svg class="w-12 h-12 mx-auto mb-3 text-text-secondary" :class="{ 'text-accent-indigo animate-bounce': dragOver }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        
        <div v-if="!file">
          <p class="text-sm font-medium text-text-primary mb-1">Drag and drop your query file here</p>
          <p class="text-xs text-text-secondary mb-3">or</p>
          <label class="px-4 py-1.5 bg-card-bg hover:bg-[#F3F4F6] text-text-primary text-xs rounded border border-divider cursor-pointer transition-colors font-medium">
            Browse Files
            <input type="file" class="hidden" @change="handleFileSelect" accept=".txt">
          </label>
        </div>
        
        <div v-else class="flex flex-col items-center">
          <div class="p-3 bg-indigo-50 rounded-lg border border-indigo-100 mb-3">
            <svg class="w-6 h-6 text-accent-indigo" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p class="text-accent-indigo font-medium text-sm">{{ file.name }}</p>
          <p class="text-[10px] text-text-secondary mt-1">{{ (file.size / 1024).toFixed(2) }} KB</p>
          
          <button @click="file = null" class="mt-4 text-xs text-text-secondary hover:text-red-600 hover:underline">
            Remove file
          </button>
        </div>
      </div>

      <!-- Action Button -->
      <div class="flex justify-center">
        <button 
          @click="processBatch"
          class="px-6 py-2.5 bg-accent-indigo hover:bg-accent-hover text-white rounded-md font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
          :disabled="!file || !store.config.dataset_loaded || loading"
        >
          <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          {{ loading ? 'Processing Batch...' : 'Process Queries' }}
        </button>
      </div>
      
      <!-- Results Area -->
      <div v-if="resultText" class="flex flex-col gap-3 mt-2 animate-fade-in flex-1 min-h-[220px]">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold text-emerald-600 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Processing Complete
          </h3>
          <button 
            @click="downloadResults"
            class="px-3 py-1.5 bg-card-bg hover:bg-[#F3F4F6] text-text-primary text-xs font-semibold rounded transition-colors flex items-center gap-2 border border-divider"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download Results
          </button>
        </div>
        
        <textarea 
          readonly 
          class="w-full flex-1 bg-app-bg border border-divider rounded-lg p-4 text-xs font-mono text-text-primary focus:outline-none resize-none custom-scrollbar"
          v-model="resultText"
        ></textarea>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
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
