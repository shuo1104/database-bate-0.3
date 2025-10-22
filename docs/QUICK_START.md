# 快速启动指南

## 项目概述

这是一个使用 Flask 构建的 Advanced 配方数据管理系统，支持传统 Web 界面和 RESTful API。

## 技术栈

- **后端框架**: Flask 2.3+
- **数据库**: MySQL 5.7+
- **密码加密**: Argon2
- **认证**: Session (Web) + JWT (API)
- **安全**: CSRF 保护, 速率限制, 安全响应头
- **API 文档**: OpenAPI/Swagger

## 快速启动（5分钟）

### 1. 安装依赖

```bash
# 确保使用 Python 3.8+
pip install -r requirements.txt
```

### 2. 配置环境变量

项目根目录已有 `.env` 文件，请根据您的环境修改：

```env
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password  # 修改为您的MySQL密码
DB_DATABASE=test_base
DB_CHARSET=utf8mb4

# Flask配置
FLASK_SECRET_KEY=change_this_to_a_random_secret_key_in_production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 会话配置（秒）
SESSION_LIFETIME=28800

# CORS配置
CORS_ENABLED=True
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# JWT配置
JWT_SECRET_KEY=change_this_to_a_random_jwt_secret_key_in_production
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800
```

### 3. 初始化数据库

```bash
# 创建数据库表
python scripts/create_tables.py

# 导入基础配置数据
python scripts/seed_data.py

# 创建管理员账号
python scripts/create_admin.py
```

### 4. 启动应用

```bash
python app.py
```

访问: **http://localhost:5000**

默认管理员账号（如果使用 create_admin.py 创建）:
- 用户名: `admin`
- 密码: 创建时设置的密码

### 5. API 文档

访问 Swagger UI: **http://localhost:5000/api/docs/swagger**

## 常见问题

### Q1: 数据库连接失败

**错误**: `Collation 'utf8mb4_unicode_ci' unknown`

**解决**: 
- 检查 MySQL 版本是否支持 utf8mb4
- 已在配置中注释掉 collation，使用默认值

### Q2: CSRF 验证失败

**错误**: `The CSRF session token is missing`

**解决**:
- 确保 `.env` 文件中的 `FLASK_SECRET_KEY` 已设置
- 重启应用
- 清除浏览器 Cookie 后重试

### Q3: 页面样式丢失

**原因**: CSP（内容安全策略）过于严格

**解决**: 已在 `app.py` 中配置允许 CDN 资源加载

### Q4: 模块导入错误

**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
# 重新安装依赖
pip install -r requirements.txt
```

## 项目结构

```
data_base/
├── app.py                    # 主应用入口
├── .env                      # 环境变量配置
├── requirements.txt          # Python 依赖
│
├── api/                      # API 相关模块
│   ├── auth.py              # JWT 认证
│   └── docs.py              # API 文档生成
│
├── blueprints/              # Flask 蓝图
│   ├── api.py               # RESTful API 路由
│   ├── auth.py              # 用户认证
│   ├── projects.py          # 项目管理
│   ├── materials.py         # 原料管理
│   ├── fillers.py           # 无机材料管理
│   └── formulas.py          # 配方管理
│
├── config/                  # 配置模块
│   ├── config.py            # 主配置文件
│   ├── production.py        # 生产环境配置
│   └── env.example          # 环境变量示例
│
├── core/                    # 核心工具模块
│   ├── constants.py         # 常量定义
│   ├── extensions.py        # Flask 扩展初始化
│   ├── logger.py            # 日志系统
│   ├── utils.py             # 工具函数
│   └── validators.py        # 输入验证
│
├── scripts/                 # 数据库脚本
│   ├── create_tables.py     # 创建表结构
│   ├── seed_data.py         # 导入基础数据
│   ├── create_admin.py      # 创建管理员
│   └── check_ready.py       # 环境检查
│
├── templates/               # HTML 模板
├── tests/                   # 单元测试
├── logs/                    # 日志文件
├── sql/                     # SQL 脚本
└── docs/                    # 项目文档
    ├── API_GUIDE.md         # API 使用指南
    ├── CHANGELOG.md         # 变更日志
    ├── fixes/               # 修复记录
    ├── improvements/        # 改进记录
    └── reports/             # 最终报告
```

## 开发建议

### 1. 运行测试

```bash
pytest
```

### 2. 代码检查

```bash
pip install -r requirements-dev.txt
flake8 .
```

### 3. 查看日志

```bash
# 应用日志
tail -f logs/app.log

# 错误日志
tail -f logs/error.log
```

## 生产部署

**重要**: 不要在生产环境使用 Flask 内置服务器！

推荐使用 Gunicorn + Nginx:

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

详细部署指南: [docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md)

## 安全建议

1. ✅ 修改 `.env` 中的所有密钥为随机强密码
2. ✅ 生产环境设置 `FLASK_DEBUG=False`
3. ✅ 使用 HTTPS（配置 Nginx）
4. ✅ 定期更新依赖包
5. ✅ 定期备份数据库

## 需要帮助？

- 查看详细文档: [docs/](docs/)
- API 使用指南: [docs/API_GUIDE.md](docs/API_GUIDE.md)
- 问题修复记录: [docs/fixes/](docs/fixes/)
- 改进记录: [docs/improvements/](docs/improvements/)

---

**最后更新**: 2025-10-21
**版本**: v4.0 (前后端分离 + 代码库整理)

