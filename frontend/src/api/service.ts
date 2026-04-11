import apiClient from './index'

export interface ServicePort {
  name: string
  port: number
  target_port: string
  protocol: string
}

export interface Service {
  name: string
  namespace: string
  type: string
  cluster_ip: string
  external_ip: string
  ports: ServicePort[]
  selector: Record<string, string>
  created_at: string
  labels: Record<string, string>
}

export interface ServicesResponse {
  services: Service[]
  total: number
}

export const serviceApi = {
  /** 获取 Service 列表 */
  getServices: async (namespace?: string): Promise<ServicesResponse> => {
    const params = namespace ? { namespace } : {}
    return apiClient.get('/services', { params })
  },

  /** 获取单个 Service 详情 */
  getService: async (namespace: string, name: string): Promise<Service> => {
    return apiClient.get(`/services/${namespace}/${name}`)
  },
}
