# 🚀 快速上手指南

## 📋 前置准备

### 1. 环境要求

- **Node.js**: >= 18.0.0
- **包管理器**: pnpm >= 8.1.0 (推荐) 或 npm >= 10.0.0
- **后端服务**: FastAPI 后端需已启动

### 2. 检查环境

```bash
# 检查 Node.js 版本
node --version

# 检查 npm 版本
npm --version

# 安装 pnpm (推荐)
npm install -g pnpm

# 检查 pnpm 版本
pnpm --version
```

## 🎯 5 分钟快速启动

### 步骤 1: 进入前端目录

```bash
cd frontend_vue3
```

### 步骤 2: 安装依赖

```bash
# 使用 pnpm (推荐)
pnpm install

# 或使用 npm
npm install
```

> ⏱️ 首次安装大约需要 1-3 分钟

### 步骤 3: 启动开发服务器

```bash
# 使用 pnpm
pnpm dev

# 或使用 npm
npm run dev
```

### 步骤 4: 访问应用

浏览器自动打开: http://localhost:3000

> 如果没有自动打开，请手动访问该地址

### 步骤 5: 登录系统

- 用户名: `admin`
- 密码: （联系后端管理员获取）

## 🔧 完整联调步骤

### 1. 启动后端服务

在另一个终端窗口：

```bash
cd backend_fastapi
python main.py run --env=dev
```

后端服务地址: http://localhost:8000
API 文档: http://localhost:8000/docs

### 2. 启动前端服务

```bash
cd frontend_vue3
pnpm dev
```

前端服务地址: http://localhost:3000

### 3. 验证连接

访问前端后，尝试登录。如果能成功登录并看到数据，说明前后端联调成功！

## 📖 核心功能演示

### 1. 项目管理

- 📝 **新增项目**: 点击"新增"按钮
- ✏️ **编辑项目**: 点击表格中的"编辑"按钮
- ❌ **删除项目**: 点击表格中的"删除"按钮
- 🔍 **搜索项目**: 使用顶部搜索框

### 2. 原料管理

- 📝 **新增原料**: 点击"新增"按钮
- ✏️ **编辑原料**: 点击表格中的"编辑"按钮
- ❌ **删除原料**: 点击表格中的"删除"按钮
- 🔍 **搜索原料**: 使用顶部搜索框

### 3. 用户管理

- 👤 **查看个人信息**: 点击右上角用户名
- 🚪 **退出登录**: 用户下拉菜单 → 退出登录

## 🎨 开发建议

### 1. 推荐的 IDE 配置

- **VSCode** + 以下插件:
  - Volar (Vue 3)
  - TypeScript Vue Plugin
  - ESLint
  - Prettier

### 2. 推荐的浏览器

- **Chrome** (推荐)
- **Edge**
- **Firefox**

### 3. 开发工具

- **Vue DevTools**: 浏览器扩展，用于调试 Vue 应用
- **Postman**: API 测试工具

## 🐛 常见问题排查

### 问题 1: 安装依赖失败

**解决方案**:

```bash
# 清除 node_modules
rm -rf node_modules

# 清除缓存
pnpm store prune

# 重新安装
pnpm install
```

### 问题 2: 启动失败 - 端口被占用

**错误信息**: `Port 3000 is already in use`

**解决方案**:

方法 1: 修改端口
```bash
# 编辑 .env.development
VITE_APP_PORT=3001
```

方法 2: 关闭占用端口的进程
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <进程ID> /F

# macOS/Linux
lsof -i :3000
kill -9 <进程ID>
```

### 问题 3: API 请求失败

**错误信息**: 网络请求失败或 401 错误

**检查清单**:
1. ✅ 后端服务是否启动？
2. ✅ 后端地址配置是否正确？ (`.env.development` 中的 `VITE_API_BASE_URL`)
3. ✅ 是否使用了正确的用户名和密码？

**解决方案**:

```bash
# 1. 确认后端服务运行中
curl http://localhost:8000/health

# 2. 检查前端配置
cat .env.development | grep VITE_API_BASE_URL
# 应该输出: VITE_API_BASE_URL=http://localhost:8000

# 3. 清除浏览器缓存或使用无痕模式
```

### 问题 4: 页面空白或报错

**解决方案**:

1. 打开浏览器开发者工具 (F12)
2. 查看 Console 中的错误信息
3. 检查 Network 面板中的请求状态
4. 尝试硬刷新页面 (Ctrl + Shift + R)

### 问题 5: TypeScript 报错

**解决方案**:

```bash
# 重新生成类型定义
pnpm dev

# 类型定义文件会自动生成在:
# - src/types/auto-imports.d.ts
# - src/types/components.d.ts
```

## 📚 下一步学习

### 1. 阅读完整文档

- [README.md](./README.md) - 项目详细文档
- [项目结构说明](#)
- [API 接口文档](http://localhost:8000/docs)

### 2. 学习核心技术

- [Vue 3 官方文档](https://cn.vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/zh/)
- [Element Plus 组件库](https://element-plus.org/zh-CN/)
- [Vite 构建工具](https://cn.vitejs.dev/)

### 3. 参与开发

- 熟悉项目结构
- 了解代码规范
- 参考现有功能模块
- 开发新功能

## 💡 开发技巧

### 1. 使用 TypeScript 类型提示

```typescript
// API 调用会自动提示返回类型
const res = await getProjectListApi() // res 自动推断为 PageResult<ProjectInfo>
```

### 2. 使用组合式 API

```typescript
// 响应式数据
const count = ref(0)
const user = reactive({ name: 'admin' })

// 计算属性
const doubleCount = computed(() => count.value * 2)

// 监听变化
watch(count, (newVal) => {
  console.log('count 变化:', newVal)
})
```

### 3. 使用 Element Plus 组件

```vue
<template>
  <el-button type="primary" @click="handleClick">
    按钮
  </el-button>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'

function handleClick() {
  ElMessage.success('点击成功')
}
</script>
```

## 🎉 恭喜！

您已成功启动前端项目！现在可以开始开发了。

如有任何问题，请查阅 [README.md](./README.md) 或联系项目维护者。

