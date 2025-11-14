/**
 * Request Logger Utility
 * 请求日志工具 - 支持日志级别控制和敏感信息过滤
 */

// ==================== 日志级别 ====================
export enum LogLevel {
  NONE = 0,    // 不输出任何日志
  ERROR = 1,   // 仅错误
  WARN = 2,    // 错误 + 警告
  INFO = 3,    // 错误 + 警告 + 信息
  DEBUG = 4,   // 所有日志（包括详细信息）
}

// ==================== 日志配置 ====================
interface LoggerConfig {
  level: LogLevel
  enableColors: boolean
  slowRequestThreshold: number  // 慢请求阈值（毫秒）
  filterSensitiveHeaders: boolean
}

// 从环境变量读取日志级别
const getLogLevelFromEnv = (): LogLevel => {
  const envLevel = import.meta.env.VITE_LOG_LEVEL?.toUpperCase()
  
  switch (envLevel) {
    case 'NONE':
      return LogLevel.NONE
    case 'ERROR':
      return LogLevel.ERROR
    case 'WARN':
      return LogLevel.WARN
    case 'INFO':
      return LogLevel.INFO
    case 'DEBUG':
      return LogLevel.DEBUG
    default:
      // 开发环境默认 INFO，生产环境默认 WARN
      return import.meta.env.DEV ? LogLevel.INFO : LogLevel.WARN
  }
}

// 默认配置
const defaultConfig: LoggerConfig = {
  level: getLogLevelFromEnv(),
  enableColors: true,
  slowRequestThreshold: 3000,  // 3秒
  filterSensitiveHeaders: true,
}

let config: LoggerConfig = { ...defaultConfig }

// ==================== 配置管理 ====================
export const setLogLevel = (level: LogLevel) => {
  config.level = level
}

export const setLoggerConfig = (newConfig: Partial<LoggerConfig>) => {
  config = { ...config, ...newConfig }
}

export const getLoggerConfig = (): LoggerConfig => {
  return { ...config }
}

// ==================== 敏感信息过滤 ====================
/**
 * 过滤敏感的 Header 信息
 */
const filterSensitiveHeaders = (headers: any): any => {
  if (!config.filterSensitiveHeaders || !headers) {
    return headers
  }

  const filtered: any = {}
  const sensitiveKeys = ['authorization', 'cookie', 'x-api-key', 'x-auth-token']

  for (const [key, value] of Object.entries(headers)) {
    const lowerKey = key.toLowerCase()
    
    if (sensitiveKeys.includes(lowerKey)) {
      // 只显示前几个字符
      if (typeof value === 'string' && value.length > 10) {
        filtered[key] = `${value.substring(0, 10)}...***`
      } else {
        filtered[key] = '***'
      }
    } else {
      filtered[key] = value
    }
  }

  return filtered
}

/**
 * 截断过长的数据
 */
const truncateData = (data: any, maxLength: number = 200): any => {
  if (!data) return data
  
  const str = JSON.stringify(data)
  if (str.length <= maxLength) {
    return data
  }
  
  return `${str.substring(0, maxLength)}... (truncated, total ${str.length} chars)`
}

// ==================== 日志输出函数 ====================
/**
 * DEBUG 级别日志（最详细）
 */
export const logDebug = (message: string, data?: any) => {
  if (config.level < LogLevel.DEBUG) return

  if (config.enableColors) {
    console.log(
      `%c[DEBUG] ${message}`,
      'color: #909399; font-weight: normal',
      data || ''
    )
  } else {
    console.log(`[DEBUG] ${message}`, data || '')
  }
}

/**
 * INFO 级别日志
 */
export const logInfo = (message: string, data?: any) => {
  if (config.level < LogLevel.INFO) return

  if (config.enableColors) {
    console.log(
      `%c[INFO] ${message}`,
      'color: #409eff; font-weight: normal',
      data || ''
    )
  } else {
    console.log(`[INFO] ${message}`, data || '')
  }
}

/**
 * WARN 级别日志
 */
