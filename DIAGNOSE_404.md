# 🔍 404 错误精准诊断

## 📋 请按顺序执行以下测试

### ✅ **测试 1：后端健康检查**

打开浏览器或在终端执行：

**浏览器访问**：
```
http://localhost:8000/health
```

**或 PowerShell 执行**：
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing | Select-Object StatusCode, Content
```

**预期结果**：
```json
{"status":"healthy","version":"2.0.0","environment":"dev"}
```

- ✅ 如果成功：后端正常运行
- ❌ 如果失败：后端未启动或端口被占用

---

### ✅ **测试 2：后端 API 文档**

**浏览器访问**：
```
http://localhost:8000/docs
```

**预期结果**：能看到 Swagger UI 界面，显示所有 API 接口

- ✅ 如果能打开：后端路由注册正常
- ❌ 如果打不开：后端有问题

---

### ✅ **测试 3：直接测试后端登录接口**

**PowerShell 执行**：
```powershell
$body = @{
    username = "admin"
    password = "test123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**预期结果**：
- ✅ 200 或 401（密码错误但接口存在）
- ❌ 404（接口不存在）

---

### ✅ **测试 4：前端代理是否工作**

**前提**：前端服务必须运行中

1. 打开浏览器访问前端：`http://localhost:3000`
2. 按 `F12` 打开开发者工具
3. 切换到 **Console（控制台）** 标签
4. 输入以下代码并回车：

```javascript
fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'test' })
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

**预期结果**：
- ✅ 返回登录响应（成功或失败都说明代理工作）
- ❌ 404 错误（代理未工作或路径错误）

---

### ✅ **测试 5：使用 API 测试工具**

访问：`http://localhost:3000/API_TEST.html`

点击 **"🚀 一键测试所有接口"**

---

## 🐛 **根据测试结果诊断**

### 情况 1：测试 1 和 2 失败
**问题**：后端未启动或配置错误

**解决**：
```bash
cd D:\WorkSpace\workspace\data_base\backend_fastapi
python main.py run --env=dev
```

---

### 情况 2：测试 1 和 2 成功，测试 3 失败
**问题**：后端路由未正确注册

**检查**：
1. 打开 `backend_fastapi/app/api/v1/__init__.py`
2. 确认路由已注册：
```python
api_router.include_router(auth_router, prefix="/auth", tags=["认证管理"])
```

---

### 情况 3：测试 1-3 成功，测试 4 失败
**问题**：前端代理配置问题

**解决**：

1. **重启前端服务**（重要！）
```bash
# 按 Ctrl+C 停止前端
# 然后重新启动
pnpm dev
```

2. **检查 vite.config.ts**：
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
  },
}
```

3. **清除浏览器缓存**：
   - 按 `Ctrl + Shift + Delete`
   - 或硬刷新：`Ctrl + Shift + R`

---

### 情况 4：全部成功但前端页面仍然 404
**问题**：前端某个特定页面或接口问题

**需要告诉我**：
1. 在哪个页面出现 404？
2. 做什么操作时出现 404？
3. 浏览器 Network 面板中失败请求的完整 URL

---

## 📸 **请提供以下信息**

如果以上测试后仍然有问题，请告诉我：

1. **哪个测试失败了？** （测试 1/2/3/4/5）

2. **失败的具体错误信息**

3. **浏览器 F12 Network 面板截图**，显示：
   - 失败请求的 URL
   - 请求方法
   - 状态码
   - 响应内容

4. **后端终端的日志输出**（最后 20 行）

---

## 🔧 **常见修复方法汇总**

### 修复 1：重启前端服务
```bash
cd frontend_vue3
# Ctrl+C 停止
pnpm dev
```

### 修复 2：清除浏览器缓存
- `Ctrl + Shift + R` （硬刷新）
- 或 `Ctrl + Shift + Delete` （清除缓存）

### 修复 3：重启后端服务
```bash
cd backend_fastapi
# Ctrl+C 停止
python main.py run --env=dev
```

### 修复 4：检查端口占用
```powershell
# 检查 8000 端口
netstat -ano | findstr :8000

# 检查 3000 端口
netstat -ano | findstr :3000
```

---

## 💡 **快速诊断命令**

在 PowerShell 中执行：

```powershell
Write-Host "=== 诊断开始 ===" -ForegroundColor Cyan

# 测试后端健康
Write-Host "`n[1/3] 测试后端健康检查..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host "✅ 后端健康: $($health.StatusCode)" -ForegroundColor Green
    Write-Host $health.Content
} catch {
    Write-Host "❌ 后端异常: $_" -ForegroundColor Red
}

# 测试后端登录接口
Write-Host "`n[2/3] 测试后端登录接口..." -ForegroundColor Yellow
try {
    $body = @{username="admin";password="test"} | ConvertTo-Json
    $login = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method POST -ContentType "application/json" -Body $body -UseBasicParsing
    Write-Host "✅ 登录接口存在: $($login.StatusCode)" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 401 -or $statusCode -eq 422) {
        Write-Host "✅ 登录接口存在（密码错误正常）: $statusCode" -ForegroundColor Green
    } else {
        Write-Host "❌ 登录接口异常: $statusCode - $_" -ForegroundColor Red
    }
}

# 测试前端服务
Write-Host "`n[3/3] 测试前端服务..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    Write-Host "✅ 前端运行中: $($frontend.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ 前端未运行: $_" -ForegroundColor Red
}

Write-Host "`n=== 诊断完成 ===" -ForegroundColor Cyan
```

---

**请执行上述测试，然后告诉我结果！** 🚀

