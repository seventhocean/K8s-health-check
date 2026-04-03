import apiClient from './index'

export interface Deployment {
  name: string
  namespace: string
  labels: Record<string, string>
  replicas: {
    desired: number
    ready: number
    available: number
    unavailable: number
    updated: number
  }
  strategy: {
    type: string
    rolling_update?: {
      max_surge: string
      max_unavailable: string
    }
  }
  is_ready: boolean
  is_fully_available: boolean
  conditions: any[]
  created_at: string
}

export interface DeploymentsResponse {
  deployments: Deployment[]
  total: number
  by_namespace?: Record<string, any>
}

export const deploymentApi = {
  /** 获取所有 Deployment */
  getDeployments: async (namespace?: string): Promise<DeploymentsResponse> => {
    const params = namespace ? { namespace } : {}
    return apiClient.get('/deployments', { params })
  },

  /** 获取单个 Deployment */
  getDeployment: async (namespace: string, name: string): Promise<Deployment> => {
    return apiClient.get(`/deployments/${namespace}/${name}`)
  },

  /** 获取 Deployment 状态 */
  getDeploymentStatus: async (namespace: string, name: string) => {
    return apiClient.get(`/deployments/${namespace}/${name}/status`)
  },
}
