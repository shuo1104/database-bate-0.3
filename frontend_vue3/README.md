# 光创化物 R&D 配方数据库管理系统 - 前端

## 📖 项目简介

基于 **Vue 3 + TypeScript + Vite + Element Plus** 构建的现代化前后端分离管理系统前端，专为光创化物 R&D 配方数据库设计。

## ✨ 技术栈

### 核心框架
- **Vue 3.5.17** - 渐进式 JavaScript 框架
- **TypeScript 5.8.3** - JavaScript 的超集
- **Vite 6.3.5** - 下一代前端构建工具
- **Element Plus 2.10.4** - Vue 3 UI 组件库

### 状态管理
- **Pinia 3.0.3** - Vue 3 官方状态管理库
- **pinia-plugin-persistedstate** - 状态持久化插件

### 路由管理
- **Vue Router 4.5.1** - Vue 官方路由管理器

### HTTP 请求
- **Axios 1.10.0** - Promise 风格的 HTTP 客户端

### 工具库
- **@vueuse/core** - Vue 组合式 API 工具集
- **dayjs** - 轻量级日期时间库
- **nprogress** - 页面加载进度条
- **exceljs** - Excel 操作库
- **file-saver** - 文件下载库

### 开发工具
- **UnoCSS** - 原子化 CSS 引擎
- **unplugin-auto-import** - API 自动导入
- **unplugin-vue-components** - 组件自动导入

## 🚀 快速开始

### 前置要求

- Node.js >= 18.0.0
- pnpm >= 8.1.0 (推荐) 或 npm >= 10.0.0

### 安装依赖

```bash
cd frontend_vue3
pnpm install
# 或
npm install
```

### 启动开发服务器

```bash
pnpm dev
# 或
npm run dev
```

访问: http://localhost:3000

### 构建生产版本

```bash
pnpm build
# 或
npm run build
```

### 预览构建结果

```bash
pnpm preview
# 或
npm run preview
```

## 📁 项目结构

```
frontend_vue3/
├── public/                 # 静态资源
├── src/                    # 源代码
│   ├── api/               # API 接口
│   │   ├── auth.ts        # 认证接口
│   │   ├── projects.ts    # 项目管理接口
│   │   ├── materials.ts   # 原料管理接口
│   │   └── index.ts       # 统一导出
│   ├── assets/            # 静态资源
│   │   ├── icons/         # 图标
│   │   ├── images/        # 图片
│   │   └── logo/          # Logo
│   ├── components/        # 通用组件
│   │   └── Pagination.vue # 分页组件
│   ├── layouts/           # 布局组件
│   │   ├── index.vue      # 主布局
│   │   └── components/    # 布局子组件
│   │       ├── Sidebar.vue   # 侧边栏
│   │       └── Navbar.vue    # 顶部导航
│   ├── router/            # 路由配置
│   │   └── index.ts       # 路由定义
│   ├── store/             # 状态管理
│   │   ├── index.ts       # Store 入口
│   │   └── modules/       # Store 模块
│   │       ├── user.ts    # 用户状态
│   │       └── app.ts     # 应用状态
│   ├── styles/            # 全局样式
│   │   ├── index.scss     # 主样式
│   │   └── variables.scss # SCSS 变量
│   ├── types/             # TypeScript 类型定义
│   │   ├── env.d.ts       # 环境变量类型
│   │   └── global.d.ts    # 全局类型
│   ├── utils/             # 工具函数
│   │   ├── request.ts     # Axios 封装
│   │   ├── auth.ts        # 认证工具
│   │   ├── storage.ts     # 存储工具
│   │   ├── common.ts      # 通用工具
│   │   └── index.ts       # 统一导出
│   ├── views/             # 页面组件
│   │   ├── auth/          # 认证页面
│   │   │   └── Login.vue  # 登录页
│   │   ├── projects/      # 项目管理
│   │   │   └── index.vue  # 项目列表
│   │   ├── materials/     # 原料管理
│   │   │   └── index.vue  # 原料列表
│   │   ├── fillers/       # 填料管理
│   │   │   └── index.vue  # 填料列表
│   │   └── error/         # 错误页面
│   │       └── 404.vue    # 404 页面
│   ├── App.vue            # 根组件
│   ├── main.ts            # 应用入口
│   └── settings.ts        # 全局配置
├── .env.development       # 开发环境配置
├── .env.production        # 生产环境配置
├── .gitignore            # Git 忽略文件
├── index.html            # HTML 模板
├── package.json          # 项目配置
├── tsconfig.json         # TypeScript 配置
├── tsconfig.node.json    # Node TypeScript 配置
├── uno.config.ts         # UnoCSS 配置
├── vite.config.ts        # Vite 配置
└── README.md             # 项目文档
```

