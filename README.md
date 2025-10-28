# Advanced - PhotoPolymer Formulation Management DB

## 高级光敏聚合物配方管理数据库

一个基于 FastAPI + Vue 3 的现代化光敏聚合物配方管理系统，用于管理项目、原料、填料、配方和测试结果。

## 🚀 项目特性

### 后端 (FastAPI)
- ✅ 基于 FastAPI 的高性能 RESTful API
- ✅ SQLAlchemy ORM 数据库管理
- ✅ JWT 身份认证与授权
- ✅ 完整的 CRUD 操作
- ✅ 图片导出功能（项目报告）
- ✅ 系统日志记录
- ✅ 用户权限管理

### 前端 (Vue 3)
- ✅ Vue 3 + TypeScript + Vite
- ✅ Element Plus UI 组件库
- ✅ UnoCSS 原子化 CSS
- ✅ Pinia 状态管理
- ✅ Vue Router 路由管理
- ✅ 响应式设计
- ✅ 暗黑/白天主题切换
- ✅ 现代化交互体验

## 📦 项目结构

```
data_base/
├── backend_fastapi/        # FastAPI 后端
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心功能（数据库、安全等）
│   │   ├── config/        # 配置文件
│   │   ├── utils/         # 工具函数
│   │   └── scripts/       # 数据库脚本
│   ├── logs/              # 日志文件
│   ├── static/            # 静态文件
│   ├── main.py            # 应用入口
│   └── requirements.txt   # Python 依赖
│
├── frontend_vue3/         # Vue 3 前端
│   ├── src/
│   │   ├── api/          # API 接口
│   │   ├── components/   # 公共组件
│   │   ├── composables/  # 组合式函数
│   │   ├── layouts/      # 布局组件
│   │   ├── router/       # 路由配置
│   │   ├── store/        # 状态管理
│   │   ├── styles/       # 全局样式
│   │   ├── utils/        # 工具函数
│   │   └── views/        # 页面组件
│   ├── package.json      # Node 依赖
│   └── vite.config.ts    # Vite 配置
│
├── START_SERVICES.bat     # 启动服务（Windows）
└── START_DEV_SERVICES.bat # 开发环境启动（Windows）
```

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL / MySQL
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT (python-jose)
- **密码加密**: Passlib + Bcrypt
- **图片处理**: Pillow + Matplotlib
- **日志**: Python logging

### 前端
- **框架**: Vue 3.3+
- **语言**: TypeScript 5.0+
- **构建工具**: Vite 5.0+
- **UI 组件**: Element Plus
- **CSS 框架**: UnoCSS
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios

## 📋 功能模块

### 1. 用户管理
- 用户注册与登录
- 角色权限管理（管理员/普通用户）
- 用户信息编辑
- 密码修改

### 2. 项目管理
- 项目 CRUD 操作
- 项目详情查看
- 项目报告导出（图片）
- 项目统计

### 3. 原料管理
- 原料信息维护
- 原料分类
- 供应商信息
- 原料库存

### 4. 填料管理
- 填料信息维护
- 填料分类
- 填料属性管理

### 5. 配方管理
- 配方创建与编辑
- 配方组成管理
- 配方版本控制

### 6. 测试结果
- 测试数据录入
- 测试结果查询
- 数据可视化

### 7. 系统日志
- 登录日志
- 操作日志
- 系统统计

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- PostgreSQL / MySQL
- pnpm (推荐) 或 npm

### 后端启动

```bash
# 进入后端目录
cd backend_fastapi

# 创建虚拟环境（可选）
python -m venv env
.\env\Scripts\activate  # Windows
# source env/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置数据库（修改 app/config/settings.py）

# 启动服务
python main.py
# 或
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将在 `http://localhost:8000` 运行

### 前端启动

```bash
# 进入前端目录
cd frontend_vue3

# 安装依赖
pnpm install
# 或
npm install

# 启动开发服务器
pnpm dev
# 或
npm run dev
```

前端服务将在 `http://localhost:3000` 运行

### 一键启动（Windows）

```bash
# 开发环境
START_DEV_SERVICES.bat

# 生产环境
START_SERVICES.bat
```

## 🎨 主题系统

系统支持暗黑/白天主题切换：
- 点击右上角的太阳/月亮图标切换主题
- 主题偏好自动保存到本地存储
- 跨标签页主题同步
- 完整的暗黑模式适配

## 📝 默认账号

系统初始化后会创建默认管理员账号：

```
用户名: admin
密码: admin123
```

**⚠️ 生产环境请立即修改默认密码！**

## 🔧 配置说明

### 后端配置

编辑 `backend_fastapi/app/config/settings.py`：

```python
# 数据库配置
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"

# JWT 配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS 配置
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
```

### 前端配置

编辑 `frontend_vue3/src/settings.ts`：

```typescript
// API 基础地址
export const API_BASE_URL = 'http://localhost:8000'

// 应用配置
export const APP_NAME = '材料配方管理系统'
export const APP_VERSION = '1.0.0'
```

## 📊 数据库初始化

```bash
cd backend_fastapi

# 运行初始化脚本
python app/scripts/create_log_tables.py

# 创建管理员账号
python -c "from app.api.v1.modules.auth.service import AuthService; AuthService.create_default_admin()"
```

## 🐛 常见问题

### 1. 后端启动失败
- 检查 Python 版本是否 >= 3.9
- 检查数据库连接配置
- 检查端口 8000 是否被占用

### 2. 前端启动失败
- 检查 Node.js 版本是否 >= 16
- 删除 `node_modules` 重新安装依赖
- 检查端口 3000 是否被占用

### 3. 跨域问题
- 确保后端 CORS 配置包含前端地址
- 检查前端 API 请求地址是否正确

### 4. 登录失败
- 检查数据库是否已创建用户
- 检查密码是否正确
- 查看浏览器控制台和后端日志

## 📄 许可证

本项目采用 MIT 许可证。

## 🏢 关于 Advanced

**Advanced** 是一家专注于光敏聚合物材料研发的高新技术企业，致力于为客户提供先进的配方管理解决方案。

## 👥 联系方式

如有问题或建议，请联系开发团队。

---

**项目名称**: Advanced - PhotoPolymer Formulation Management DB  
**开发时间**: 2025年10月  
**最后更新**: 2025年10月28日  
**版本**: 2.0.0

