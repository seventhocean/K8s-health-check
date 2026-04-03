import apiClient from './index'

export interface Node {
  name: string
  labels: Record<string, string>
  kubelet_version: string
  os_image: string
  container_runtime: string
  is_ready: boolean
  capacity: {
    cpu: number
    memory_bytes: number
    pods: number
  }
  allocatable: {
    cpu: number
    memory_bytes: number
    pods: number
  }
  conditions: Record<string, any>
  addresses: Record<string, string>
}

export interface NodesResponse {
  nodes: Node[]
  total: number
}

export const nodeApi = {
  /** 获取所有节点 */
  getNodes: async (): Promise<NodesResponse> => {
    return apiClient.get('/nodes')
  },

  /** 获取单个节点 */
  getNode: async (nodeName: string): Promise<Node> => {
    return apiClient.get(`/nodes/${nodeName}`)
  },

  /** 获取节点指标 */
  getNodeMetrics: async (nodeName: string) => {
    return apiClient.get(`/nodes/${nodeName}/metrics`)
  },
}
