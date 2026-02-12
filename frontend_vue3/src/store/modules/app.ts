/**
 * 应用状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore(
  'app',
  () => {
    // 侧边栏状态
    const sidebar = ref({
      opened: true,
      withoutAnimation: false,
    })

    // 设备类型
    const device = ref('desktop')

    // 页面大小
    const size = ref('default')

    /**
     * 切换侧边栏
     */
    function toggleSidebar(withoutAnimation?: boolean) {
      sidebar.value.opened = !sidebar.value.opened
      sidebar.value.withoutAnimation = !!withoutAnimation
    }

    /**
     * 关闭侧边栏
     */
    function closeSidebar(withoutAnimation: boolean) {
      sidebar.value.opened = false
      sidebar.value.withoutAnimation = withoutAnimation
    }

    /**
     * 设置设备类型
     */
    function setDevice(val: string) {
      device.value = val
    }

    /**
     * 设置页面大小
     */
    function setSize(val: string) {
      size.value = val
    }

    return {
      sidebar,
      device,
      size,
      toggleSidebar,
      closeSidebar,
      setDevice,
      setSize,
    }
  },
  {
    persist: true,
  }
)

