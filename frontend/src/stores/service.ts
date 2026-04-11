import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { serviceApi, type Service } from '@/api/service'

export const useServiceStore = defineStore('service', () => {
  const services = ref<Service[]>([])
  const loading = ref(false)
  const currentNamespace = ref<string>('')

  const filteredServices = computed(() => {
    if (!currentNamespace.value) return services.value
    return services.value.filter(s => s.namespace === currentNamespace.value)
  })

  async function fetchServices(namespace?: string) {
    loading.value = true
    try {
      const data = await serviceApi.getServices(namespace)
      services.value = data.services || []
    } catch (error) {
      console.error('Failed to fetch services:', error)
      services.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    services,
    loading,
    currentNamespace,
    filteredServices,
    fetchServices,
  }
})
