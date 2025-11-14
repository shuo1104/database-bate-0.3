/**
 * 用户管理 API
 */
import { request } from '@/utils/request'

// 用户信息接口
export interface UserInfo {
  user_id: number
  username: string
  real_name?: string
  position?: string
  email?: string
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
  updated_at?: string
}

// 用户列表查询参数
export interface UserQueryParams {
  page?: number
  page_size?: number
  username?: string
  role?: string
  is_active?: boolean
}

// 用户列表响应
export interface UserListResponse {
  items: UserInfo[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 创建用户请求
export interface CreateUserRequest {
  username: string
  password: string
  real_name?: string
  position?: string
  email?: string
  role: 'admin' | 'user'
}

// 更新用户请求
export interface UpdateUserRequest {
  real_name?: string
  position?: string
  email?: string
  role?: 'admin' | 'user'
  is_active?: boolean
}

// 重置密码请求
export interface ResetPasswordRequest {
  new_password: string
}

/**
 * 获取用户列表
 */
export function getUserListApi(params?: UserQueryParams): Promise<UserListResponse> {
  return request({
    url: '/api/v1/auth/users',
    method: 'get',
    params
  })
}

/**
 * 创建用户
 */
export function createUserApi(data: CreateUserRequest): Promise<UserInfo> {
  return request({
    url: '/api/v1/auth/users',
    method: 'post',
    data
  })
}

/**
 * 更新用户信息
 */
export function updateUserApi(userId: number, data: UpdateUserRequest): Promise<UserInfo> {
  return request({
    url: `/api/v1/auth/users/${userId}`,
    method: 'put',
    data
  })
}

/**
 * 删除用户
 */
export function deleteUserApi(userId: number): Promise<void> {
  return request({
    url: `/api/v1/auth/users/${userId}`,
    method: 'delete'
  })
}

/**
 * 重置用户密码
 */
export function resetUserPasswordApi(userId: number, data: ResetPasswordRequest): Promise<void> {
  return request({
    url: `/api/v1/auth/users/${userId}/reset-password`,
    method: 'put',
    data
  })
}

