/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginApi, getCurrentUserInfoApi, type LoginData, type UserInfo } from '@/api/auth'
import { setToken, removeToken } from '@/utils/auth'
import storage from '@/utils/storage'

export const useUserStore = defineStore(
  'user',
  () => {
    // 状态
    const token = ref<string>('')
    const userInfo = ref<UserInfo | null>(null)
    const logId = ref<number | null>(null)  // 登录日志ID

    /**
     * 登录
     */
    async function login(loginData: LoginData) {
      try {
        const response = await loginApi(loginData)
        
        // 保存token
        token.value = response.token.access_token
        setToken(response.token.access_token)
        storage.setRefreshToken(response.token.refresh_token)
        
        // 保存用户信息
        userInfo.value = response.user
        storage.setUserInfo(response.user)
        
        // 保存登录日志ID
        if (response.log_id) {
          logId.value = response.log_id
          storage.set('log_id', response.log_id)
        }
        
        return response
      } catch (error) {
        return Promise.reject(error)
      }
    }

    /**
     * 获取用户信息
     */
    async function getUserInfo() {
      try {
        const data = await getCurrentUserInfoApi()
        userInfo.value = data
        storage.setUserInfo(data)
        return data
      } catch (error) {
        return Promise.reject(error)
      }
    }

    /**
     * 设置用户信息
     */
    function setUserInfo(data: UserInfo) {
      userInfo.value = data
      storage.setUserInfo(data)
    }

    /**
     * 退出登录
     */
    function logout() {
      token.value = ''
      userInfo.value = null
      logId.value = null
      removeToken()
      storage.clear()
    }

    /**
     * 重置状态
     */
    function reset() {
      token.value = ''
      userInfo.value = null
      logId.value = null
    }

    return {
      token,
      userInfo,
      logId,
      login,
      getUserInfo,
      setUserInfo,
      logout,
      reset,
    }
  },
  {
    persist: true, // 持久化
  }
)

