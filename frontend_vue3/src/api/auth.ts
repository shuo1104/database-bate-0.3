/**
 * 认证相关API
 */
import { request } from '@/utils/request'

/**
 * 用户信息
 */
export interface UserInfo {
  user_id: number
  username: string
  real_name?: string
  position?: string
  role: string
  email?: string
  is_active: boolean
  created_at?: string
  last_login?: string
}

/**
 * 登录数据
 */
export interface LoginData {
  username: string
  password: string
}

/**
 * Token 响应
 */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

/**
 * 登录响应
 */
export interface LoginResponse {
  token: TokenResponse
  user: UserInfo
  log_id?: number  // 登录日志ID，用于心跳和登出
}

/**
 * 注册数据
 */
export interface RegisterData {
  username: string
  password: string
  real_name?: string
  email?: string
}

/**
 * 修改密码数据
 */
export interface ChangePasswordData {
  old_password: string
  new_password: string
}

/**
 * 用户登录
 */
export function loginApi(data: LoginData) {
  return request<LoginResponse>({
    url: '/api/v1/auth/login',
    method: 'post',
    data,
  })
}

/**
 * 用户注册
 */
export function registerApi(data: RegisterData) {
  return request<any>({
    url: '/api/v1/auth/register',
    method: 'post',
    data,
  })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUserInfoApi() {
  return request<UserInfo>({
    url: '/api/v1/auth/current/info',
    method: 'get',
  })
}

/**
 * 更新个人信息
 */
export interface UpdateProfileData {
  real_name?: string
  position?: string
  email?: string
}

export function updateProfileApi(data: UpdateProfileData) {
  return request<UserInfo>({
    url: '/api/v1/auth/current/profile',
    method: 'put',
    data,
  })
}

/**
 * 修改密码
 */
export function changePasswordApi(data: ChangePasswordData) {
  return request<any>({
    url: '/api/v1/auth/current/password',
    method: 'put',
    data,
  })
}

