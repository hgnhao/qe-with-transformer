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
  <div class="bg-card-bg rounded-lg border border-divider p-6 shadow-none relative overflow-hidden">
    <h2 class="text-lg font-semibold text-text-primary mb-6 flex items-center gap-2">
      Settings
    </h2>

    <div class="space-y-6">
      <!-- Preprocessing -->
      <div>
        <h3 class="text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-3">Preprocessing</h3>
        
        <label class="flex items-center justify-between p-3 rounded-lg bg-app-bg border border-divider hover:bg-[#F3F4F6] transition-colors cursor-pointer group mb-3">
          <span class="text-sm font-medium text-text-secondary group-hover:text-text-primary transition-colors">Apply Stemming</span>
          <div class="relative inline-block w-10 h-5">
            <input type="checkbox" v-model="store.config.apply_stemming" @change="handleConfigChange" class="peer sr-only">
            <div class="w-10 h-5 bg-[#E5E7EB] rounded-full peer-checked:bg-accent-indigo transition-colors duration-300"></div>
            <div class="absolute top-0.5 left-0.5 bg-white w-4 h-4 rounded-full transition-transform duration-300 peer-checked:translate-x-5 shadow-sm"></div>
          </div>
        </label>

        <label class="flex items-center justify-between p-3 rounded-lg bg-app-bg border border-divider hover:bg-[#F3F4F6] transition-colors cursor-pointer group">
          <span class="text-sm font-medium text-text-secondary group-hover:text-text-primary transition-colors">Remove Stopwords</span>
          <div class="relative inline-block w-10 h-5">
            <input type="checkbox" v-model="store.config.remove_stopwords" @change="handleConfigChange" class="peer sr-only">
            <div class="w-10 h-5 bg-[#E5E7EB] rounded-full peer-checked:bg-accent-indigo transition-colors duration-300"></div>
            <div class="absolute top-0.5 left-0.5 bg-white w-4 h-4 rounded-full transition-transform duration-300 peer-checked:translate-x-5 shadow-sm"></div>
          </div>
        </label>
      </div>

      <hr class="border-divider">

      <!-- Weighting Scheme -->
      <div>
        <h3 class="text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-3">Weighting Scheme</h3>
        
        <div class="space-y-3">
          <div class="flex flex-col gap-1">
            <label class="text-xs text-text-secondary font-medium">Method</label>
            <select v-model="store.searchParams.weight_scheme" class="bg-card-bg border border-divider rounded-lg p-2.5 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-indigo transition-shadow">
              <option v-for="scheme in weightingSchemes" :key="scheme.value" :value="scheme.value">{{ scheme.label }}</option>
            </select>
          </div>
          
          <div class="flex flex-col gap-1" v-if="store.searchParams.weight_scheme.includes('tf')">
            <label class="text-xs text-text-secondary font-medium">TF Variant</label>
            <select v-model="store.searchParams.tf_variant" class="bg-card-bg border border-divider rounded-lg p-2.5 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-indigo transition-shadow">
              <option v-for="variant in tfVariants" :key="variant.value" :value="variant.value">{{ variant.label }}</option>
            </select>
          </div>
        </div>
      </div>

      <hr class="border-divider">

      <!-- Query Expansion -->
      <div>
        <h3 class="text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-3">Query Expansion</h3>
        
        <label class="flex items-center gap-3 p-3 rounded-lg bg-app-bg border border-divider hover:bg-[#F3F4F6] transition-colors cursor-pointer group mb-4">
          <input type="checkbox" v-model="store.searchParams.all_expansion_terms" class="w-4 h-4 rounded border-divider text-accent-indigo focus:ring-accent-indigo bg-card-bg">
          <span class="text-sm font-medium text-text-secondary group-hover:text-text-primary transition-colors">Add ALL similar terms</span>
        </label>
        
        <div class="space-y-2" :class="{ 'opacity-50 pointer-events-none': store.searchParams.all_expansion_terms }">
          <div class="flex justify-between items-center">
            <label class="text-sm text-text-secondary font-medium">Top K Terms</label>
            <span class="text-accent-indigo font-mono text-xs bg-indigo-50 border border-indigo-100/50 px-2 py-0.5 rounded">{{ store.searchParams.top_k_expansion }}</span>
          </div>
          <input 
            type="range" 
            v-model="store.searchParams.top_k_expansion" 
            min="1" max="20" 
            class="w-full h-1.5 bg-[#E5E7EB] rounded-lg appearance-none cursor-pointer accent-accent-indigo"
          >
          <div class="flex justify-between text-xs text-text-secondary opacity-70">
            <span>1</span>
            <span>20</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Status Indicator -->
    <div class="mt-6 pt-4 border-t border-divider flex items-center justify-between">
      <span class="text-xs text-text-secondary">System Status</span>
      <div class="flex items-center gap-2">
        <span class="relative flex h-2 w-2">
          <span :class="['animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', store.config.dataset_loaded ? 'bg-emerald-400' : 'bg-amber-400']"></span>
          <span :class="['relative inline-flex rounded-full h-2 w-2', store.config.dataset_loaded ? 'bg-emerald-500' : 'bg-amber-500']"></span>
        </span>
        <span class="text-xs font-medium" :class="store.config.dataset_loaded ? 'text-emerald-600' : 'text-amber-600'">
          {{ store.config.dataset_loaded ? 'Ready' : 'Loading...' }}
        </span>
      </div>
    </div>
  </div>
</template>