export const logWarn = (message: string, data?: any) => {
  if (config.level < LogLevel.WARN) return

  if (config.enableColors) {
    console.warn(
      `%c[WARN] ${message}`,
      'color: #e6a23c; font-weight: bold',
      data || ''
    )
  } else {
    console.warn(`[WARN] ${message}`, data || '')
  }
}

/**
 * ERROR 级别日志
 */
export const logError = (message: string, data?: any) => {
  if (config.level < LogLevel.ERROR) return

  if (config.enableColors) {
    console.error(
      `%c[ERROR] ${message}`,
      'color: #f56c6c; font-weight: bold',
      data || ''
    )
  } else {
    console.error(`[ERROR] ${message}`, data || '')
  }
}

// ==================== 请求日志专用函数 ====================
/**
 * 记录请求日志
 */
export const logRequest = (method: string, url: string, config?: any) => {
  if (config.level < LogLevel.INFO) return

  const message = `${method} ${url}`

  // DEBUG 级别显示详细信息
  if (config.level >= LogLevel.DEBUG && config) {
    logDebug(message, {
      params: config.params,
      data: truncateData(config.data, 300),
      headers: filterSensitiveHeaders(config.headers),
    })
  } else {
    // INFO 级别仅显示简单信息
    logInfo(message)
  }
}

/**
 * 记录响应日志
 */
export const logResponse = (
  method: string,
  url: string,
  status: number,
  duration: number,
  data?: any
) => {
  if (config.level < LogLevel.INFO) return

  const message = `${method} ${url} - ${status} (${duration}ms)`

  // 检查是否为慢请求
  if (duration > config.slowRequestThreshold) {
    logWarn(`⚠️ Slow Request: ${message}`)
    return
  }

  // DEBUG 级别显示响应数据
  if (config.level >= LogLevel.DEBUG) {
    logDebug(message, {
      status,
      duration: `${duration}ms`,
      data: truncateData(data, 300),
    })
  } else {
    // INFO 级别仅显示状态
    logInfo(message)
  }
}

/**
 * 记录请求错误
 */
export const logRequestError = (
  method: string,
  url: string,
  status?: number,
  error?: any
) => {
  if (config.level < LogLevel.ERROR) return

  const message = `${method} ${url}${status ? ` - ${status}` : ''}`

  // DEBUG 级别显示详细错误
  if (config.level >= LogLevel.DEBUG) {
    logError(message, {
      status,
      message: error?.message,
      data: error?.response?.data,
    })
  } else {
    // ERROR 级别仅显示基本错误信息
    logError(message, error?.message || 'Request failed')
  }
}

/**
 * 记录请求重试
 */
export const logRetry = (url: string, attempt: number, maxRetries: number) => {
  if (config.level < LogLevel.WARN) return

  logWarn(`🔄 Retrying (${attempt}/${maxRetries}): ${url}`)
}

// ==================== 开发工具 ====================
/**
 * 输出日志配置信息（仅开发环境）
 */
export const printLoggerInfo = () => {
  if (!import.meta.env.DEV) return

  const levelNames = ['NONE', 'ERROR', 'WARN', 'INFO', 'DEBUG']
  console.log(
    '%c📋 Logger Configuration',
    'color: #67c23a; font-size: 14px; font-weight: bold'
  )
  console.table({
    'Log Level': levelNames[config.level],
    'Colors Enabled': config.enableColors,
    'Slow Request Threshold': `${config.slowRequestThreshold}ms`,
    'Filter Sensitive Headers': config.filterSensitiveHeaders,
  })
  console.log(
    '%cTip: Use setLogLevel(LogLevel.DEBUG) to see detailed logs',
    'color: #909399; font-style: italic'
  )
}

// 开发环境自动输出配置信息
if (import.meta.env.DEV) {
  setTimeout(printLoggerInfo, 1000)
}

export default {
  LogLevel,
  setLogLevel,
  setLoggerConfig,
  getLoggerConfig,
  logDebug,
  logInfo,
  logWarn,
  logError,
  logRequest,
  logResponse,
  logRequestError,
  logRetry,
  printLoggerInfo,
}

