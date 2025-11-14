/**
 * 错误处理工具
 * 提供统一的错误处理、消息去重、错误分类等功能
 */
import { ElMessage, ElMessageBox, type MessageHandler } from 'element-plus'

// ==================== 类型定义 ====================
export type ErrorType = 'network' | 'validation' | 'business' | 'auth' | 'system'
export type ErrorSeverity = 'error' | 'warning' | 'info'

export interface AppError {
  code: number
  message: string
  type: ErrorType
  severity: ErrorSeverity
  details?: any
  timestamp: number
  userId?: string
  path?: string
  canRetry?: boolean
}

interface ErrorMessageCache {
  hash: string
  timestamp: number
  messageInstance?: MessageHandler
}

// ==================== 配置 ====================
const ERROR_CONFIG = {
  // 消息去重时间窗口（毫秒）
  dedupeWindow: 3000,
  // 最大缓存消息数
  maxCacheSize: 50,
  // 是否在开发环境输出详细日志
  verboseLogging: import.meta.env.DEV,
}

// ==================== 状态管理 ====================
// 错误消息缓存（用于去重）
const errorMessageCache: Map<string, ErrorMessageCache> = new Map()

// 当前显示的消息实例
const activeMessages: Set<MessageHandler> = new Set()

// ==================== 工具函数 ====================

/**
 * 生成消息指纹（用于去重）
 */
function generateMessageHash(message: string, code?: number): string {
  return `${code || 0}-${message.substring(0, 100)}`
}

/**
 * 清理过期的缓存消息
 */
function cleanExpiredCache() {
  const now = Date.now()
  const expiredKeys: string[] = []
  
  errorMessageCache.forEach((cache, hash) => {
    if (now - cache.timestamp > ERROR_CONFIG.dedupeWindow) {
      expiredKeys.push(hash)
    }
  })
  
  expiredKeys.forEach(key => errorMessageCache.delete(key))
  
  // 如果缓存过大，删除最旧的条目
  if (errorMessageCache.size > ERROR_CONFIG.maxCacheSize) {
    const sorted = Array.from(errorMessageCache.entries())
      .sort((a, b) => a[1].timestamp - b[1].timestamp)
    
    const toDelete = sorted.slice(0, errorMessageCache.size - ERROR_CONFIG.maxCacheSize)
    toDelete.forEach(([key]) => errorMessageCache.delete(key))
  }
}

/**
 * 检查消息是否为重复
 */
function isDuplicateMessage(hash: string): boolean {
  cleanExpiredCache()
  
  const cache = errorMessageCache.get(hash)
  if (!cache) {
    return false
  }
  
  const now = Date.now()
  const timeSinceLastShow = now - cache.timestamp
  
  return timeSinceLastShow < ERROR_CONFIG.dedupeWindow
}

/**
 * 记录消息到缓存
 */
function cacheMessage(hash: string, messageInstance?: MessageHandler) {
  errorMessageCache.set(hash, {
    hash,
    timestamp: Date.now(),
    messageInstance,
  })
}

/**
 * 获取当前用户ID（如果有）
 */
function getCurrentUserId(): string | undefined {
  try {
    const userStore = localStorage.getItem('user')
    if (userStore) {
      const user = JSON.parse(userStore)
      return user.userId || user.username
    }
  } catch (error) {
    // 忽略错误
  }
  return undefined
}

/**
 * 日志输出（仅开发环境）
 */
function devLog(level: 'error' | 'warn' | 'info', message: string, data?: any) {
  if (!ERROR_CONFIG.verboseLogging) return
  
  const logFn = level === 'error' ? console.error : level === 'warn' ? console.warn : console.log
  const emoji = level === 'error' ? '❌' : level === 'warn' ? '⚠️' : 'ℹ️'
  
  logFn(`${emoji} [ErrorHandler] ${message}`, data || '')
}

// ==================== 核心错误处理函数 ====================

/**
 * 创建标准错误对象
 */
export function createAppError(
  type: ErrorType,
  message: string,
  code: number = 500,
  options?: {
    severity?: ErrorSeverity
    details?: any
    canRetry?: boolean
  }
): AppError {
  return {
    code,
    message,
    type,
    severity: options?.severity || 'error',
    details: options?.details,
    timestamp: Date.now(),
    userId: getCurrentUserId(),
    path: window.location.pathname,
    canRetry: options?.canRetry || false,
  }
}

/**
 * 显示错误消息（带去重）
 */
export function showErrorMessage(
  message: string,
  options?: {
    code?: number
    type?: 'error' | 'warning' | 'info' | 'success'
    duration?: number
    showClose?: boolean
    allowDuplicate?: boolean
  }
): MessageHandler | null {
  const {
    code,
    type = 'error',
    duration = 3000,
    showClose = true,
    allowDuplicate = false,
  } = options || {}
  
  // 检查是否为重复消息
  const hash = generateMessageHash(message, code)
  if (!allowDuplicate && isDuplicateMessage(hash)) {
    devLog('info', 'Duplicate message blocked', { message, hash })
    return null
  }
  
  // 显示消息
  const messageInstance = ElMessage({
    message,
    type,
    duration,
    showClose,
    onClose: () => {
      activeMessages.delete(messageInstance)
    },
  })
  
  // 缓存消息
  cacheMessage(hash, messageInstance)
  activeMessages.add(messageInstance)
  
  devLog('info', `Message shown: ${message}`)
  
  return messageInstance
}

