/**
 * 用户在线状态心跳
 * 自动定期更新用户在线状态和使用时长
 */

import { onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/store'
import { updateHeartbeatApi, userLogoutApi } from '@/api/logs'

// 心跳间隔（3分钟）
const HEARTBEAT_INTERVAL = 3 * 60 * 1000

export function useHeartbeat() {
  const userStore = useUserStore()
  let heartbeatTimer: number | null = null

  /**
   * 发送心跳
   */
  async function sendHeartbeat() {
    const logId = userStore.logId
    if (!logId) return

    try {
      await updateHeartbeatApi(logId)
      // 心跳发送成功
    } catch (error) {
      console.error('[Heartbeat] 心跳发送失败:', error)
    }
  }

  /**
   * 启动心跳
   */
  function startHeartbeat() {
    if (heartbeatTimer) return

    // 立即发送一次心跳
    sendHeartbeat()

    // 定期发送心跳
    heartbeatTimer = window.setInterval(() => {
      sendHeartbeat()
    }, HEARTBEAT_INTERVAL)

    // 心跳已启动
  }

  /**
   * 停止心跳
   */
  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
      // 心跳已停止
    }
  }

  /**
   * 用户登出（发送登出请求）
   */
  async function logout() {
    const logId = userStore.logId
    if (!logId) return

    try {
      await userLogoutApi(logId)
      // 登出成功
    } catch (error) {
      console.error('[Heartbeat] 登出失败:', error)
    }
  }

  /**
   * 页面可见性变化处理
   */
  function handleVisibilityChange() {
    if (document.hidden) {
      // 页面隐藏时停止心跳
      stopHeartbeat()
    } else {
      // 页面显示时恢复心跳
      startHeartbeat()
    }
  }

  /**
   * 页面关闭前处理
   */
  function handleBeforeUnload() {
    // 页面关闭时发送登出请求（使用 sendBeacon 确保发送成功）
    const logId = userStore.logId
    if (logId) {
      // 使用 navigator.sendBeacon 在页面关闭时发送请求
      const url = `/api/v1/logs/logout/${logId}`
      const data = JSON.stringify({})
      navigator.sendBeacon(url, data)
    }
  }

  // 返回启动和停止函数，由外部在生命周期钩子中调用
  const init = () => {
    // 如果用户已登录，启动心跳
    if (userStore.logId) {
      startHeartbeat()
      // 监听页面可见性变化
      document.addEventListener('visibilitychange', handleVisibilityChange)
      // 监听页面关闭
      window.addEventListener('beforeunload', handleBeforeUnload)
    }
  }

  const destroy = () => {
    stopHeartbeat()
    document.removeEventListener('visibilitychange', handleVisibilityChange)
    window.removeEventListener('beforeunload', handleBeforeUnload)
  }

  return {
    init,
    destroy,
    sendHeartbeat,
    logout
  }
}

