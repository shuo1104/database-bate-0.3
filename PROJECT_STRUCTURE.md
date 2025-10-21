# 项目结构说明

## 目录树

```
data_base/
├── 📄 app.py                          # Flask 应用主入口
├── 📄 .env                            # 环境变量配置（不提交到Git）
├── 📄 requirements.txt                # Python 依赖包
├── 📄 requirements-dev.txt            # 开发环境依赖
├── 📄 pytest.ini                      # Pytest 配置
├── 📄 README.md                       # 项目说明
├── 📄 QUICK_START.md                  # 快速启动指南
│
├── 📁 api/                            # API 相关模块
│   ├── __init__.py
│   ├── auth.py                        # JWT 认证实现
│   ├── docs.py                        # OpenAPI 文档生成
│   └── routes/                        # API 路由模块（可扩展）
│
├── 📁 blueprints/                     # Flask 蓝图（功能模块）
│   ├── __init__.py
│   ├── api.py                         # RESTful API 路由
│   ├── auth.py                        # 用户认证（登录/登出/用户管理）
│   ├── projects.py                    # 项目管理
│   ├── materials.py                   # 原料管理
│   ├── fillers.py                     # 无机材料管理
│   └── formulas.py                    # 配方成分管理
│
├── 📁 config/                         # 配置模块
│   ├── __init__.py
│   ├── config.py                      # 主配置文件（从.env加载）
│   ├── production.py                  # 生产环境特定配置
│   ├── env.example                    # 环境变量示例
│   └── env.production.example         # 生产环境变量示例
│
├── 📁 core/                           # 核心工具模块
│   ├── __init__.py
│   ├── constants.py                   # 常量定义
│   ├── extensions.py                  # Flask 扩展集中管理（CSRF, Limiter, CORS）
│   ├── logger.py                      # 日志系统配置
│   ├── utils.py                       # 通用工具函数（数据库连接、JSON序列化等）
│   └── validators.py                  # 输入验证函数
│
├── 📁 scripts/                        # 数据库和部署脚本
│   ├── create_tables.py               # 创建数据库表结构
│   ├── seed_data.py                   # 导入基础配置数据
│   ├── create_admin.py                # 创建管理员账号
│   ├── check_ready.py                 # 环境就绪检查
│   └── deploy.sh                      # 部署脚本（Linux）
│
├── 📁 templates/                      # Jinja2 HTML 模板
│   ├── layout.html                    # 主布局模板
│   ├── layout_embedded.html           # 嵌入式布局（iframe）
│   ├── login.html                     # 登录页面
│   ├── index.html                     # 主页（导航）
│   └── ... (其他模板文件)
│
├── 📁 tests/                          # 单元测试
│   ├── __init__.py
│   ├── conftest.py                    # Pytest 配置
│   ├── test_app.py                    # 应用测试
│   ├── test_utils.py                  # 工具函数测试
│   └── test_validators.py             # 验证器测试
│
├── 📁 logs/                           # 日志文件
│   ├── app.log                        # 应用日志
│   └── error.log                      # 错误日志
│
├── 📁 sql/                            # SQL 脚本
│   └── database_indexes.sql           # 数据库索引优化
│
└── 📁 docs/                           # 项目文档
    ├── API_GUIDE.md                   # API 使用指南
    ├── CHANGELOG.md                   # 变更日志
    ├── DEPLOYMENT_CHECKLIST.md        # 部署检查清单
    ├── REPO_CLEANUP.md                # 代码库整理记录
    ├── SECURITY_REPORT.md             # 安全审计报告
    │
    ├── fixes/                         # 问题修复记录
    │   ├── ALL_CSRF_FIXED.md          # CSRF 修复记录
    │   ├── CSRF_FIXED.md              # CSRF 初次修复
    │   └── FIXED_IMPORTS.md           # 导入路径修复
    │
    ├── improvements/                  # 改进记录
    │   ├── IMPROVEMENTS_ROUND2.md     # 第二轮改进
    │   ├── IMPROVEMENTS_ROUND3.md     # 第三轮改进
    │   └── IMPROVEMENTS_ROUND4.md     # 第四轮改进（前后端分离）
    │
    ├── reports/                       # 最终报告
    │   ├── FINAL_REPORT.md            # 最终改进报告
    │   └── FINAL_SUMMARY.md           # 总结
    │
    └── needs/                         # 需求文档
        ├── 需求1.docx
        └── 需求2-详细整体需求.pdf
```

