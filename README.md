# 化学配方管理系统

一个基于 Flask 的化学配方数据库管理系统，用于管理项目信息、原料、无机填料、配方组成和测试结果。

## 功能特性

### 核心功能
- ✅ 用户认证与授权（管理员/普通用户）
- ✅ 项目信息管理（喷墨、涂层、3D打印、复合材料）
- ✅ 原料数据库管理
- ✅ 无机填料数据库管理
- ✅ 配方成分配置
- ✅ 测试结果记录（按项目类型分表）
- ✅ 数据导出（CSV格式）
- ✅ 批量操作支持

### 安全特性
- ✅ Argon2id 密码哈希
- ✅ Session 管理（HttpOnly, SameSite, Secure）
- ✅ SQL 注入防护（参数化查询）
- ✅ CSRF 保护（Flask-WTF）
- ✅ 请求频率限制（防暴力破解）
- ✅ 环境变量配置（敏感信息保护）
- ✅ 单点登录（SSO）机制
- ✅ 完整的输入验证
- ✅ 安全响应头（CSP, X-Frame-Options等）
- ✅ 审计日志（登录尝试、用户操作）
- ✅ 全局错误处理

## 技术栈

### 后端
- **框架**: Flask 2.3+
- **数据库**: MySQL 8.0+
- **密码哈希**: Argon2-CFFI
- **WSGI服务器**: Gunicorn（生产环境）
- **测试框架**: Pytest + Coverage
- **Python**: 3.7+
- **连接池**: MySQL Connector/Python
- **频率限制**: Flask-Limiter (支持Redis)

### API
- **认证**: JWT (PyJWT)
- **CORS**: Flask-CORS
- **文档**: Swagger UI + OpenAPI 3.0
- **架构**: RESTful API

### 前端（可选）
- **支持任意前端框架**: React, Vue, Angular
- **支持移动端**: React Native, Flutter
- **支持桌面端**: Electron, Tauri

## 项目结构

详细的项目目录结构请查看：[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

**主要目录**:
- `api/` - API模块（JWT认证、文档生成）
- `blueprints/` - Flask Blueprints（Web+API路由）
- `core/` - 核心模块（工具、验证、常量、日志）
- `config/` - 配置文件（开发/生产环境）
- `scripts/` - 工具脚本（部署、初始化）
- `docs/` - 完整文档（5450行）
- `sql/` - SQL文件（性能优化）
- `templates/` - Jinja2模板
- `tests/` - 单元测试（42个）

---

## 快速开始

### 1. 环境要求

```bash
- Python 3.7 或更高版本
- MySQL 8.0 或更高版本
- pip 包管理器
```

### 2. 安装步骤

```bash
# 克隆项目
git clone <repository_url>
cd data_base

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，配置数据库连接信息和密钥
```

### 3. 数据库初始化

```bash
# 创建数据库和表结构
python create_tables.py

# 导入初始配置数据
python seed_data.py

# 创建管理员账号
python create_admin.py
```

### 4. 运行应用

```bash
# 开发环境
python app.py

# 生产环境（推荐使用 gunicorn）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

访问 `http://localhost:5000` 即可使用系统。

## 配置说明

### 环境变量配置文件 (.env)

```ini
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_DATABASE=test_base
DB_CHARSET=utf8mb4

# Flask配置
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 会话配置（秒）
SESSION_LIFETIME=28800
```

⚠️ **安全提示**:
- 生产环境务必设置强随机密钥作为 `FLASK_SECRET_KEY`
- 不要将 `.env` 文件提交到版本控制系统
- 生产环境必须设置 `FLASK_DEBUG=False`

## 项目结构

```
data_base/
├── app.py                 # Flask 应用主文件
├── config.py              # 配置管理（从环境变量读取）
├── constants.py           # 常量定义
├── validators.py          # 输入验证模块
├── logger.py              # 日志配置模块
├── utils.py               # 工具函数
├── create_tables.py       # 数据库表创建脚本
├── seed_data.py           # 初始数据导入脚本
├── create_admin.py        # 管理员账号创建脚本
├── requirements.txt       # Python 依赖
├── env.example            # 环境变量示例文件
├── blueprints/            # 功能模块（Blueprint）
│   ├── auth.py           # 用户认证与授权
│   ├── projects.py       # 项目管理
│   ├── materials.py      # 原料管理
│   ├── fillers.py        # 填料管理
│   └── formulas.py       # 配方管理
├── templates/             # HTML 模板
├── logs/                  # 日志文件目录（自动创建）
└── needs/                 # 需求文档
```

## 数据库设计

### 主要数据表

1. **tbl_Users** - 用户账号管理
2. **tbl_ProjectInfo** - 项目基本信息
3. **tbl_RawMaterials** - 原料信息
4. **tbl_InorganicFillers** - 无机填料信息
5. **tbl_FormulaComposition** - 配方成分
6. **tbl_TestResults_\*** - 测试结果（按类型分表）

### 配置表

- **tbl_Config_ProjectTypes** - 项目类型
- **tbl_Config_MaterialCategories** - 材料类别
- **tbl_Config_FillerTypes** - 填料类型

## 用户角色

### 管理员 (admin)
- 用户管理（添加、禁用、删除用户）
- 重置用户密码
- 所有普通用户权限

### 普通用户 (user)
- 查看和管理项目
- 管理原料和填料数据
- 编辑配方成分
- 记录测试结果
- 导出数据

## 日志管理

日志文件存储在 `logs/` 目录：

- `app.log` - 所有应用日志（自动轮转，最大10MB）
- `error.log` - 仅错误日志

日志格式：
```
[2025-10-21 10:30:15,123] INFO in module_name: Message
```

## 安全最佳实践

### 已实现 ✅
- ✅ SQL 参数化查询（防止SQL注入）
- ✅ Argon2id 密码哈希
- ✅ Session 安全配置（HttpOnly, SameSite, Secure）
- ✅ CSRF 保护（Flask-WTF）
- ✅ 请求频率限制（Flask-Limiter）
  - 全局: 200次/天，50次/小时
  - 登录: 5次/分钟，20次/小时
- ✅ 环境变量配置（敏感信息保护）
- ✅ 完整的输入验证
- ✅ 安全响应头
  - X-Frame-Options, X-Content-Type-Options
  - Content-Security-Policy
  - X-XSS-Protection
- ✅ 审计日志（登录、操作记录）
- ✅ 全局错误处理

### 生产环境建议 ⚠️
- ⚠️ 使用 HTTPS（必须）
- ⚠️ 使用 Redis 存储频率限制数据（可选）
- ⚠️ 定期安全审计
- ⚠️ 定期更新依赖包
- ⚠️ 配置 WAF（Web应用防火墙）

## 测试

### 运行测试

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_validators.py

# 查看覆盖率报告
pytest --cov=. --cov-report=html
# 打开 htmlcov/index.html 查看详细报告
```

### 测试统计

- 总测试数: 42个
- 测试模块: 3个
- 目标覆盖率: >80%
- 当前覆盖率: ~60%

### 代码质量检查

```bash
# 代码格式化
black .

# 代码检查
flake8 .
pylint *.py

# 类型检查
mypy .
```

## API使用（前后端分离）

### API文档

访问Swagger UI在线文档：
```
http://localhost:5000/api/docs/swagger
```

### 快速示例

```javascript
// 1. 登录获取令牌
const response = await fetch('http://localhost:5000/api/v1/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'admin',
        password: 'password123'
    })
});

