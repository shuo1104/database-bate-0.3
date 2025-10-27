# 🚀 FastAPI 后端快速启动指南

**光创化物 R&D 配方数据库管理系统 - 3分钟启动！**

---

## ⚡ 一键启动（3步）

### **第1步: 安装依赖** (30秒)

```bash
cd backend_fastapi
pip install -r requirements.txt
```

### **第2步: 配置数据库** (1分钟)

创建配置文件 `env/.env.dev` (或编辑已存在的文件):

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_DATABASE=test_base

# JWT密钥（生产环境必须修改）
SECRET_KEY=your-secret-key-change-in-production-光创化物
```

### **第3步: 启动服务** (10秒)

```bash
python main.py run --env=dev
```

**看到以下输出表示成功：**

```
╔═══════════════════════════════════════════════════════════╗
║   光创化物 R&D 配方数据库管理系统 - FastAPI版本        ║
╚═══════════════════════════════════════════════════════════╝

🚀 应用启动中... 环境: dev
📖 API文档: http://0.0.0.0:8000/docs
📖 ReDoc文档: http://0.0.0.0:8000/redoc
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🎯 立即体验

### **访问API文档**

打开浏览器访问:

- **Swagger UI**: http://localhost:8000/docs
  - 交互式API文档
  - 可直接测试所有接口

- **ReDoc**: http://localhost:8000/redoc
  - 更美观的文档展示

- **健康检查**: http://localhost:8000/health
  ```json
  {
    "status": "healthy",
    "version": "2.0.0",
    "environment": "dev"
  }
  ```

---

## 🧪 快速测试

### **方式1: 使用Swagger UI（最简单）**

1. 打开 http://localhost:8000/docs
2. 找到 `POST /api/v1/auth/login`
3. 点击 "Try it out"
4. 输入登录信息（如果数据库中有用户）:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
5. 点击 "Execute"
6. 复制返回的 `access_token`
7. 点击页面右上角 "Authorize"
8. 输入 `Bearer <your_token>`
9. 现在可以测试所有需要认证的接口！

### **方式2: 使用测试脚本（自动化）**

```bash
# 测试认证模块
python test_api.py

# 测试所有模块
python test_all_modules.py
```

### **方式3: 使用curl（命令行）**

