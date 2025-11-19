# 路径修改总结

## 📝 修改的文件

### 1. 后端 Systemd 服务配置
**文件**: `backend_fastapi/depoly/photopolymer-api.service`

| 配置项 | 原值 | 新值 | 说明 |
|--------|------|------|------|
| User | `%u` | `xgs` | 使用绝对用户名 |
| Group | `%u` | `xgs` | 使用绝对组名 |
| WorkingDirectory | `%h/workspace/data_base/database-bate-0.3/backend_fastapi` | `/home/xgs/workspace/database-bate-0.3/backend_fastapi` | ❌ 路径错误：`data_base` 目录不存在 |
| Environment PATH | `%h/venv/database/bin:...` | `/home/xgs/venv/database/bin:...` | 使用绝对路径 |
| Environment PYTHONPATH | `%h/workspace/data_base/database-bate-0.3/backend_fastapi` | `/home/xgs/workspace/database-bate-0.3/backend_fastapi` | ❌ 路径错误：`data_base` 目录不存在 |
| ExecStart | `%h/venv/database/bin/python %h/workspace/data_base/database-bate-0.3/backend_fastapi/main.py --env=prod` | `/home/xgs/venv/database/bin/python /home/xgs/workspace/database-bate-0.3/backend_fastapi/main.py --env=prod` | ❌ 路径错误：`data_base` 目录不存在 |

---

### 2. 前端 Nginx 配置
**文件**: `frontend_vue3/depoly/photopolymer-frontend.conf`

| 配置项 | 原值 | 新值 | 说明 |
|--------|------|------|------|
| root | `__PROJECT_ROOT__/frontend_vue3/dist` | `/home/xgs/workspace/database-bate-0.3/frontend_vue3/dist` | ❌ 占位符未替换 |
| proxy_pass | `http://localhost:8080` | `http://localhost:8000` | ❌ 端口错误：应该代理到后端的 8000 端口 |

---

## 🔍 发现的主要问题

### 问题 1: `data_base` 目录不存在
**错误路径**: `/home/xgs/workspace/data_base/database-bate-0.3/`  
**正确路径**: `/home/xgs/workspace/database-bate-0.3/`  
**影响**: 导致后端服务无法启动（CHDIR 错误）

### 问题 2: API 代理端口错误
**错误配置**: `proxy_pass http://localhost:8080;`  
**正确配置**: `proxy_pass http://localhost:8000;`  
**影响**: 前端无法调用后端 API（会形成循环代理）

### 问题 3: 使用了占位符和变量
**错误**: `__PROJECT_ROOT__`, `%h`, `%u`  
**正确**: 使用绝对路径  
**影响**: 配置文件无法正确解析路径

---

## ✅ 部署步骤

### 方法 1: 使用自动更新脚本（推荐）
```bash
cd /home/xgs/workspace/database-bate-0.3
bash update_configs.sh
```

### 方法 2: 手动更新
```bash
# 1. 停止服务
sudo systemctl stop photopolymer-api.service

# 2. 更新后端配置
sudo cp backend_fastapi/depoly/photopolymer-api.service /etc/systemd/system/
sudo systemctl daemon-reload

# 3. 更新前端配置
sudo cp frontend_vue3/depoly/photopolymer-frontend.conf /etc/nginx/sites-available/photopolymer
sudo ln -sf /etc/nginx/sites-available/photopolymer /etc/nginx/sites-enabled/photopolymer
sudo nginx -t

# 4. 启动服务
sudo systemctl start photopolymer-api.service
sudo systemctl reload nginx

# 5. 检查状态
sudo systemctl status photopolymer-api.service
sudo systemctl status nginx
```

---

## 📋 关键路径清单

```
项目根目录:        /home/xgs/workspace/database-bate-0.3
后端目录:          /home/xgs/workspace/database-bate-0.3/backend_fastapi
前端目录:          /home/xgs/workspace/database-bate-0.3/frontend_vue3
前端构建目录:      /home/xgs/workspace/database-bate-0.3/frontend_vue3/dist
虚拟环境目录:      /home/xgs/venv/database
Python 解释器:     /home/xgs/venv/database/bin/python
```

---

## 🔧 验证命令

```bash
# 检查后端服务
sudo systemctl status photopolymer-api.service

# 检查后端日志
sudo journalctl -u photopolymer-api.service -n 50 --no-pager

# 检查端口监听
sudo lsof -i :8000  # 后端
sudo lsof -i :8080  # 前端

# 测试访问
curl http://localhost:8000/docs  # 后端 API 文档
curl http://localhost:8080       # 前端页面
```

---

## 📚 相关文档

- 详细路径配置说明: `doc/路径配置说明.md`
- 部署说明: `doc/部署说明.md`
- 生产环境部署指南: `doc/PRODUCTION_DEPLOYMENT_GUIDE.md`

---

**修改日期**: 2025-11-19  
**修改人**: AI Assistant  
**版本**: 1.0

