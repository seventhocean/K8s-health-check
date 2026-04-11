import apiClient from './index'

export interface Namespace {
  name: string
  status: string
  created_at: string
  labels: Record<string, string>
}

export interface NamespacesResponse {
  namespaces: Namespace[]
  total: number
}

export const namespaceApi = {
  /** 获取命名空间列表 */
  getNamespaces: async (): Promise<NamespacesResponse> => {
    return apiClient.get('/namespaces')
  },

  /** 获取单个命名空间详情 */
  getNamespace: async (name: string): Promise<Namespace> => {
    return apiClient.get(`/namespaces/${name}`)
  },
}
