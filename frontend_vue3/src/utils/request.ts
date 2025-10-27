/**
 * axios 请求封装
 */
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getToken, removeToken } from './auth'
import storage from './storage'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: '', // 不使用 baseURL，API 路径已包含完整路径
  timeout: 50000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, msg, data } = response.data

    // 二进制数据直接返回
    if (response.config.responseType === 'blob') {
      return response.data
    }

    // 成功响应
    if (code === 200 || code === 0) {
      return data
    }

    // 错误响应
    ElMessage.error(msg || '系统错误')
    return Promise.reject(new Error(msg || '系统错误'))
  },
  (error: AxiosError) => {
    // 处理HTTP错误
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          ElMessageBox.confirm('登录状态已过期，请重新登录', '系统提示', {
            confirmButtonText: '重新登录',
            cancelButtonText: '取消',
            type: 'warning',
          }).then(() => {
            removeToken()
            storage.clear()
            window.location.href = '/login'
          })
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error((data as any)?.msg || '服务器错误')
          break
        default:
          ElMessage.error((data as any)?.msg || `连接错误 ${status}`)
      }
    } else if (error.request) {
      ElMessage.error('网络请求失败，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

// 导出 axios 实例
export default service

