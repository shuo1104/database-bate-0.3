/**
 * 认证工具函数
 */
import storage from './storage'

/**
 * 获取Token
 */
export function getToken(): string | null {
  return storage.getToken()
}

/**
 * 设置Token
 */
export function setToken(token: string): void {
  storage.setToken(token)
}

/**
 * 移除Token
 */
export function removeToken(): void {
  storage.removeToken()
}

/**
 * 检查是否已登录
 */
export function isLoggedIn(): boolean {
  return !!getToken()
}

/**
 * 检查是否有权限
 */
export function hasPermission(_permission: string): boolean {
  const userInfo = storage.getUserInfo()
  if (!userInfo) return false
  
  // 管理员拥有所有权限
  if (userInfo.role === 'admin') return true
  
  // 其他权限检查逻辑
  return true
}

/**
 * 检查是否是管理员
 */
export function isAdmin(): boolean {
  const userInfo = storage.getUserInfo()
  return userInfo?.role === 'admin'
}

