# 后端服务需要重启

## 问题原因

日志 API 返回 500 错误的真正原因是：**缺少 `greenlet` 模块**

错误日志显示：
```
the greenlet library is required to use this function. No module named 'greenlet._greenlet'
```

## 解决方案

### 1. 确认 greenlet 已安装

```bash
pip install greenlet>=3.0.0
```

或者重新安装所有依赖：

```bash
cd backend_fastapi
pip install -r requirements.txt
```

### 2. **重启后端服务** ⚠️ 重要！

greenlet 安装后，**必须重启 FastAPI 服务**才能生效。

#### 方法 1: 如果使用 `python main.py run`

1. 按 `Ctrl+C` 停止当前运行的服务
2. 重新运行：
```bash
cd backend_fastapi
python main.py run --env=dev
```

#### 方法 2: 如果使用 uvicorn 直接运行

1. 按 `Ctrl+C` 停止服务
2. 重新运行：
```bash
cd backend_fastapi
uvicorn main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

#### 方法 3: 杀掉所有 Python 进程后重启

```powershell
# Windows PowerShell
Get-Process python | Stop-Process -Force

# 然后重新启动
cd backend_fastapi
python main.py run --env=dev
```

### 3. 验证服务已正常启动

访问以下地址确认服务正常：

```
http://localhost:8000/health
http://localhost:8000/docs
```

### 4. 测试日志 API

重启后，这些 API 应该正常工作：

```bash
# 测试系统统计（需要管理员权限）
GET http://localhost:8000/api/v1/logs/statistics

# 测试登录日志
GET http://localhost:8000/api/v1/logs/login?page=1&page_size=20
```

## 为什么需要重启？

Python 在启动时会加载所有模块。如果在服务运行时安装新的依赖包，服务进程中的 Python 解释器不会自动检测到新安装的包。必须重启服务才能让新安装的 `greenlet` 模块被正确加载。

## 确认问题已解决

重启后，检查日志文件应该不再有 greenlet 相关的错误：

```bash
# 查看最新日志
tail -f backend_fastapi/logs/app.log
```

如果看到类似这样的日志，说明服务正常：

```
[INFO] 📥 GET /api/v1/logs/statistics from 127.0.0.1
[INFO] 📤 GET /api/v1/logs/statistics [200] 0.050s
```

---

**更新时间**: 2025-10-27  
**问题状态**: ✅ 已确认 - 需要重启后端服务

