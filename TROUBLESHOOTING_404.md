# 🔧 404 错误排查与解决指南

## ❌ **问题描述**

前端请求时出现 404 错误：
```
请求的资源不存在
Request failed with status code 404
```

---

## 🔍 **问题诊断**

### 诊断结果：**后端服务未启动** ❌

当前后端服务 (`http://localhost:8000`) 无法访问。

---

## ✅ **解决方案**

### **步骤 1: 启动后端服务** 🚀

打开一个**新的终端窗口**（终端 1）：

```bash
# 进入后端目录
cd D:\WorkSpace\workspace\data_base\backend_fastapi

# 启动后端服务
python main.py run --env=dev
```

**预期输出**：
```
🚀 FastAPI 应用启动成功
📍 服务地址: http://0.0.0.0:8000
📖 API 文档: http://0.0.0.0:8000/docs
📘 ReDoc 文档: http://0.0.0.0:8000/redoc
🔍 健康检查: http://0.0.0.0:8000/health
```

### **步骤 2: 验证后端服务** ✅

打开浏览器，访问以下任一地址：

1. **健康检查**: http://localhost:8000/health
   - 应该看到：`{"status":"healthy","version":"2.0.0","environment":"dev"}`

2. **API 文档**: http://localhost:8000/docs
   - 应该看到 Swagger UI 界面

3. **测试登录接口**: http://localhost:8000/api/v1/auth/login
   - 应该返回 405 或 422 错误（正常，因为需要 POST 请求）

### **步骤 3: 启动前端服务** 🎨

打开**另一个终端窗口**（终端 2）：

```bash
# 进入前端目录
cd D:\WorkSpace\workspace\data_base\frontend_vue3

# 启动前端服务（如果未安装依赖，先运行 pnpm install）
pnpm dev
```

**预期输出**：
```
  VITE v6.3.5  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### **步骤 4: 访问前端应用** 🌐

打开浏览器，访问：http://localhost:3000

应该能看到登录页面。

---

## 🔄 **完整的启动流程**

### 方式 1: 使用两个终端（推荐）

**终端 1 - 后端**:
```bash
cd D:\WorkSpace\workspace\data_base\backend_fastapi
python main.py run --env=dev
```
保持此终端运行。

**终端 2 - 前端**:
```bash
cd D:\WorkSpace\workspace\data_base\frontend_vue3
pnpm dev
```
保持此终端运行。

### 方式 2: 使用后台运行（高级）

**Windows PowerShell**:
```powershell
# 启动后端（后台）
cd D:\WorkSpace\workspace\data_base\backend_fastapi
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python main.py run --env=dev"

# 启动前端（后台）
cd D:\WorkSpace\workspace\data_base\frontend_vue3
Start-Process powershell -ArgumentList "-NoExit", "-Command", "pnpm dev"
```

---

## 🐛 **其他可能的 404 问题**

如果后端已启动但仍然 404，检查以下几点：

### 1. **检查 API 路径是否正确** ✅

前端 API 路径格式：
```
/api/v1/{模块}/{接口}
```

**正确示例**：
- ✅ `/api/v1/auth/login`
- ✅ `/api/v1/projects/list`
- ✅ `/api/v1/materials/list`

**错误示例**：
- ❌ `/auth/login` (缺少 /api/v1 前缀)
- ❌ `/api/auth/login` (缺少 v1)
- ❌ `/v1/auth/login` (缺少 /api)

### 2. **检查前端代理配置** ✅

打开 `frontend_vue3/.env.development`，确认：

```bash
VITE_APP_BASE_API=/api
VITE_API_BASE_URL=http://localhost:8000
```

打开 `frontend_vue3/vite.config.ts`，确认代理配置：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

**重要**：修改配置后需要**重启前端服务**！

### 3. **检查后端路由注册** ✅

打开 `backend_fastapi/app/api/v1/__init__.py`，确认路由已注册：

```python
# 应该看到这些路由注册
api_router.include_router(auth_router, prefix="/auth", tags=["认证管理"])
api_router.include_router(projects_router, prefix="/projects", tags=["项目管理"])
api_router.include_router(materials_router, prefix="/materials", tags=["原料管理"])
```

### 4. **检查请求方法是否正确** ✅

| 接口 | 方法 | 路径 |
|------|------|------|
| 登录 | POST | `/api/v1/auth/login` |
| 获取用户信息 | GET | `/api/v1/auth/me` |
| 项目列表 | GET | `/api/v1/projects/list` |
| 创建项目 | POST | `/api/v1/projects/create` |
| 原料列表 | GET | `/api/v1/materials/list` |

---

## 🧪 **测试 API 接口**

### 使用浏览器测试

访问 http://localhost:8000/docs，在 Swagger UI 中测试接口。

### 使用 curl 测试

```bash
# 健康检查
curl http://localhost:8000/health

