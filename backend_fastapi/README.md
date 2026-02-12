# PhotoPolymer 配方管理系统 - 后端

基于 **FastAPI** 的高性能异步 API 服务。

## ✨ 技术栈

- **FastAPI 0.104** - 高性能异步 Web 框架
- **SQLAlchemy 2.0** - ORM（异步）
- **PostgreSQL 14+** - 关系型数据库
- **Asyncpg** - PostgreSQL 异步驱动
- **JWT** - 身份认证
- **Bcrypt** - 密码加密
- **Matplotlib** - 图表生成

## 🚀 快速开始

## ⚙️ 运行约定

- 统一使用 **conda 的 `database` 虚拟环境**。
- 一切配置与部署遵守 **“更换生成服务器环境后能快速移植部署”** 的原则。

### 安装依赖

```bash
conda activate database
cd backend_fastapi
pip install -r requirements.txt
```

### 配置数据库

编辑 `env/.env.dev` 文件：

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_DATABASE=photopolymer_db

SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 初始化数据库

```bash
python scripts/create_tables.py
```

### 启动服务

```bash
python main.py
```

服务地址：http://localhost:8000  
API 文档：http://localhost:8000/docs

## 📁 项目结构

```
backend_fastapi/
├── app/
│   ├── api/v1/              # API 版本 1
│   │   └── modules/         # 业务模块
│   │       ├── auth/        # 认证模块
│   │       ├── projects/    # 项目管理
│   │       ├── materials/   # 原料管理
│   │       ├── fillers/     # 填料管理
│   │       ├── formulas/    # 配方管理
│   │       ├── test_results/# 测试结果
│   │       └── logs/        # 系统日志
│   ├── core/                # 核心模块
│   │   ├── database.py      # 数据库引擎
│   │   ├── security.py      # JWT 认证
│   │   ├── logger.py        # 日志系统
│   │   ├── middlewares.py   # 中间件
│   │   └── exceptions.py    # 异常处理
│   ├── config/              # 配置管理
│   │   └── settings.py      # 系统配置
│   └── utils/               # 工具函数
│       └── chart_generator.py # 图表生成
├── scripts/                 # 脚本工具
│   ├── create_tables.py     # 创建数据库表
│   ├── generate_test_data.py # 生成测试数据
│   └── DATA_GENERATION_README.md # 数据生成说明
├── logs/                    # 日志文件
├── static/                  # 静态文件
├── main.py                  # 应用入口
└── requirements.txt         # Python 依赖
```

## 🏗️ 分层架构

每个业务模块遵循分层架构：

```
module/
├── model.py       # ORM 模型（数据库表定义）
├── schema.py      # Pydantic 模型（请求/响应验证）
├── crud.py        # 数据访问层（数据库操作）
├── service.py     # 业务逻辑层（核心业务逻辑）
└── controller.py  # 控制器层（HTTP 路由）
```

## 📚 API 文档

### 认证模块

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 用户登录 | POST | `/api/v1/auth/login` | 返回 JWT 令牌 |
| 获取用户信息 | GET | `/api/v1/auth/current/info` | 需要认证 |
| 更新个人信息 | PUT | `/api/v1/auth/current/profile` | 需要认证 |
| 修改密码 | PUT | `/api/v1/auth/current/password` | 需要认证 |
| 获取用户列表 | GET | `/api/v1/auth/users` | 管理员 |
| 创建用户 | POST | `/api/v1/auth/users` | 管理员 |

### 项目管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取项目列表 | GET | `/api/v1/projects` | 分页查询 |
| 创建项目 | POST | `/api/v1/projects` | - |
| 获取项目详情 | GET | `/api/v1/projects/{id}` | - |
| 更新项目 | PUT | `/api/v1/projects/{id}` | - |
| 删除项目 | DELETE | `/api/v1/projects/{id}` | - |
| 导出项目报告 | GET | `/api/v1/projects/{id}/export` | 图片格式 |

### 配方管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取配方列表 | GET | `/api/v1/formulas` | 按项目查询 |
| 创建配方 | POST | `/api/v1/formulas` | - |
| 更新配方 | PUT | `/api/v1/formulas/{id}` | - |
| 删除配方 | DELETE | `/api/v1/formulas/{id}` | - |

## 🔐 安全特性

- ✅ JWT 认证（Access + Refresh Token）
- ✅ 密码 Bcrypt 加密
- ✅ Pydantic 数据验证
- ✅ CORS 中间件
- ✅ 请求日志记录
- ✅ 全局异常处理
- ✅ SQL 注入防护

## 📊 数据库

### 主要数据表

- `tbl_Users` - 用户表
- `tbl_ProjectInfo` - 项目信息表
- `tbl_ProjectType` - 项目类型表
- `tbl_RawMaterials` - 原料表
- `tbl_InorganicFillers` - 填料表
- `tbl_FormulaComposition` - 配方组成表
- `tbl_TestResults_*` - 测试结果表（按项目类型分表）
- `tbl_LoginLogs` - 登录日志表
- `tbl_RegistrationLogs` - 注册日志表

### 数据生成

```bash
# 生成 99 万条项目记录
python scripts/generate_test_data.py

# 生成原料和填料数据
python scripts/generate_materials_fillers.py
```

## 📝 日志系统

### 日志轮转策略
- **轮转方式**：按日期（每天午夜）
- **文件命名**：
  - 当前日志：`app.log` / `error.log`
  - 历史日志：`app.log.YYYY-MM-DD` / `error.log.YYYY-MM-DD`
- **保留策略**：保留最近 N 天（`LOG_BACKUP_COUNT` 配置）
- **日志级别**：
  - `app.log`：INFO 及以上
  - `error.log`：ERROR 及以上

### 日志格式
```
[2025-10-30 14:30:45] INFO [fastapi_app:123] - User login successful
```

## 🛠️ 开发指南

### 创建新模块

1. 在 `app/api/v1/modules/` 创建模块目录
2. 创建 `model.py`（ORM 模型）
3. 创建 `schema.py`（Pydantic 模型）
4. 创建 `crud.py`（数据访问层）
5. 创建 `service.py`（业务逻辑层）
6. 创建 `controller.py`（路由控制器）
7. 在 `app/api/v1/__init__.py` 注册路由

### 示例代码

```python
# controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/list")
async def get_list(db: AsyncSession = Depends(get_db)):
    # 调用 service 层
    result = await YourService.get_list(db)
    return {"data": result}
```

## 🐛 常见问题

### 数据库连接失败

1. 检查 PostgreSQL 服务是否运行
2. 检查 `.env.dev` 配置是否正确
3. 检查数据库是否已创建

### 导入错误

确保在虚拟环境中运行：

```bash
.\env\Scripts\activate  # Windows
source env/bin/activate # Linux/Mac
```

### 端口被占用

修改 `main.py` 中的端口号：

```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 📄 许可证

MIT License
