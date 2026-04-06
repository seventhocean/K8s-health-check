import apiClient from './index'
import type { User } from './auth'

export interface AuditLog {
  id: number
  user_id?: number
  username?: string
  action: string
  resource_type: string
  resource_name: string
  namespace?: string
  details?: string
  status: string
  ip_address?: string
  created_at: string
}

export const userApi = {
  /** 获取用户列表 */
  getUsers: async (params?: {
    skip?: number
    limit?: number
    keyword?: string
    role?: string
    is_active?: boolean
  }): Promise<User[]> => {
    return apiClient.get('/users', { params })
  },

  /** 获取用户详情 */
  getUser: async (userId: number): Promise<User> => {
    return apiClient.get(`/users/${userId}`)
  },

  /** 创建用户 */
  createUser: async (data: {
    username: string
    email: string
    phone?: string
    password: string
    role?: string
  }): Promise<User> => {
    return apiClient.post('/users', data)
  },

  /** 更新用户 */
  updateUser: async (
    userId: number,
    data: {
      email?: string
      phone?: string
      role?: string
      is_active?: boolean
    }
  ): Promise<User> => {
    return apiClient.put(`/users/${userId}`, data)
  },

  /** 删除用户 */
  deleteUser: async (userId: number): Promise<void> => {
    return apiClient.delete(`/users/${userId}`)
  },

  /** 获取审计日志 */
  getAuditLogs: async (params?: {
    skip?: number
    limit?: number
    user_id?: number
    action?: string
    resource_type?: string
  }): Promise<AuditLog[]> => {
    return apiClient.get('/users/audit/logs', { params })
  },
}
