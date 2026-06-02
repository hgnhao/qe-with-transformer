<script setup>
import { onMounted } from 'vue'
import { store } from '../store'

onMounted(() => {
  store.fetchConfig()
})

const handleConfigChange = () => {
  store.updateConfig()
}

const weightingSchemes = [
  { value: 'tf', label: 'Term Frequency (TF)' },
  { value: 'idf', label: 'Inverse Document Freq (IDF)' },
  { value: 'tf-idf', label: 'TF-IDF' },
  { value: 'tf-idf-cosine', label: 'TF-IDF + Cosine Norm' }
]

const tfVariants = [
  { value: 'raw', label: 'Raw' },
  { value: 'logarithmic', label: 'Logarithmic' },
  { value: 'binary', label: 'Binary' },
  { value: 'augmented', label: 'Augmented' }
]
</script>

<template>
  <div class="bg-slate-800/60 backdrop-blur-lg rounded-2xl border border-slate-700/50 p-6 shadow-xl relative overflow-hidden">
    <!-- Decorative gradient -->
    <div class="absolute -top-10 -right-10 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

    <h2 class="text-xl font-semibold mb-6 flex items-center gap-2">
      <svg class="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      Settings
    </h2>

    <div class="space-y-6 relative z-10">
      <!-- Preprocessing -->
      <div>
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Preprocessing</h3>
        
        <label class="flex items-center justify-between p-3 rounded-lg bg-slate-900/40 border border-slate-700/50 hover:bg-slate-700/40 transition-colors cursor-pointer group mb-3">
          <span class="text-sm font-medium text-slate-300 group-hover:text-white transition-colors">Apply Stemming</span>
          <div class="relative inline-block w-10 h-5">
            <input type="checkbox" v-model="store.config.apply_stemming" @change="handleConfigChange" class="peer sr-only">
            <div class="w-10 h-5 bg-slate-600 rounded-full peer-checked:bg-indigo-500 transition-colors duration-300"></div>
            <div class="absolute top-0.5 left-0.5 bg-white w-4 h-4 rounded-full transition-transform duration-300 peer-checked:translate-x-5 shadow"></div>
          </div>
        </label>

        <label class="flex items-center justify-between p-3 rounded-lg bg-slate-900/40 border border-slate-700/50 hover:bg-slate-700/40 transition-colors cursor-pointer group">
          <span class="text-sm font-medium text-slate-300 group-hover:text-white transition-colors">Remove Stopwords</span>
          <div class="relative inline-block w-10 h-5">
            <input type="checkbox" v-model="store.config.remove_stopwords" @change="handleConfigChange" class="peer sr-only">
            <div class="w-10 h-5 bg-slate-600 rounded-full peer-checked:bg-indigo-500 transition-colors duration-300"></div>
            <div class="absolute top-0.5 left-0.5 bg-white w-4 h-4 rounded-full transition-transform duration-300 peer-checked:translate-x-5 shadow"></div>
          </div>
        </label>
      </div>

      <hr class="border-slate-700/50">

      <!-- Weighting Scheme -->
      <div>
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Weighting Scheme</h3>
        
        <div class="space-y-3">
          <div class="flex flex-col gap-1">
            <label class="text-xs text-slate-400">Method</label>
            <select v-model="store.searchParams.weight_scheme" class="bg-slate-900/50 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-shadow">
              <option v-for="scheme in weightingSchemes" :key="scheme.value" :value="scheme.value">{{ scheme.label }}</option>
            </select>
          </div>
          
          <div class="flex flex-col gap-1" v-if="store.searchParams.weight_scheme.includes('tf')">
            <label class="text-xs text-slate-400">TF Variant</label>
            <select v-model="store.searchParams.tf_variant" class="bg-slate-900/50 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-shadow">
              <option v-for="variant in tfVariants" :key="variant.value" :value="variant.value">{{ variant.label }}</option>
            </select>
          </div>
        </div>
      </div>

      <hr class="border-slate-700/50">

      <!-- Query Expansion -->
      <div>
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Query Expansion</h3>
        
        <label class="flex items-center gap-3 p-3 rounded-lg bg-slate-900/40 border border-slate-700/50 hover:bg-slate-700/40 transition-colors cursor-pointer group mb-4">
          <input type="checkbox" v-model="store.searchParams.all_expansion_terms" class="w-4 h-4 rounded border-slate-600 text-indigo-500 focus:ring-indigo-500 bg-slate-800">
          <span class="text-sm font-medium text-slate-300 group-hover:text-white transition-colors">Add ALL similar terms</span>
        </label>
        
        <div class="space-y-2" :class="{ 'opacity-50 pointer-events-none': store.searchParams.all_expansion_terms }">
          <div class="flex justify-between items-center">
            <label class="text-sm text-slate-300">Top K Terms</label>
            <span class="text-indigo-400 font-mono text-sm bg-indigo-500/10 px-2 py-0.5 rounded">{{ store.searchParams.top_k_expansion }}</span>
          </div>
          <input 
            type="range" 
            v-model="store.searchParams.top_k_expansion" 
            min="1" max="20" 
            class="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          >
          <div class="flex justify-between text-xs text-slate-500">
            <span>1</span>
            <span>20</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Status Indicator -->
    <div class="mt-6 pt-4 border-t border-slate-700/50 flex items-center justify-between">
      <span class="text-xs text-slate-400">System Status</span>
      <div class="flex items-center gap-2">
        <span class="relative flex h-2 w-2">
          <span :class="['animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', store.config.dataset_loaded ? 'bg-emerald-400' : 'bg-amber-400']"></span>
          <span :class="['relative inline-flex rounded-full h-2 w-2', store.config.dataset_loaded ? 'bg-emerald-500' : 'bg-amber-500']"></span>
        </span>
        <span class="text-xs font-medium" :class="store.config.dataset_loaded ? 'text-emerald-400' : 'text-amber-400'">
          {{ store.config.dataset_loaded ? 'Ready' : 'Loading...' }}
        </span>
      </div>
    </div>
  </div>
</template>
