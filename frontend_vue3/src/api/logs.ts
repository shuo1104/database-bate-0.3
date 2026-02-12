/**
 * 系统日志API
 */

import { request } from '@/utils/request'

// ========== 接口类型定义 ==========

/** 登录日志 */
export interface LoginLog {
  log_id: number
  user_id: number
  username: string
  login_time: string
  logout_time?: string
  duration?: number
  ip_address?: string
  user_agent?: string
}

/** 注册日志 */
export interface RegistrationLog {
  log_id: number
  user_id: number
  username: string
  registration_time: string
  real_name?: string
  position?: string
  email?: string
  role: string
  ip_address?: string
}

/** 系统统计 */
export interface SystemStatistics {
  system_uptime_days: number
  system_start_date: string
  total_users: number
  total_projects: number
  total_materials: number
  total_fillers: number
  total_logins_today: number
  active_users_today: number
  total_usage_time_today: number
}

/** 每日使用统计 */
export interface DailyUsageStatistics {
  date: string
  login_count: number
  active_users: number
  total_duration: number
  avg_duration: number
}

/** 登录日志列表查询参数 */
export interface LoginLogListQuery {
  page: number
  page_size: number
  username?: string
  start_date?: string
  end_date?: string
}

/** 注册日志列表查询参数 */
export interface RegistrationLogListQuery {
  page: number
  page_size: number
  username?: string
  start_date?: string
  end_date?: string
}

/** 每日使用统计查询参数 */
export interface DailyUsageListQuery {
  days?: number
  start_date?: string
  end_date?: string
}

/** 列表响应 */
export interface ListResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// ========== API 方法 ==========

/**
 * 获取系统统计信息
 */
export function getSystemStatisticsApi() {
  return request<SystemStatistics>({
    url: '/api/v1/logs/statistics',
    method: 'get'
  })
}

/**
 * 获取登录日志列表
 */
export function getLoginLogsApi(params: LoginLogListQuery) {
  return request<ListResponse<LoginLog>>({
    url: '/api/v1/logs/login',
    method: 'get',
    params
  })
}

/**
 * 获取注册日志列表
 */
export function getRegistrationLogsApi(params: RegistrationLogListQuery) {
  return request<ListResponse<RegistrationLog>>({
    url: '/api/v1/logs/registration',
    method: 'get',
    params
  })
}

/**
 * 获取每日使用统计
 */
export function getDailyUsageStatisticsApi(params: DailyUsageListQuery) {
  return request<{ items: DailyUsageStatistics[] }>({
    url: '/api/v1/logs/daily-usage',
    method: 'get',
    params
  })
}

/**
 * 更新心跳（保持在线状态）
 */
export function updateHeartbeatApi(logId: number) {
  return request({
    url: `/api/v1/logs/heartbeat/${logId}`,
    method: 'post'
  })
}

/**
 * 用户登出
 */
export function userLogoutApi(logId: number) {
  return request({
    url: `/api/v1/logs/logout/${logId}`,
    method: 'post'
  })
}

