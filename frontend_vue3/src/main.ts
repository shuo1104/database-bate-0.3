import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'
import { useTheme } from '@/composables/useTheme'
import { handleSystemError } from '@/utils/errorHandler'

// 样式
import 'uno.css'
import 'element-plus/dist/index.css'
import '@/styles/index.scss'
import '@/styles/table-enhance.scss'

// 初始化主题（在应用挂载前）
const { initTheme } = useTheme()
initTheme()

// 创建应用
const app = createApp(App)

// ==================== 全局错误处理 ====================
// Vue 错误处理器
app.config.errorHandler = (err, instance, info) => {
  console.error('❌ Vue Error:', err)
  console.error('📍 Component:', instance?.$options?.name || 'Anonymous')
  console.error('ℹ️ Error Info:', info)
  
  // 处理系统错误
  handleSystemError(
    'An application error occurred. Please refresh the page if the issue persists.',
    err as Error
  )
}

// Vue 警告处理器（仅开发环境）
if (import.meta.env.DEV) {
  app.config.warnHandler = (msg, instance, trace) => {
    console.warn('⚠️ Vue Warning:', msg)
    console.warn('📍 Component:', instance?.$options?.name || 'Anonymous')
    console.warn('📚 Trace:', trace)
  }
}

// 使用插件
app.use(router)
app.use(pinia)

// 挂载应用
app.mount('#app')

