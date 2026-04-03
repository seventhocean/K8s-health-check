import apiClient from './index'

export interface Pod {
  name: string
  namespace: string
  phase: string
  qos_class: string
  node_name: string
  host_ip: string
  pod_ip: string
  labels: Record<string, string>
  containers: {
    count: number
    ready: number
    statuses: any[]
  }
  resources: {
    requests: {
      cpu: number
      memory: number
    }
    limits: {
      cpu: number
      memory: number
    }
  }
  created_at: string
  start_time: string
}

export interface PodsResponse {
  pods: Pod[]
  total: number
  by_namespace?: Record<string, any>
}

export const podApi = {
  /** 获取所有 Pod */
  getPods: async (namespace?: string): Promise<PodsResponse> => {
    const params = namespace ? { namespace } : {}
    return apiClient.get('/pods', { params })
  },

  /** 获取单个 Pod */
  getPod: async (namespace: string, podName: string): Promise<Pod> => {
    return apiClient.get(`/pods/${namespace}/${podName}`)
  },

  /** 获取命名空间 Pod 状态汇总 */
  getNamespacePodStatus: async (namespace: string) => {
    return apiClient.get(`/pods/namespace/${namespace}/status`)
  },
}
