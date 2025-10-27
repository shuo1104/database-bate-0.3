import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'

// 样式
import 'uno.css'
import 'element-plus/dist/index.css'
import '@/styles/index.scss'

// 创建应用
const app = createApp(App)

// 使用插件
app.use(router)
app.use(pinia)

// 挂载应用
app.mount('#app')

