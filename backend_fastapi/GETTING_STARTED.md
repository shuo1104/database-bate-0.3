# 🚀 快速开始指南

**光创化物 R&D FastAPI 后端 - 5分钟快速上手**

---

## ⚡ 极速启动（3步）

### **第1步: 安装依赖**

```bash
cd backend_fastapi
pip install -r requirements.txt
```

### **第2步: 配置数据库**

编辑文件 `env/.env.dev` (已创建，需要编辑):

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_DATABASE=test_base
```

### **第3步: 启动服务**

```bash
python main.py run --env=dev
```

看到以下输出表示启动成功:

```
╔═══════════════════════════════════════════════════════════╗
║   光创化物 R&D 配方数据库管理系统 - FastAPI版本        ║
╚═══════════════════════════════════════════════════════════╝

🚀 应用启动中... 环境: dev
📖 API文档: http://0.0.0.0:8000/docs
📖 ReDoc文档: http://0.0.0.0:8000/redoc
```

---

## 📖 访问文档

启动后访问以下地址:

- **Swagger UI**: http://localhost:8000/docs
  - 交互式API文档
  - 可直接测试API
  
- **ReDoc**: http://localhost:8000/redoc
  - 更优雅的API文档展示

- **健康检查**: http://localhost:8000/health
  - 快速检查服务状态

---

## 🧪 测试API

### **方式1: 使用Swagger UI (推荐)**

1. 打开 http://localhost:8000/docs
2. 点击 `POST /api/v1/auth/register`
3. 点击 "Try it out"
4. 输入测试数据:
   ```json
   {
     "username": "testuser",
     "password": "test123456",
     "real_name": "测试用户"
   }
   ```
5. 点击 "Execute"

### **方式2: 使用测试脚本**

```bash
python test_api.py
```

### **方式3: 使用curl**

```bash
# 注册用户
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456",
    "real_name": "测试用户"
  }'

# 登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456"
  }'
```

---

## 🔧 环境配置说明

### **配置文件位置**

```
env/
└── .env.dev    # 开发环境配置
```

### **完整配置项**

```env
# ==================== 环境 ====================
ENVIRONMENT=dev

# ==================== 服务器配置 ====================
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
RELOAD=True  # 开发环境自动重载
WORKERS=1

# ==================== 数据库配置 ====================
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root  # ⚠️ 请修改为实际密码
DB_DATABASE=test_base
DB_CHARSET=utf8mb4

# ==================== JWT配置 ====================
SECRET_KEY=dev-secret-key-光创化物-change-in-production  # ⚠️ 生产环境必须修改
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 1天
REFRESH_TOKEN_EXPIRE_MINUTES=10080  # 7天

# ==================== Redis配置（可选） ====================
REDIS_ENABLE=False
REDIS_HOST=localhost
REDIS_PORT=6379

# ==================== 调试配置 ====================
DEBUG=True
LOG_LEVEL=INFO
```

---

## 📊 数据库准备

### **使用现有数据库**

如果你已经有Flask版本的数据库，**可以直接使用**！

新版本兼容原有的数据库表结构，只需确保配置正确即可。

### **创建新数据库**

```sql
CREATE DATABASE test_base
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE test_base;

-- 用户表会自动创建（如果不存在）
```

### **初始化管理员账号**

你可以:

1. 使用原有的管理员账号登录
2. 或通过API注册新用户:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "admin123",
       "real_name": "管理员"
     }'
   ```

---

## 🐛 常见问题

### **Q1: 启动时报错 "No module named 'fastapi'"**

**A**: 依赖未安装，请运行:
```bash
pip install -r requirements.txt
```

### **Q2: 数据库连接失败**

**A**: 检查配置文件:
```bash
# 确认 env/.env.dev 中的数据库配置是否正确
# 特别是密码 DB_PASSWORD
```

### **Q3: JWT认证失败**

**A**: 确保请求头包含正确的Token:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### **Q4: 端口被占用**

**A**: 修改配置文件中的端口:
```env
SERVER_PORT=8001  # 改为其他端口
```

---

## 📂 项目结构速览

```
backend_fastapi/
├── main.py                     # 🚀 启动入口
├── requirements.txt            # 📦 依赖列表
├── test_api.py                 # 🧪 测试脚本
├── README.md                   # 📖 项目说明
├── GETTING_STARTED.md          # 📖 本文档
├── MIGRATION_GUIDE.md          # 📖 迁移指南
├── env/
│   └── .env.dev               # ⚙️ 环境配置
├── app/
│   ├── api/v1/modules/
│   │   └── auth/              # ✅ 认证模块（已完成）
│   ├── core/                  # 💖 核心功能
│   ├── config/                # ⚙️ 配置管理
│   └── common/                # 📦 公共模块
└── logs/                      # 📝 日志目录
```

---

## 🎯 下一步

1. **熟悉API文档**
   - 访问 http://localhost:8000/docs
   - 测试所有认证相关接口

2. **查看代码**
   - 从 `app/api/v1/modules/auth/` 开始
   - 了解分层架构

3. **开始开发**
   - 参考 `MIGRATION_GUIDE.md`
   - 迁移其他业务模块

---

## 💡 有用的命令

```bash
# 启动开发服务器
python main.py run --env=dev

# 查看帮助
python main.py --help

# 测试API
python test_api.py

# 查看日志
tail -f logs/app.log
```

---

## 📞 获取帮助

遇到问题？查看以下文档:

- 📖 [README.md](./README.md) - 项目概览
- 📖 [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - 迁移指南
- 📖 代码注释 - 每个文件都有详细注释
- 📖 API文档 - http://localhost:8000/docs

---

**祝你使用愉快！** 🎉

---

**文档版本**: 1.0  
**最后更新**: 2025-10-24