## 核心模块说明

### 1. `app.py` - 应用入口
- Flask 应用初始化
- 扩展配置（CSRF、CORS、Limiter）
- 蓝图注册
- 全局错误处理
- 安全响应头配置

### 2. `api/` - API 模块
- **auth.py**: JWT 令牌生成、验证、装饰器
- **docs.py**: OpenAPI 规范生成

### 3. `blueprints/` - 功能模块
每个蓝图负责一个功能领域：
- **api.py**: RESTful API 端点（/api/v1/*）
- **auth.py**: 用户认证和会话管理
- **projects.py**: 项目CRUD操作
- **materials.py**: 原料CRUD操作
- **fillers.py**: 无机材料CRUD操作
- **formulas.py**: 配方CRUD操作

### 4. `config/` - 配置管理
- **config.py**: 从环境变量加载配置
- **production.py**: 生产环境覆盖配置
- **.env**: 实际配置（不提交）
- **env.example**: 配置模板

### 5. `core/` - 核心工具
- **constants.py**: 系统常量（状态码、限制等）
- **extensions.py**: Flask 扩展集中初始化
- **logger.py**: 结构化日志配置
- **utils.py**: 数据库连接、JSON 序列化
- **validators.py**: 输入验证（用户名、密码、邮箱等）

### 6. `scripts/` - 管理脚本
- **create_tables.py**: 初始化数据库表
- **seed_data.py**: 导入基础数据
- **create_admin.py**: 创建管理员用户
- **check_ready.py**: 环境检查工具

### 7. `templates/` - 前端模板
- 使用 Bootstrap 5 + Bootstrap Icons
- 支持 iframe 嵌套架构
- 响应式设计
- CSRF 令牌集成

### 8. `tests/` - 测试套件
- 使用 pytest 框架
- 覆盖核心功能
- Fixture 复用

### 9. `docs/` - 文档中心
- API 指南
- 改进历史
- 安全报告
- 部署指南

## 关键配置文件

### `.env` - 环境变量
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=***
DB_DATABASE=test_base
DB_CHARSET=utf8mb4

FLASK_SECRET_KEY=***
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

SESSION_LIFETIME=28800

CORS_ENABLED=True
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

JWT_SECRET_KEY=***
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800
```

### `requirements.txt` - 依赖包
主要依赖：
- Flask 2.3+
- mysql-connector-python
- argon2-cffi
- flask-wtf
- flask-limiter
- flask-cors
- PyJWT
- python-dotenv

## 设计原则

1. **模块化**: 功能按蓝图分离
2. **安全优先**: CSRF、速率限制、输入验证、密码加密
3. **配置分离**: 敏感信息通过环境变量管理
4. **日志完善**: 结构化日志记录所有关键操作
5. **错误处理**: 全局异常捕获和优雅降级
6. **API 友好**: 同时支持传统 Web 和 RESTful API
7. **文档齐全**: 代码注释 + Markdown 文档

## 数据流

### Web 请求流程
```
浏览器 
  → Nginx（生产环境）
    → Gunicorn/Flask
      → Blueprint 路由
        → 业务逻辑
          → 数据库
            → 返回 HTML/JSON
```

### API 请求流程
```
客户端
  → /api/v1/* 
    → CORS 检查
      → JWT 验证
        → Blueprint API 路由
          → 业务逻辑
            → 数据库
              → 返回 JSON
```

---

**最后更新**: 2025-10-21
**维护者**: AI Assistant