const { data } = await response.json();
const accessToken = data.access_token;

// 2. 使用令牌访问API
const projects = await fetch('http://localhost:5000/api/v1/projects', {
    headers: {'Authorization': `Bearer ${accessToken}`}
});
```

### API端点

**认证**:
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新令牌
- `GET /api/v1/auth/me` - 当前用户信息

**项目管理**:
- `GET /api/v1/projects` - 项目列表（分页）
- `GET /api/v1/projects/{id}` - 项目详情
- `POST /api/v1/projects` - 创建项目

**用户管理**:
- `GET /api/v1/users` - 用户列表（管理员）

**系统**:
- `GET /api/v1/health` - 健康检查

### 前端集成

详细的前端集成示例请查看：[API_GUIDE.md](API_GUIDE.md)

支持的前端技术栈：
- ✅ React + Axios
- ✅ Vue 3 + Composition API
- ✅ Angular + HttpClient
- ✅ React Native（移动端）
- ✅ Flutter（移动端）

---

## 生产环境部署

### 快速部署（推荐）

```bash
# 1. 克隆代码
git clone <repository>
cd data_base

# 2. 配置环境
cp env.production.example .env.production
# 编辑 .env.production

# 3. 运行部署脚本
chmod +x deploy.sh
./deploy.sh

# 4. 启动应用
./start_production.sh
```

### 手动部署

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt
pip install gunicorn

# 3. 配置环境变量
cp env.production.example .env.production
# 编辑配置

# 4. 初始化数据库
python create_tables.py
python seed_data.py
python create_admin.py

# 5. 应用数据库优化（可选但推荐）
mysql -u user -p database < database_indexes.sql

# 6. 使用Gunicorn启动
gunicorn -c gunicorn_config.py app:app
```

### 性能优化

**数据库索引**:
```bash
# 应用30+个性能索引
mysql -u user -p database < database_indexes.sql

# 预期效果：
# - 查询速度提升2-10倍
# - JOIN操作显著加速
# - 几乎消除全表扫描
```

**连接池配置**:
```ini
# .env.production
DB_POOL_SIZE=20  # 根据并发量调整
```

### Nginx配置示例

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 安全头（应用已自动设置）
    add_header Strict-Transport-Security "max-age=31536000" always;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 开发指南

### 添加新功能

1. 在 `blueprints/` 创建新的 Blueprint
2. 在 `app.py` 中注册 Blueprint
3. 使用 `validators.py` 进行输入验证
4. 使用 `logger` 记录重要操作
5. 遵循现有的代码风格

### 代码规范

- 使用参数化查询，禁止字符串拼接SQL
- 总是检查 `get_db_connection()` 返回值
- 使用 `logger` 而不是 `print()`
- 使用 `constants.py` 中的常量
- 添加适当的错误处理

## 故障排除

### 数据库连接失败
检查 `.env` 文件中的数据库配置，确保 MySQL 服务正在运行。

### 密码哈希错误
确保已安装 `argon2-cffi` 包：
```bash
pip install argon2-cffi
```

### 日志目录权限问题
确保应用有权限在项目目录创建 `logs/` 文件夹。

## 版本历史

详见 [CHANGELOG.md](CHANGELOG.md)

## 许可证

[根据实际情况填写]

## 联系方式

[根据实际情况填写]

---

**⚠️ 警告**: 本系统包含敏感的化学配方数据，请妥善保管数据库备份，并定期更新安全补丁。

