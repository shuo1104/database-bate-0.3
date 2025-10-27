# 光创化物 R&D 配方数据库管理系统 - FastAPI 后端

**化学配方数据管理系统后端 - 基于 FastAPI 的现代化重构版本**

版本: 2.0.0

---

## 📋 项目概述

这是将原 Flask 项目迁移到 FastAPI 架构的后端系统，采用现代化的异步架构和前后端分离设计。

### **核心改进**

| 项目 | 原架构 (Flask) | 新架构 (FastAPI) |
|------|---------------|------------------|
| **框架** | Flask 2.3 (同步) | FastAPI 0.115 (异步) |
| **认证** | Session + Cookie | JWT (Access + Refresh Token) |
| **数据库** | 原生 mysql-connector | SQLAlchemy 2.0 异步 |
| **架构** | Blueprint | 分层架构 (Model/Schema/CRUD/Service/Controller) |
| **文档** | 手动 Swagger | 自动生成 Swagger/ReDoc |

---

## 🏗️ 项目结构

```
backend_fastapi/
├── main.py                  # 应用入口
├── requirements.txt         # Python依赖
├── env/                     # 环境配置
│   └── .env.dev            # 开发环境配置
├── app/
│   ├── api/v1/             # API版本1
│   │   └── modules/        # 业务模块
│   │       ├── auth/       # 认证模块 ✅
│   │       │   ├── model.py      # ORM模型
│   │       │   ├── schema.py     # Pydantic模型
│   │       │   ├── crud.py       # 数据访问层
│   │       │   ├── service.py    # 业务逻辑层
│   │       │   └── controller.py # 路由控制器
│   │       ├── projects/   # 项目管理 🚧
│   │       ├── materials/  # 原料管理 🚧
│   │       ├── fillers/    # 填料管理 🚧
│   │       └── formulas/   # 配方管理 🚧
│   ├── core/               # 核心模块
│   │   ├── database.py     # 数据库引擎
│   │   ├── security.py     # JWT认证
│   │   ├── logger.py       # 日志系统
│   │   ├── middlewares.py  # 中间件
│   │   └── exceptions.py   # 异常处理
│   ├── common/             # 公共模块
│   │   └── response.py     # 统一响应
│   ├── config/             # 配置管理
│   │   └── settings.py     # 系统配置
│   └── plugin/             # 插件系统
│       └── init_app.py     # 应用初始化
├── logs/                   # 日志目录
└── static/                 # 静态文件
```

---

## 🚀 快速开始

### **1. 安装依赖**

```bash
cd backend_fastapi
pip install -r requirements.txt
```

### **2. 配置环境变量**

编辑 `env/.env.dev` 文件：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_DATABASE=test_base

# JWT配置
SECRET_KEY=your-secret-key-change-in-production
```

### **3. 启动服务**

```bash
# 开发环境启动
python main.py run --env=dev
```

### **4. 访问文档**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

---

## 📚 API 文档

### **认证模块** (已完成 ✅)

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 用户登录 | POST | `/api/v1/auth/login` | 返回JWT令牌 |
| 用户注册 | POST | `/api/v1/auth/register` | 创建新用户 |
| 获取用户信息 | GET | `/api/v1/auth/current/info` | 需要认证 |
| 更新个人信息 | PUT | `/api/v1/auth/current/profile` | 需要认证 |
| 修改密码 | PUT | `/api/v1/auth/current/password` | 需要认证 |

### **示例请求**

#### 登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### 使用令牌访问

```bash
curl -X GET "http://localhost:8000/api/v1/auth/current/info" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔧 开发指南

### **分层架构规范**

每个业务模块遵循以下结构：

```
module_name/
├── model.py       # 1. ORM模型 - 数据库表定义
├── schema.py      # 2. Pydantic模型 - 请求/响应验证
├── crud.py        # 3. 数据访问层 - 数据库操作
├── service.py     # 4. 业务逻辑层 - 核心业务逻辑
└── controller.py  # 5. 控制器层 - HTTP路由
```

### **开发新模块步骤**

1. **创建模型** (`model.py`)
   ```python
   from app.core.database import Base
   
   class YourModel(Base):
       __tablename__ = "your_table"
       ...
   ```

2. **创建Schema** (`schema.py`)
   ```python
   from pydantic import BaseModel
   
   class YourRequest(BaseModel):
       field: str
   ```

3. **创建CRUD** (`crud.py`)
   ```python
   class YourCRUD:
       @staticmethod
       async def get_all(db: AsyncSession):
           ...
   ```

4. **创建Service** (`service.py`)
   ```python
   class YourService:
       @staticmethod
       async def list_items(db: AsyncSession):
           ...
   ```

5. **创建Controller** (`controller.py`)
   ```python
   router = APIRouter()
   
   @router.get("/list")
   async def list_items(db: AsyncSession = Depends(get_db)):
       ...
   ```

6. **注册路由** (`app/api/v1/__init__.py`)
   ```python
   from app.api.v1.modules.your_module.controller import router
   api_router.include_router(router, prefix="/your-module")
   ```

---

## ✅ 迁移进度

- [x] **项目结构搭建**
- [x] **核心配置迁移**
- [x] **数据库引擎** (异步SQLAlchemy 2.0)
- [x] **JWT认证系统**
- [x] **用户认证模块** (完整实现)
- [ ] **项目管理模块** (待迁移)
- [ ] **原料管理模块** (待迁移)
- [ ] **填料管理模块** (待迁移)
- [ ] **配方管理模块** (待迁移)
- [ ] **前端对接** (待开发)

---

## 📊 数据库表映射

| 原表名 | 模型类 | 状态 |
|--------|--------|------|
| `tbl_Users` | `UserModel` | ✅ 完成 |
| `tbl_ProjectInfo` | `ProjectModel` | 🚧 待迁移 |
| `tbl_RawMaterials` | `MaterialModel` | 🚧 待迁移 |
| `tbl_InorganicFillers` | `FillerModel` | 🚧 待迁移 |
| `tbl_FormulaComposition` | `FormulaModel` | 🚧 待迁移 |

---

## 🔒 安全特性

- ✅ JWT认证 (Access + Refresh Token)
- ✅ 密码Bcrypt加密
- ✅ Pydantic数据验证
- ✅ CORS中间件
- ✅ 请求日志记录
- ✅ 全局异常处理

---

## 📝 下一步计划

1. **继续迁移业务模块**
   - 项目管理模块
   - 原料/填料管理模块
   - 配方管理模块

2. **添加高级功能**
   - 数据库迁移 (Alembic)
   - 批量操作API
   - Excel导入导出
   - 文件上传

3. **前端开发**
   - Vue3 前端项目搭建
   - API对接
   - UI组件开发

---

## 🤝 贡献者

光创化物 R&D 团队

---

**最后更新**: 2025-10-24