## 🎯 核心功能

### 已实现功能

#### 1. 用户认证
- ✅ 用户登录
- ✅ JWT Token 认证
- ✅ 自动 Token 刷新
- ✅ 用户信息管理

#### 2. 项目管理
- ✅ 项目列表查询
- ✅ 项目创建/编辑/删除
- ✅ 项目筛选与搜索
- ✅ 分页功能

#### 3. 原料管理
- ✅ 原料列表查询
- ✅ 原料创建/编辑/删除
- ✅ 原料筛选与搜索
- ✅ 分页功能

#### 4. 填料管理
- ✅ 基础页面结构（待开发完整功能）

### 待开发功能

- ⏳ 配方成分管理（与项目关联）
- ⏳ 测试结果管理
- ⏳ 数据统计与报表
- ⏳ Excel 导入导出
- ⏳ 用户权限管理
- ⏳ 系统设置

## 🔧 开发指南

### API 接口调用

项目使用统一的 `request` 工具进行 API 调用：

```typescript
// 导入 API
import { getProjectListApi } from '@/api/projects'

// 调用 API
const res = await getProjectListApi({
  page: 1,
  page_size: 20,
  ProjectName: '测试项目'
})
```

### 状态管理

使用 Pinia 进行状态管理：

```typescript
// 导入 Store
import { useUserStore } from '@/store'

// 使用 Store
const userStore = useUserStore()

// 访问状态
console.log(userStore.userInfo)

// 调用方法
await userStore.login({ username: 'admin', password: '123456' })
```

### 路由守卫

路由自动进行权限验证：

```typescript
// 已登录：允许访问所有页面（除 /login）
// 未登录：重定向到 /login
```

### 样式开发

支持 SCSS 和 UnoCSS：

```vue
<template>
  <div class="container flex-center">
    内容
  </div>
</template>

<style scoped lang="scss">
.container {
  padding: 20px;
  background-color: $primary-color;
}
</style>
```

### 组件开发

使用 Vue 3 Composition API：

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'

const count = ref(0)

function increment() {
  count.value++
}

onMounted(() => {
  console.log('组件已挂载')
})
</script>
```

## 🔐 环境变量

### 开发环境 (`.env.development`)

```bash
# 应用端口
VITE_APP_PORT=3000

# API 基础路径
VITE_APP_BASE_API=/api

# 后端服务地址
VITE_API_BASE_URL=http://localhost:8000

# 应用标题
VITE_APP_TITLE=光创化物 R&D 配方管理系统
```

### 生产环境 (`.env.production`)

```bash
# API 基础路径
VITE_APP_BASE_API=/api

# 后端服务地址（需修改为实际生产地址）
VITE_API_BASE_URL=https://your-production-domain.com

# 应用标题
VITE_APP_TITLE=光创化物 R&D 配方管理系统
```

## 📦 打包部署

### 构建

```bash
pnpm build
```

构建产物位于 `dist/` 目录。

### 部署

#### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤝 与后端联调

### 1. 启动后端服务

```bash
cd backend_fastapi
python main.py run --env=dev
```

后端服务运行在: http://localhost:8000

### 2. 启动前端服务

```bash
cd frontend_vue3
pnpm dev
```

前端服务运行在: http://localhost:3000

### 3. 自动代理

前端开发服务器会自动将 `/api` 开头的请求代理到后端 `http://localhost:8000`。

## 📝 默认账号

- 用户名: `admin`
- 密码: （请联系后端查看或创建测试账号）

## 🛠️ 常见问题

### 1. 安装依赖失败

```bash
# 清除缓存
pnpm store prune
# 重新安装
pnpm install
```

### 2. 端口被占用

修改 `.env.development` 中的 `VITE_APP_PORT`。

### 3. API 请求失败

检查后端服务是否启动，以及 `VITE_API_BASE_URL` 配置是否正确。

## 📄 许可证

MIT License

## 👥 贡献者

光创化物 R&D 团队

