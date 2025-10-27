/**
 * 用户管理API
 */
import request from '@/utils/request'

/**
 * 用户列表查询参数
 */
export interface UserListQuery {
  page: number
  page_size: number
  username?: string
  role?: string
  is_active?: boolean
}

/**
 * 用户信息
 */
export interface UserInfo {
  user_id: number
  username: string
  real_name?: string
  position?: string
  email?: string
  role: string
  is_active: boolean
  created_at?: string
  last_login?: string
}

/**
 * 创建用户请求
 */
export interface CreateUserRequest {
  username: string
  password: string
  real_name?: string
  position?: string
  email?: string
  role: string
}

/**
 * 更新用户请求
 */
export interface UpdateUserRequest {
  real_name?: string
  position?: string
  email?: string
  role?: string
  is_active?: boolean
}

/**
 * 重置密码请求
 */
export interface ResetPasswordRequest {
  new_password: string
}

/**
 * 用户列表响应
 */
export interface UserListResponse {
  items: UserInfo[]
  total: number
  page: number
  page_size: number
}

/**
 * 获取用户列表
 */
export function getUserListApi(params: UserListQuery) {
  return request<UserListResponse>({
    url: '/api/v1/auth/users',
    method: 'get',
    params,
  })
}

/**
 * 创建用户
 */
export function createUserApi(data: CreateUserRequest) {
  return request<UserInfo>({
    url: '/api/v1/auth/users',
    method: 'post',
    data,
  })
}

/**
 * 更新用户
 */
export function updateUserApi(userId: number, data: UpdateUserRequest) {
  return request<UserInfo>({
    url: `/api/v1/auth/users/${userId}`,
    method: 'put',
    data,
  })
}

/**
 * 删除用户
 */
export function deleteUserApi(userId: number) {
  return request({
    url: `/api/v1/auth/users/${userId}`,
    method: 'delete',
  })
}

/**
 * 重置用户密码
 */
export function resetUserPasswordApi(userId: number, data: ResetPasswordRequest) {
  return request({
    url: `/api/v1/auth/users/${userId}/reset-password`,
    method: 'put',
    data,
  })
}

