/**
 * Axios Request Wrapper
 * 企业级请求拦截器 - 包含完整的错误处理、请求重试、日志记录
 */
import axios, { type AxiosInstance, type AxiosResponse, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getToken, removeToken } from './auth'
import storage from './storage'
import { logRequest, logResponse, logRequestError, logRetry } from './logger'

// ==================== 全局状态管理 ====================
// 全局401锁，防止并发请求时重复弹窗
let is401DialogShowing = false

// ==================== 配置常量 ====================
// 登录接口路径（用于判断是否为登录请求）
const LOGIN_URL = '/api/v1/auth/login'

// 需要重试的HTTP状态码
const RETRY_STATUS_CODES = [408, 429, 500, 502, 503, 504]

// 请求重试配置
const RETRY_CONFIG = {
  maxRetries: 2,        // 最大重试次数
  retryDelay: 1000,     // 重试延迟（毫秒）
  retryStatusCodes: RETRY_STATUS_CODES
}

// ==================== 辅助函数 ====================
/**
 * 延迟函数（用于请求重试）
 */
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * 判断是否需要重试
 */
function shouldRetry(error: AxiosError): boolean {
  const config = error.config as any
  const status = error.response?.status
  
  // 如果config不存在，不重试
  if (!config) {
    return false
  }
  
  // 初始化重试计数器（如果不存在）
  if (typeof config.__retryCount !== 'number') {
    config.__retryCount = 0
  }
  
  // 如果已经重试过最大次数，不再重试
  if (config.__retryCount >= RETRY_CONFIG.maxRetries) {
    return false
  }
  
  // 检查状态码是否在重试列表中
  if (status && RETRY_CONFIG.retryStatusCodes.includes(status)) {
    return true
  }
  
  // 网络错误也重试
  if (!error.response && error.message.includes('Network Error')) {
    return true
  }
  
  return false
}

/**
 * 获取友好的错误消息
 */
function getErrorMessage(error: AxiosError): string {
  const data = error.response?.data as any
  const status = error.response?.status
  
  // 优先使用服务器返回的错误信息
  if (data?.msg) return data.msg
  if (data?.detail) return data.detail
  if (data?.message) return data.message
  
  // 根据状态码返回默认消息
  switch (status) {
    case 400:
      return 'Invalid request parameters'
    case 401:
      return 'Authentication failed'
    case 403:
      return 'No permission to access this resource'
    case 404:
      return 'Requested resource does not exist'
    case 408:
      return 'Request timeout'
    case 429:
      return 'Too many requests, please try again later'
    case 500:
      return 'Server error'
    case 502:
      return 'Gateway error'
    case 503:
      return 'Service temporarily unavailable'
    case 504:
      return 'Gateway timeout'
    default:
      return error.message || 'Unknown error'
  }
}

// ==================== 创建 Axios 实例 ====================
const service: AxiosInstance = axios.create({
  baseURL: '', // No baseURL, API paths already include full path
  timeout: 50000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

// ==================== 请求拦截器 ====================
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加认证Token
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 初始化重试计数器
    if (!(config as any).__retryCount) {
      (config as any).__retryCount = 0
    }
    
    // 添加请求时间戳（用于计算请求耗时）
    (config as any).__requestStartTime = Date.now()
    
    // 记录请求日志（使用日志工具）
    logRequest(config.method?.toUpperCase() || 'UNKNOWN', config.url || '', config)
    
    return config
  },
  (error: AxiosError) => {
    // 记录错误日志（使用日志工具）
    const method = error.config?.method?.toUpperCase() || 'UNKNOWN'
    const url = error.config?.url || 'UNKNOWN'
    logRequestError(method, url, error.response?.status, error)
    return Promise.reject(error)
  }
)

// ==================== 响应拦截器 ====================
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 计算请求耗时
    const requestTime = Date.now() - (response.config as any).__requestStartTime
    
    // 记录响应日志（使用日志工具）
    logResponse(
      response.config.method?.toUpperCase() || 'UNKNOWN',
      response.config.url || '',
      response.status,
      requestTime,
      response.data
    )
    
    const { code, msg, data } = response.data

    // 返回二进制数据（文件下载等）
    if (response.config.responseType === 'blob') {
      return response.data
    }

    // 成功响应
    if (code === 200 || code === 0) {
      return data
    }

    // 业务错误
    const errorMsg = msg || 'System error'
    ElMessage.error(errorMsg)
    return Promise.reject(new Error(errorMsg))
  },
  async (error: AxiosError) => {
    // 记录错误日志（使用日志工具）
    const method = error.config?.method?.toUpperCase() || 'UNKNOWN'
    const url = error.config?.url || 'UNKNOWN'
    logRequestError(method, url, error.response?.status, error)
    
    // ==================== 请求重试机制 ====================
    // 判断是否需要重试
    if (shouldRetry(error)) {
      const config = error.config as any
      config.__retryCount += 1
      
      // 记录重试日志
      logRetry(config.url, config.__retryCount, RETRY_CONFIG.maxRetries)
      
      // 等待后重试
      await delay(RETRY_CONFIG.retryDelay * config.__retryCount)
      return service(config)
    }
    
    // ==================== HTTP 错误处理 ====================
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 判断是否为登录请求（通过URL判断更准确）
          const requestUrl = error.config?.url || ''
          const isLoginRequest = requestUrl.includes(LOGIN_URL)
          
          if (isLoginRequest) {
            // 登录失败 - 显示服务器返回的错误信息
            const errorMsg = (data as any)?.detail || (data as any)?.msg || 'Incorrect username or password'
            ElMessage.error(errorMsg)
          } else {
            // Token 过期或无效 - 显示会话过期对话框
            // 使用全局锁防止并发请求时重复弹窗
            if (!is401DialogShowing) {
              is401DialogShowing = true
              
              ElMessageBox.confirm(
                'Your session has expired. Please login again to continue.',
                'Session Expired',
                {
                  confirmButtonText: 'Re-login',
                  cancelButtonText: 'Cancel',
                  type: 'warning',
                  closeOnClickModal: false,
                  closeOnPressEscape: false,
                  showClose: false,
                  distinguishCancelAndClose: true,
                }
              )
                .then(() => {
                  // 用户点击"重新登录"
                  removeToken()
                  storage.clear()
                  window.location.href = '/login'
                })
                .catch(() => {
                  // 用户点击"取消"，也需要跳转到登录页
                  removeToken()
                  storage.clear()
                  window.location.href = '/login'
                })
                .finally(() => {
                  // 重置锁状态
                  is401DialogShowing = false
                })
            }
          }
          break
          
        case 403:
          ElMessage.error('No permission to access this resource')
          break
          
        case 404:
          ElMessage.error('Requested resource does not exist')
          break
          
        case 422:
          // 数据验证错误 - 显示详细错误信息
          const validationMsg = getErrorMessage(error)
          ElMessage.error(validationMsg)
          break
          
        case 429:
          ElMessage.warning('Too many requests, please slow down')
          break
          
        case 500:
        case 502:
        case 503:
        case 504:
          // 服务器错误 - 使用友好的错误消息
          const serverErrorMsg = getErrorMessage(error)
          ElMessage.error(serverErrorMsg)
          break
          
        default:
          const defaultErrorMsg = getErrorMessage(error)
          ElMessage.error(defaultErrorMsg)
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      ElMessage.error('Network request failed, please check your connection')
    } else {
      // 请求配置错误
      ElMessage.error('Request configuration error')
    }

    return Promise.reject(error)
  }
)

// Export axios instance with type override
export default service

// Type-safe request wrapper
export function request<T = any>(config: any): Promise<T> {
  return service(config)
}

