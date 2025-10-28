import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'
import { useTheme } from '@/composables/useTheme'

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

// 使用插件
app.use(router)
app.use(pinia)

// 挂载应用
app.mount('#app')

