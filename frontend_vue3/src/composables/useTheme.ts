/**
 * 主题管理 Composable
 * 用于管理应用的暗黑/白天主题切换
 */
import { ref } from 'vue'

// 主题类型
export type ThemeMode = 'light' | 'dark'

// 本地存储的键名
const THEME_STORAGE_KEY = 'app-theme'

// 全局主题状态（确保单例）
const isDark = ref<boolean>(false)
const isInitialized = ref<boolean>(false)

export function useTheme() {
  /**
   * 初始化主题
   * 从 localStorage 读取用户的主题偏好
   */
  const initTheme = () => {
    if (isInitialized.value) return

    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null
    
    if (savedTheme === 'dark') {
      isDark.value = true
      applyTheme('dark')
    } else {
      isDark.value = false
      applyTheme('light')
    }

    isInitialized.value = true
  }

  /**
   * 应用主题到 DOM
   * @param theme - 要应用的主题模式
   */
  const applyTheme = (theme: ThemeMode) => {
    const htmlElement = document.documentElement
    const bodyElement = document.body
    
    if (theme === 'dark') {
      htmlElement.classList.add('dark')
      bodyElement.classList.add('dark')
      // 强制更新背景色
      htmlElement.style.backgroundColor = '#141414'
      bodyElement.style.backgroundColor = '#141414'
    } else {
      htmlElement.classList.remove('dark')
      bodyElement.classList.remove('dark')
      // 恢复白色背景
      htmlElement.style.backgroundColor = '#ffffff'
      bodyElement.style.backgroundColor = '#ffffff'
    }
    
    // 触发重绘，确保所有样式都被应用
    setTimeout(() => {
      window.dispatchEvent(new Event('theme-changed'))
    }, 0)
  }

  /**
   * 切换主题
   */
  const toggleTheme = () => {
    isDark.value = !isDark.value
    const newTheme: ThemeMode = isDark.value ? 'dark' : 'light'
    
    // 应用主题
    applyTheme(newTheme)
    
    // 保存到 localStorage
    localStorage.setItem(THEME_STORAGE_KEY, newTheme)
  }

  /**
   * 设置指定主题
   * @param theme - 要设置的主题模式
   */
  const setTheme = (theme: ThemeMode) => {
    isDark.value = theme === 'dark'
    applyTheme(theme)
    localStorage.setItem(THEME_STORAGE_KEY, theme)
  }

  /**
   * 获取当前主题
   */
  const getCurrentTheme = (): ThemeMode => {
    return isDark.value ? 'dark' : 'light'
  }

  // 监听主题变化，同步到其他标签页
  const syncThemeAcrossTabs = () => {
    window.addEventListener('storage', (event) => {
      if (event.key === THEME_STORAGE_KEY) {
        const newTheme = event.newValue as ThemeMode
        if (newTheme) {
          isDark.value = newTheme === 'dark'
          applyTheme(newTheme)
        }
      }
    })
  }

  return {
    isDark,
    initTheme,
    toggleTheme,
    setTheme,
    getCurrentTheme,
    syncThemeAcrossTabs
  }
}