```bash
# 1. 注册用户
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456",
    "real_name": "测试用户"
  }'

# 2. 登录获取Token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456"
  }'

# 3. 使用Token访问（替换YOUR_TOKEN）
curl -X GET "http://localhost:8000/api/v1/auth/current/info" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 可用的API接口

### **1. 认证管理** (5个)

| 接口 | 方法 | 路径 | 需要认证 |
|------|------|------|----------|
| 用户登录 | POST | `/api/v1/auth/login` | ❌ |
| 用户注册 | POST | `/api/v1/auth/register` | ❌ |
| 获取用户信息 | GET | `/api/v1/auth/current/info` | ✅ |
| 更新个人信息 | PUT | `/api/v1/auth/current/profile` | ✅ |
| 修改密码 | PUT | `/api/v1/auth/current/password` | ✅ |

### **2. 项目管理** (13个)

| 接口 | 方法 | 路径 | 功能 |
|------|------|------|------|
| 项目列表 | GET | `/api/v1/projects/list` | 分页查询 |
| 项目详情 | GET | `/api/v1/projects/{id}` | 包含配方成分 |
| 创建项目 | POST | `/api/v1/projects/create` | 自动生成配方编码 |
| 更新项目 | PUT | `/api/v1/projects/{id}` | 更新基本信息 |
| 删除项目 | DELETE | `/api/v1/projects/{id}` | 级联删除 |
| 批量删除 | POST | `/api/v1/projects/batch/delete` | 批量操作 |
| 项目类型 | GET | `/api/v1/projects/config/types` | 配置接口 |
| 配方设计师 | GET | `/api/v1/projects/config/formulators` | 配置接口 |
| 配方成分列表 | GET | `/api/v1/projects/{id}/compositions` | 查询成分 |
| 添加成分 | POST | `/api/v1/projects/compositions/create` | 添加原料/填料 |
| 删除成分 | DELETE | `/api/v1/projects/compositions/{id}` | 删除成分 |

### **3. 原料管理** (10个)

| 接口 | 方法 | 路径 | 功能 |
|------|------|------|------|
| 原料列表 | GET | `/api/v1/materials/list` | 分页+筛选 |
| 原料详情 | GET | `/api/v1/materials/{id}` | 详细信息 |
| 创建原料 | POST | `/api/v1/materials/create` | 新增原料 |
| 更新原料 | PUT | `/api/v1/materials/{id}` | 更新信息 |
| 删除原料 | DELETE | `/api/v1/materials/{id}` | 删除 |
| 批量删除 | POST | `/api/v1/materials/batch/delete` | 批量操作 |
| 原料类别 | GET | `/api/v1/materials/config/categories` | 配置接口 |
| 供应商列表 | GET | `/api/v1/materials/config/suppliers` | 配置接口 |

### **4. 填料管理** (10个)

**说明**: 与原料管理结构完全相同，路径为 `/api/v1/fillers/*`

---

## 🔧 常见问题

### **Q1: 启动报错 "No module named 'fastapi'"**

**A**: 依赖未安装
```bash
pip install -r requirements.txt
```

### **Q2: 数据库连接失败**

**A**: 检查配置文件 `env/.env.dev`
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=你的实际密码
DB_DATABASE=test_base
```

确保MySQL服务已启动，数据库 `test_base` 已创建。

### **Q3: 端口被占用**

**A**: 修改端口
```env
# 在 env/.env.dev 中修改
SERVER_PORT=8001
```

### **Q4: 401 Unauthorized 错误**

**A**: Token未设置或已过期
1. 重新登录获取新Token
2. 在Swagger UI中点击右上角 "Authorize"
3. 输入 `Bearer <your_token>`

### **Q5: 需要初始化管理员账号**

**A**: 两种方式

**方式1**: 通过API注册
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "real_name": "管理员"
  }'
```

**方式2**: 使用Flask版本的脚本
```bash
cd ..  # 回到项目根目录
python scripts/create_admin.py
```

---

## 📂 项目文件结构

```
backend_fastapi/
├── main.py                     # 🚀 启动入口
├── requirements.txt            # 📦 依赖列表
├── test_api.py                 # 🧪 认证测试
├── test_all_modules.py         # 🧪 完整测试
├── env/
│   └── .env.dev               # ⚙️ 环境配置
├── app/
│   ├── config/                # ⚙️ 配置管理
│   ├── core/                  # 💖 核心功能
│   ├── common/                # 📦 公共模块
│   ├── plugin/                # 🔌 插件系统
│   └── api/v1/modules/
│       ├── auth/              # 🔐 认证管理
│       ├── projects/          # 📊 项目管理
│       └── materials/         # 🧪 原料管理
└── logs/                      # 📝 日志目录
    ├── app.log
    └── error.log
```

---

## 💡 有用的命令

```bash
# 启动开发服务器
python main.py run --env=dev

# 查看帮助
python main.py --help

# 测试API
python test_api.py
python test_all_modules.py

# 查看日志
tail -f logs/app.log
tail -f logs/error.log
```

---

## 🎨 响应格式

所有API统一返回JSON格式：

### **成功响应**
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    // 实际数据
  },
  "success": true
}
```

### **分页响应**
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "list": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "success": true
}
```

### **错误响应**
```json
{
  "code": 400,
  "msg": "错误信息",
  "success": false
}
```

---

## 📖 更多文档

- 📖 [README.md](./README.md) - 项目概览
- 📖 [GETTING_STARTED.md](./GETTING_STARTED.md) - 5分钟快速上手
- 📖 [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - 迁移指南
- 📖 [MIGRATION_COMPLETED.md](./MIGRATION_COMPLETED.md) - 完成报告

---

## 🚀 下一步

1. ✅ **熟悉API文档**
   - 浏览 Swagger UI
   - 了解所有接口

2. ✅ **测试API**
   - 使用 test_all_modules.py
   - 在Swagger UI中手动测试

3. ✅ **开始前端开发**
   - 对接后端API
   - 构建Vue3前端

4. ✅ **部署到生产**
   - 修改生产环境配置
   - Docker容器化
   - Nginx反向代理

---

## 🎉 开始使用

**现在您可以开始使用FastAPI后端了！**

```bash
# 启动服务
python main.py run --env=dev

# 打开浏览器访问
# http://localhost:8000/docs
```

**祝您使用愉快！** 🚀

---

**版本**: 2.0.0  
**更新日期**: 2025-10-24  
**维护**: 光创化物 R&D

