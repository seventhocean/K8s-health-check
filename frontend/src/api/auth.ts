import apiClient from './index'

export interface User {
  id: number
  username: string
  email: string
  phone?: string
  role: 'admin' | 'developer' | 'viewer'
  is_active: boolean
  created_at: string
  last_login_at?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface RegisterRequest {
  username: string
  email: string
  phone?: string
  password: string
  role?: 'viewer' | 'developer' | 'admin'
}

export const authApi = {
  /** 用户登录 */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    return apiClient.post('/auth/login', data)
  },

  /** 用户注册 */
  register: async (data: RegisterRequest): Promise<User> => {
    return apiClient.post('/auth/register', data)
  },

  /** 获取当前用户信息 */
  getCurrentUser: async (): Promise<User> => {
    return apiClient.get('/auth/me')
  },

  /** 用户登出 */
  logout: async (): Promise<{ message: string }> => {
    return apiClient.post('/auth/logout')
  },
}