# 登录接口（需要提供用户名密码）
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# 项目列表（需要 Token）
curl http://localhost:8000/api/v1/projects/list \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 使用 PowerShell 测试

```powershell
# 健康检查
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# 登录接口
$body = @{
    username = "admin"
    password = "your_password"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

---

## 📊 **检查清单**

在报告问题之前，请确认以下各项：

- [ ] ✅ 后端服务已启动（访问 http://localhost:8000/health 有响应）
- [ ] ✅ 前端服务已启动（访问 http://localhost:3000 能打开页面）
- [ ] ✅ 前端 `.env.development` 配置正确
- [ ] ✅ 后端数据库连接正常
- [ ] ✅ 浏览器控制台无其他错误
- [ ] ✅ Network 面板中的请求路径正确

---

## 🔍 **调试技巧**

### 1. **查看浏览器开发者工具**

1. 按 `F12` 打开开发者工具
2. 切换到 **Network（网络）** 面板
3. 刷新页面或重新执行操作
4. 查看失败的请求：
   - **Request URL**: 确认请求地址是否正确
   - **Status Code**: 确认状态码（404 = 资源不存在）
   - **Response**: 查看服务器返回的错误信息

### 2. **查看后端日志**

后端终端会显示所有请求日志：

```
[2025-10-27 10:00:00] INFO - 📥 POST /api/v1/auth/login from 127.0.0.1
[2025-10-27 10:00:01] INFO - ✅ 200 - /api/v1/auth/login
```

如果看不到请求日志，说明请求**没有到达后端**（可能是前端代理配置问题）。

### 3. **查看前端控制台**

前端控制台会显示 API 错误：

```javascript
// 正常请求
GET http://localhost:3000/api/v1/projects/list 200 OK

// 404 错误
GET http://localhost:3000/api/v1/xxx/list 404 Not Found
```

---

## 💡 **常见错误及解决方案**

### 错误 1: `ECONNREFUSED` 或 `ERR_CONNECTION_REFUSED`

**原因**：后端服务未启动

**解决**：启动后端服务
```bash
cd backend_fastapi
python main.py run --env=dev
```

### 错误 2: `404 Not Found`

**原因**：API 路径错误或路由未注册

**解决**：
1. 检查前端 API 调用路径
2. 检查后端路由配置
3. 访问 http://localhost:8000/docs 查看所有可用接口

### 错误 3: `401 Unauthorized`

**原因**：Token 失效或未登录

**解决**：重新登录

### 错误 4: `500 Internal Server Error`

**原因**：后端服务器内部错误

**解决**：查看后端终端的错误日志

---

## 📞 **仍然无法解决？**

请提供以下信息：

1. **后端服务状态**：
   ```bash
   curl http://localhost:8000/health
   ```
   
2. **前端请求详情**：
   - 请求 URL（从 Network 面板复制）
   - 请求方法（GET/POST/PUT/DELETE）
   - 状态码
   
3. **浏览器控制台错误**：
   - Console 面板的完整错误信息
   
4. **后端日志**：
   - 后端终端的最后几行日志

---

## 🎯 **快速验证命令**

```bash
# 1. 检查后端是否运行
curl http://localhost:8000/health

# 2. 检查前端是否运行
curl http://localhost:3000

# 3. 检查后端 API 文档
start http://localhost:8000/docs

# 4. 检查前端应用
start http://localhost:3000
```

---

## ✅ **问题解决后的验证**

1. ✅ 访问 http://localhost:3000 能看到登录页面
2. ✅ 输入用户名密码，能成功登录
3. ✅ 登录后能看到项目列表或原料列表
4. ✅ 能进行增删改查操作

---

**祝您顺利解决问题！** 🎉

如有疑问，请查阅：
- [后端 README](./backend_fastapi/README.md)
- [前端 README](./frontend_vue3/README.md)
- [快速上手指南](./frontend_vue3/GETTING_STARTED.md)

