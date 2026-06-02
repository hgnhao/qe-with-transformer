import { reactive } from 'vue'
import axios from 'axios'

export const api = axios.create({
  baseURL: 'http://127.0.0.1:8000'
})

export const store = reactive({
  config: {
    apply_stemming: true,
    remove_stopwords: true,
    dataset_loaded: false
  },
  searchParams: {
    weight_scheme: 'tf',
    tf_variant: 'raw',
    top_k_expansion: 5,
    all_expansion_terms: false
  },
  async fetchConfig() {
    try {
      const res = await api.get('/config')
      this.config = res.data
      
      // If dataset is still loading on the backend, poll again in 2 seconds
      if (!this.config.dataset_loaded) {
        setTimeout(() => this.fetchConfig(), 2000)
      }
    } catch (e) {
      console.error("Error fetching config", e)
      // Retry in 2 seconds if backend is down
      setTimeout(() => this.fetchConfig(), 2000)
    }
  },
  async updateConfig() {
    try {
      const res = await api.post('/config', {
        apply_stemming: this.config.apply_stemming,
        remove_stopwords: this.config.remove_stopwords
      })
      this.config = res.data.config
    } catch (e) {
      console.error("Error updating config", e)
    }
  }
})