/**
 * 处理 HTTP 错误
 */
export function handleHttpError(
  status: number,
  data: any,
  options?: {
    silent?: boolean
    customMessage?: string
  }
): AppError {
  const { silent = false, customMessage } = options || {}
  
  // 提取错误消息
  const message = customMessage || data?.msg || data?.detail || data?.message || 'Request failed'
  
  // 创建错误对象
  const error = createAppError('network', message, status, {
    severity: status >= 500 ? 'error' : 'warning',
    details: data,
  })
  
  // 显示消息（除非 silent）
  if (!silent) {
    const messageType = status >= 500 ? 'error' : status >= 400 ? 'warning' : 'info'
    showErrorMessage(message, { code: status, type: messageType })
  }
  
  devLog('error', `HTTP Error [${status}]`, error)
  
  return error
}

/**
 * 处理业务逻辑错误
 */
export function handleBusinessError(
  message: string,
  options?: {
    code?: number
    silent?: boolean
    canRetry?: boolean
    details?: any
  }
): AppError {
  const { code = 400, silent = false, canRetry = false, details } = options || {}
  
  const error = createAppError('business', message, code, {
    severity: 'warning',
    canRetry,
    details,
  })
  
  if (!silent) {
    showErrorMessage(message, { code, type: 'warning' })
  }
  
  devLog('warn', 'Business Error', error)
  
  return error
}

/**
 * 处理验证错误
 */
export function handleValidationError(
  message: string,
  errors?: any[]
): AppError {
  const error = createAppError('validation', message, 422, {
    severity: 'warning',
    details: { errors },
  })
  
  showErrorMessage(message, { code: 422, type: 'warning' })
  
  devLog('warn', 'Validation Error', error)
  
  return error
}

/**
 * 处理认证错误
 */
export function handleAuthError(
  message: string = 'Authentication failed'
): AppError {
  const error = createAppError('auth', message, 401, {
    severity: 'error',
  })
  
  // 认证错误通常由 request.ts 处理，这里不显示消息
  devLog('error', 'Auth Error', error)
  
  return error
}

/**
 * 处理系统错误
 */
export function handleSystemError(
  message: string = 'System error occurred',
  originalError?: Error
): AppError {
  const error = createAppError('system', message, 500, {
    severity: 'error',
    details: {
      originalError: originalError?.message,
      stack: originalError?.stack,
    },
  })
  
  showErrorMessage(message, { code: 500, type: 'error' })
  
  devLog('error', 'System Error', error)
  console.error('Original Error:', originalError)
  
  return error
}

/**
 * 显示确认对话框（带错误上下文）
 */
export function showErrorDialog(
  message: string,
  options?: {
    title?: string
    confirmText?: string
    cancelText?: string
    showCancel?: boolean
    onConfirm?: () => void | Promise<void>
    onCancel?: () => void
  }
): Promise<void> {
  const {
    title = 'Error',
    confirmText = 'OK',
    cancelText = 'Cancel',
    showCancel = false,
    onConfirm,
    onCancel,
  } = options || {}
  
  return ElMessageBox.confirm(message, title, {
    confirmButtonText: confirmText,
    cancelButtonText: cancelText,
    type: 'error',
    showCancelButton: showCancel,
    closeOnClickModal: false,
  })
    .then(async () => {
      if (onConfirm) {
        await onConfirm()
      }
    })
    .catch(() => {
      if (onCancel) {
        onCancel()
      }
    })
}

/**
 * 显示可重试的错误对话框
 */
export function showRetryDialog(
  message: string,
  retryFn: () => void | Promise<void>
): Promise<void> {
  return showErrorDialog(message, {
    title: 'Operation Failed',
    confirmText: 'Retry',
    cancelText: 'Cancel',
    showCancel: true,
    onConfirm: retryFn,
  })
}

/**
 * 关闭所有错误消息
 */
export function closeAllMessages() {
  activeMessages.forEach(message => {
    message.close()
  })
  activeMessages.clear()
}

/**
 * 清空消息缓存
 */
export function clearMessageCache() {
  errorMessageCache.clear()
  devLog('info', 'Message cache cleared')
}

/**
 * 从 Axios 错误中提取错误信息
 */
export function extractErrorFromAxios(error: any): {
  message: string
  code: number
  type: ErrorType
} {
  const status = error.response?.status || 500
  const data = error.response?.data
  
  let message = 'Unknown error'
  let type: ErrorType = 'system'
  
  // 提取消息
  if (data?.msg) {
    message = data.msg
  } else if (data?.detail) {
    message = data.detail
  } else if (data?.message) {
    message = data.message
  } else if (error.message) {
    message = error.message
  }
  
  // 确定错误类型
  if (status === 401) {
    type = 'auth'
  } else if (status === 422) {
    type = 'validation'
  } else if (status >= 400 && status < 500) {
    type = 'business'
  } else if (status >= 500) {
    type = 'network'
  }
  
  return { message, code: status, type }
}

// ==================== 导出默认对象 ====================
export default {
  createAppError,
  showErrorMessage,
  handleHttpError,
  handleBusinessError,
  handleValidationError,
  handleAuthError,
  handleSystemError,
  showErrorDialog,
  showRetryDialog,
  closeAllMessages,
  clearMessageCache,
  extractErrorFromAxios,
}

