# PhotoPolymer 配方管理系统 - 前端

基于 **Vue 3 + TypeScript + Vite + Element Plus** 的现代化前端应用。

## ✨ 技术栈

- **Vue 3.5** - 渐进式 JavaScript 框架
- **TypeScript 5.8** - JavaScript 的超集
- **Vite 6.3** - 下一代前端构建工具
- **Element Plus 2.10** - Vue 3 UI 组件库
- **Pinia 3.0** - Vue 3 状态管理
- **Vue Router 4.5** - 路由管理
- **Axios 1.10** - HTTP 客户端
- **UnoCSS** - 原子化 CSS 引擎

## 🚀 快速开始

### 安装依赖

```bash
cd frontend_vue3
pnpm install
npm install -g pnpm

```

### 启动开发服务器

```bash
pnpm dev
```

访问：http://localhost:3000

### 构建生产版本

```bash
pnpm build
```

### 预览构建结果

```bash
pnpm preview
```

## 📁 项目结构

```
frontend_vue3/
├── src/
│   ├── api/              # API 接口定义
│   ├── assets/           # 静态资源
│   ├── components/       # 通用组件
│   ├── composables/      # 组合式函数
│   ├── layouts/          # 布局组件
│   ├── router/           # 路由配置
│   ├── store/            # Pinia 状态管理
│   ├── styles/           # 全局样式
│   ├── utils/            # 工具函数
│   ├── views/            # 页面组件
│   ├── App.vue           # 根组件
│   └── main.ts           # 应用入口
├── .env.development      # 开发环境配置
├── .env.production       # 生产环境配置
├── package.json          # 依赖配置
├── vite.config.ts        # Vite 配置
└── tsconfig.json         # TypeScript 配置
```

## 🎯 核心功能

### 用户认证
- ✅ 用户登录/登出
- ✅ JWT Token 认证
- ✅ 个人信息管理
- ✅ 密码修改

### 项目管理
- ✅ 项目列表查询
- ✅ 项目创建/编辑/删除
- ✅ 项目详情查看
- ✅ 配方组成管理
- ✅ 测试结果录入
- ✅ 项目报告导出

### 原料/填料管理
- ✅ 原料列表查询
- ✅ 原料创建/编辑/删除
- ✅ 填料列表查询
- ✅ 填料创建/编辑/删除

### 系统管理
- ✅ 用户管理（管理员）
- ✅ 系统日志查看
- ✅ 登录日志统计

## 🔧 开发指南

### API 调用

```typescript
import { getProjectListApi } from '@/api/projects'

const fetchProjects = async () => {
  const res = await getProjectListApi({
    page: 1,
    page_size: 20
  })
  console.log(res)
}
```

### 状态管理

```typescript
import { useUserStore } from '@/store'

const userStore = useUserStore()

// 登录
await userStore.login({
  username: 'admin',
  password: 'admin123'
})

// 获取用户信息
console.log(userStore.userInfo)
```

### 路由守卫

路由会自动进行权限验证：
- 已登录：允许访问所有页面
- 未登录：重定向到登录页
- 管理员页面：仅管理员可访问

## 🔐 环境变量

### 开发环境 (.env.development)

```env
VITE_APP_PORT=3000
VITE_APP_BASE_API=/api
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=PhotoPolymer 配方管理系统
```

### 生产环境 (.env.production)

```env
VITE_APP_BASE_API=/api
VITE_API_BASE_URL=https://your-domain.com
VITE_APP_TITLE=PhotoPolymer 配方管理系统
```

## 📦 部署

### Nginx 配置示例

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

## 🛠️ 常见问题

### 安装依赖失败

```bash
# 清除缓存
pnpm store prune
rm -rf node_modules pnpm-lock.yaml

# 重新安装
pnpm install
```

### 端口被占用

修改 `.env.development` 中的 `VITE_APP_PORT`

### API 请求失败

1. 检查后端服务是否启动
2. 检查 `VITE_API_BASE_URL` 配置
3. 查看浏览器控制台错误信息

## 📄 许可证

MIT License
