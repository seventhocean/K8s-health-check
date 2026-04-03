import apiClient from './index'

export interface ClusterSummary {
  collected_at: string
  nodes: {
    total: number
    ready: number
    not_ready: number
  }
  pods: {
    total: number
    by_phase: Record<string, number>
  }
  deployments: {
    total: number
    ready: number
    not_ready: number
  }
  resources: {
    total_cpu_capacity_millicores: number
    total_cpu_allocatable_millicores: number
    total_memory_capacity_bytes: number
    total_memory_allocatable_bytes: number
  }
}

export interface NamespaceInfo {
  namespaces: string[]
  total: number
  details: Record<string, { pods: number; deployments: number }>
}

export const clusterApi = {
  /** 获取集群概览 */
  getSummary: async (): Promise<ClusterSummary> => {
    return apiClient.get('/cluster/summary')
  },

  /** 获取命名空间列表 */
  getNamespaces: async (): Promise<NamespaceInfo> => {
    return apiClient.get('/cluster/namespaces')
  },
}
