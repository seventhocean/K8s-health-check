import { defineStore } from 'pinia'
import { ref } from 'vue'
import { nodeApi, type Node } from '@/api/node'

export const useNodeStore = defineStore('nodes', () => {
  const nodes = ref<Node[]>([])
  const loading = ref(false)
  const lastUpdated = ref<Date | null>(null)

  async function fetchNodes(forceRefresh = false) {
    loading.value = true
    try {
      const data = await nodeApi.getNodes()
      nodes.value = data.nodes || []
      lastUpdated.value = new Date()
    } catch (error) {
      console.error('Failed to fetch nodes:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchNode(name: string) {
    try {
      return await nodeApi.getNode(name)
    } catch (error) {
      console.error(`Failed to fetch node ${name}:`, error)
      throw error
    }
  }

  return {
    nodes,
    loading,
    lastUpdated,
    fetchNodes,
    fetchNode,
  }
})
