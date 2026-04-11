import { defineStore } from 'pinia'
import { ref } from 'vue'
import { namespaceApi, type Namespace } from '@/api/namespace'

export const useNamespaceStore = defineStore('namespace', () => {
  const namespaces = ref<Namespace[]>([])
  const loading = ref(false)

  async function fetchNamespaces() {
    loading.value = true
    try {
      const data = await namespaceApi.getNamespaces()
      namespaces.value = data.namespaces || []
    } catch (error) {
      console.error('Failed to fetch namespaces:', error)
      namespaces.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    namespaces,
    loading,
    fetchNamespaces,
  }
})
