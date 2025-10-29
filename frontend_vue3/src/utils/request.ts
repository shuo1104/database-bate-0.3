/**
 * Axios Request Wrapper
 */
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getToken, removeToken } from './auth'
import storage from './storage'

// Create axios instance
const service: AxiosInstance = axios.create({
  baseURL: '', // No baseURL, API paths already include full path
  timeout: 50000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

// Request interceptor
service.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, msg, data } = response.data

    // Return binary data directly
    if (response.config.responseType === 'blob') {
      return response.data
    }

    // Successful response
    if (code === 200 || code === 0) {
      return data
    }

    // Error response
    ElMessage.error(msg || 'System error')
    return Promise.reject(new Error(msg || 'System error'))
  },
  (error: AxiosError) => {
    // Handle HTTP errors
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Check if this is a login request (no token in request)
          const isLoginRequest = !error.config?.headers?.Authorization
          
          if (isLoginRequest) {
            // Login failed - show error message from server
            const errorMsg = (data as any)?.detail || (data as any)?.msg || 'Incorrect username or password'
            ElMessage.error(errorMsg)
          } else {
            // Token expired - show session expired dialog
            ElMessageBox.confirm('Login session expired, please login again', 'System Notification', {
              confirmButtonText: 'Re-login',
              cancelButtonText: 'Cancel',
              type: 'warning',
            }).then(() => {
              removeToken()
              storage.clear()
              window.location.href = '/login'
            })
          }
          break
        case 403:
          ElMessage.error('No permission to access this resource')
          break
        case 404:
          ElMessage.error('Requested resource does not exist')
          break
        case 500:
          ElMessage.error((data as any)?.msg || 'Server error')
          break
        default:
          ElMessage.error((data as any)?.msg || `Connection error ${status}`)
      }
    } else if (error.request) {
      ElMessage.error('Network request failed, please check network connection')
    } else {
      ElMessage.error('Request configuration error')
    }

    return Promise.reject(error)
  }
)

// Export axios instance
export default service

