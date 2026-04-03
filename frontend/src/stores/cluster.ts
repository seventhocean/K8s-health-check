import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { clusterApi, type ClusterSummary } from '@/api/cluster'

export const useClusterStore = defineStore('cluster', () => {
  const summary = ref<ClusterSummary | null>(null)
  const loading = ref(false)
  const lastUpdated = ref<Date | null>(null)

  const nodeReadyRate = computed(() => {
    if (!summary.value?.nodes.total) return 0
    return (summary.value.nodes.ready / summary.value.nodes.total) * 100
  })

  const podRunningRate = computed(() => {
    if (!summary.value?.pods.total) return 0
    const running = summary.value.pods.by_phase?.Running || 0
    return (running / summary.value.pods.total) * 100
  })

  async function fetchSummary() {
    loading.value = true
    try {
      summary.value = await clusterApi.getSummary()
      lastUpdated.value = new Date()
    } catch (error) {
      console.error('Failed to fetch cluster summary:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    summary,
    loading,
    lastUpdated,
    nodeReadyRate,
    podRunningRate,
    fetchSummary,
  }
})
