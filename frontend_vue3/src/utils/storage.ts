/**
 * LocalStorage 工具类
 */

const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_INFO_KEY = 'user_info'

export default {
  /**
   * 设置 Token
   */
  setToken(token: string) {
    localStorage.setItem(TOKEN_KEY, token)
  },

  /**
   * 获取 Token
   */
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },

  /**
   * 移除 Token
   */
  removeToken() {
    localStorage.removeItem(TOKEN_KEY)
  },

  /**
   * 设置刷新Token
   */
  setRefreshToken(token: string) {
    localStorage.setItem(REFRESH_TOKEN_KEY, token)
  },

  /**
   * 获取刷新Token
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },

  /**
   * 移除刷新Token
   */
  removeRefreshToken() {
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },

  /**
   * 设置用户信息
   */
  setUserInfo(userInfo: any) {
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo))
  },

  /**
   * 获取用户信息
   */
  getUserInfo(): any {
    const userInfo = localStorage.getItem(USER_INFO_KEY)
    return userInfo ? JSON.parse(userInfo) : null
  },

  /**
   * 移除用户信息
   */
  removeUserInfo() {
    localStorage.removeItem(USER_INFO_KEY)
  },

  /**
   * 清空所有存储
   */
  clear() {
    localStorage.clear()
  },

  /**
   * 设置任意键值
   */
  set(key: string, value: any) {
    const stringValue = typeof value === 'string' ? value : JSON.stringify(value)
    localStorage.setItem(key, stringValue)
  },

  /**
   * 获取任意键值
   */
  get(key: string): any {
    const value = localStorage.getItem(key)
    if (!value) return null
    
    try {
      return JSON.parse(value)
    } catch {
      return value
    }
  },

  /**
   * 移除任意键值
   */
  remove(key: string) {
    localStorage.removeItem(key)
  },
}

