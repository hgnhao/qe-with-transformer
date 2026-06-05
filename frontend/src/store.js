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

      // kalau dataset belum siap, coba lagi 2 detik kemudian
      if (!this.config.dataset_loaded) {
        setTimeout(() => this.fetchConfig(), 2000)
      }
    } catch (e) {
      console.error("Gagal ambil config", e)
      // backend belum nyala, coba lagi
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
      console.error("Gagal update config", e)
    }
  }
})
