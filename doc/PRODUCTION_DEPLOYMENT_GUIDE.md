# 🚀 生产环境部署指南

本文档详细说明将系统从开发环境迁移到生产环境所需的配置更改和注意事项。

---

## 📋 目录

- [必须修改的配置](#必须修改的配置)
- [推荐修改的配置](#推荐修改的配置)
- [数据库配置](#数据库配置)
- [安全加固](#安全加固)
- [性能优化](#性能优化)
- [部署检查清单](#部署检查清单)

---

## ⚠️ 必须修改的配置

### 1. 环境配置文件

创建生产环境配置文件：`env/.env.prod`

```env
# ==================== 环境标识 ====================
ENVIRONMENT=prod

# ==================== 服务器配置 ====================
# 🔴 关闭热重载，启用多进程
RELOAD=false
WORKERS=4  # 根据 CPU 核心数调整：核心数 × 2 + 1

# ==================== API 文档配置 ====================
# 🔴 关闭调试模式（必须！）
DEBUG=false

# 🔴 禁用或隐藏 API 文档（强烈建议）
# 选项1：完全禁用
DOCS_URL=
REDOC_URL=

# 选项2：使用隐藏路径（仅内部访问）
# DOCS_URL=/internal-docs-9527
# REDOC_URL=/internal-redoc-9527

# ==================== JWT 安全配置 ====================
# 🔴 使用强密钥（必须！至少 32 字符）
SECRET_KEY=your-very-strong-secret-key-min-32-chars-change-this-in-production-abc123

# 🔴 缩短 Token 有效期（推荐）
ACCESS_TOKEN_EXPIRE_MINUTES=60    # 1小时（开发环境为1天）
REFRESH_TOKEN_EXPIRE_MINUTES=10080  # 7天

# ==================== 数据库配置 ====================
# 🔴 使用生产数据库
DB_HOST=your-production-db-host
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your-strong-db-password
DB_DATABASE=photopolymer_prod_db

# 🔴 关闭 SQL 日志
DATABASE_ECHO=false

# ==================== CORS 配置 ====================
# 🔴 限制允许的来源（不要使用 *）
ALLOW_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# ==================== 日志配置 ====================
# 🔴 设置合适的日志级别
LOG_LEVEL=WARNING  # 生产环境使用 WARNING 或 ERROR
LOG_BACKUP_COUNT=30  # 保留 30 天日志
```

---

## 🔐 安全加固

### 1. JWT 密钥生成

**生成强密钥（必须）：**

```python
# 方法1：使用 Python
import secrets
print(secrets.token_urlsafe(32))

# 方法2：使用 OpenSSL
openssl rand -base64 32
```

**在 `env/.env.prod` 中设置：**
```env
SECRET_KEY=生成的强密钥
```

### 2. 默认管理员账号

**🔴 首次登录后立即修改默认密码！**

```
默认账号：admin
默认密码：admin123  ⚠️ 必须修改！
```

**修改步骤：**
1. 登录系统
2. 进入个人中心
3. 修改密码为强密码（至少 12 位，包含大小写字母、数字、特殊字符）

### 3. 数据库安全

```env
# ✅ 使用强密码
DB_PASSWORD=Strong_Db_P@ssw0rd_2024!

# ✅ 限制数据库访问 IP
# 在 PostgreSQL 配置 pg_hba.conf 中限制
```

### 4. CORS 配置

**开发环境（❌ 不安全）：**
```python
ALLOW_ORIGINS: List[str] = ["*"]  # 允许所有来源
```

**生产环境（✅ 安全）：**
```python
ALLOW_ORIGINS: List[str] = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
ALLOW_CREDENTIALS: bool = True
```

---

## 🎯 推荐修改的配置

### 1. API 文档配置

**开发环境：**
```python
TITLE: str = "Advanced - PhotoPolymer Formulation Management API"
VERSION: str = "1.0.0"
DESCRIPTION: str = "高级光敏聚合物配方管理数据库 RESTful API"
DOCS_URL: str = "/docs"
REDOC_URL: str = "/redoc"
DEBUG: bool = True
```

**生产环境：**
```python
TITLE: str = "PhotoPolymer Management API"
VERSION: str = "1.0.0"
DESCRIPTION: str = "Production API for Formulation Management"
DOCS_URL: str = None  # 或隐藏路径
REDOC_URL: str = None
DEBUG: bool = False  # 🔴 必须 False
```

### 2. 日志配置

```python
# 生产环境建议
LOG_LEVEL: str = "WARNING"  # 只记录警告和错误
LOG_BACKUP_COUNT: int = 30  # 保留 30 天
```

### 3. 数据库连接池

```python
# 生产环境优化
POOL_SIZE: int = 20       # 根据并发量调整
MAX_OVERFLOW: int = 10    # 最大溢出连接
POOL_TIMEOUT: int = 30    # 连接超时
POOL_RECYCLE: int = 1800  # 30分钟回收连接
```

---

## 💾 数据库配置

### 1. 创建生产数据库

```sql
-- 创建数据库
CREATE DATABASE photopolymer_prod_db
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';

-- 创建专用用户
CREATE USER photopolymer_user WITH ENCRYPTED PASSWORD 'your-strong-password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE photopolymer_prod_db TO photopolymer_user;
```

### 2. 初始化数据库表

```bash
# 设置生产环境
export ENVIRONMENT=prod  # Linux/Mac
set ENVIRONMENT=prod     # Windows

# 运行初始化脚本
cd backend_fastapi
python scripts/create_tables.py
```

### 3. 数据备份策略

**设置定时备份（Linux）：**

```bash
# 创建备份脚本：backup_db.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
pg_dump -U photopolymer_user -h localhost photopolymer_prod_db > "$BACKUP_DIR/backup_$DATE.sql"

# 删除 30 天前的备份
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

**添加到 crontab：**
```bash
# 每天凌晨 2 点备份
0 2 * * * /path/to/backup_db.sh
```

---

## ⚡ 性能优化

### 1. Uvicorn Workers 配置

**CPU 核心数推荐：**

| CPU 核心 | 推荐 WORKERS |
|----------|--------------|
| 2 核     | 5            |
| 4 核     | 9            |
| 8 核     | 17           |

**公式：** `WORKERS = CPU 核心数 × 2 + 1`

```env
# .env.prod
WORKERS=9  # 4 核服务器
```

### 2. 使用进程管理器

**推荐使用 Supervisor 或 Systemd：**

**Systemd 配置示例：** `/etc/systemd/system/photopolymer.service`

```ini
[Unit]
Description=PhotoPolymer API Service
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend_fastapi
Environment="ENVIRONMENT=prod"
ExecStart=/path/to/backend_fastapi/env/bin/python main.py run --env=prod
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**启动服务：**
```bash
sudo systemctl daemon-reload
sudo systemctl enable photopolymer
sudo systemctl start photopolymer
sudo systemctl status photopolymer
```

### 3. 使用 Nginx 反向代理

**Nginx 配置示例：** `/etc/nginx/sites-available/photopolymer`

```nginx
upstream photopolymer_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 强制 HTTPS（推荐）
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书配置
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 日志
    access_log /var/log/nginx/photopolymer_access.log;
    error_log /var/log/nginx/photopolymer_error.log;

    # 客户端最大请求体大小
    client_max_body_size 10M;

    # API 代理
    location /api/ {
        proxy_pass http://photopolymer_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态文件
    location /static/ {
        alias /path/to/backend_fastapi/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 前端
    location / {
        root /path/to/frontend_vue3/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 🌐 前端部署配置

### 1. 构建生产版本

**创建 `.env.production`：**

```env
VITE_APP_BASE_API=/api
VITE_API_BASE_URL=https://yourdomain.com
VITE_APP_TITLE=PhotoPolymer 配方管理系统
```

**构建：**
```bash
cd frontend_vue3
pnpm build
# 构建产物在 dist/ 目录
```

### 2. 部署到 Nginx

```bash
# 复制构建文件
cp -r dist/* /path/to/nginx/html/
```

---

## ✅ 部署检查清单

### 配置检查

- [ ] ✅ 创建 `env/.env.prod` 文件
- [ ] ✅ 设置 `DEBUG=false`
- [ ] ✅ 设置 `RELOAD=false`
- [ ] ✅ 设置 `WORKERS=4+`
- [ ] ✅ 生成并设置强 `SECRET_KEY`（32+ 字符）
- [ ] ✅ 禁用或隐藏 API 文档（`DOCS_URL`, `REDOC_URL`）
- [ ] ✅ 配置生产数据库连接
- [ ] ✅ 限制 CORS 允许的来源
- [ ] ✅ 设置 `LOG_LEVEL=WARNING` 或 `ERROR`

### 安全检查

- [ ] ✅ 修改默认管理员密码
- [ ] ✅ 数据库使用强密码
- [ ] ✅ 启用 HTTPS（SSL/TLS 证书）
- [ ] ✅ 配置防火墙规则
- [ ] ✅ 限制数据库访问 IP
- [ ] ✅ 定期更新依赖包

### 数据库检查

- [ ] ✅ 创建生产数据库
- [ ] ✅ 运行数据库初始化脚本
- [ ] ✅ 测试数据库连接
- [ ] ✅ 设置数据库备份策略
- [ ] ✅ 验证数据库用户权限

### 性能检查

- [ ] ✅ 配置 Uvicorn Workers
- [ ] ✅ 配置 Nginx 反向代理
- [ ] ✅ 启用 Gzip 压缩
- [ ] ✅ 配置静态文件缓存
- [ ] ✅ 配置数据库连接池

### 监控和日志

- [ ] ✅ 配置日志轮转
- [ ] ✅ 设置日志保留天数
- [ ] ✅ 配置进程管理器（Systemd/Supervisor）
- [ ] ✅ 设置服务自动重启
- [ ] ✅ 配置监控告警（可选）

### 部署测试

- [ ] ✅ 测试用户登录
- [ ] ✅ 测试 API 接口
- [ ] ✅ 测试文件上传
- [ ] ✅ 测试数据导出
- [ ] ✅ 压力测试（可选）

---

## 🚀 快速部署命令

```bash
# 1. 克隆项目
git clone <repository-url>
cd data_base

# 2. 后端部署
cd backend_fastapi
python -m venv env
source env/bin/activate  # Linux/Mac
# .\env\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. 配置环境
cp env/.env.example env/.env.prod
# 编辑 env/.env.prod，修改必要配置

# 4. 初始化数据库
export ENVIRONMENT=prod
python scripts/create_tables.py

# 5. 启动服务（使用 Systemd）
sudo systemctl start photopolymer

# 6. 前端部署
cd ../frontend_vue3
pnpm install
pnpm build
sudo cp -r dist/* /var/www/html/

# 7. 配置 Nginx
sudo ln -s /etc/nginx/sites-available/photopolymer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📞 故障排查

### 服务无法启动

```bash
# 查看服务状态
sudo systemctl status photopolymer

# 查看日志
sudo journalctl -u photopolymer -f

# 查看应用日志
tail -f backend_fastapi/logs/error.log
```

### 数据库连接失败

```bash
# 测试数据库连接
psql -h localhost -U photopolymer_user -d photopolymer_prod_db

# 检查 PostgreSQL 服务
sudo systemctl status postgresql
```

### API 响应 502

```bash
# 检查后端服务是否运行
curl http://localhost:8000/api/v1/auth/login

# 检查 Nginx 配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

---

## 📊 性能监控

### 推荐工具

- **应用监控**：Prometheus + Grafana
- **日志分析**：ELK Stack (Elasticsearch, Logstash, Kibana)
- **APM**：New Relic / Datadog
- **错误追踪**：Sentry

---

## 📝 版本更新流程

```bash
# 1. 拉取最新代码
git pull origin master

# 2. 更新后端依赖
cd backend_fastapi
source env/bin/activate
pip install -r requirements.txt

# 3. 运行数据库迁移（如有）
# python scripts/migrate.py

# 4. 重启服务
sudo systemctl restart photopolymer

# 5. 更新前端
cd ../frontend_vue3
pnpm install
pnpm build
sudo cp -r dist/* /var/www/html/

# 6. 清除 Nginx 缓存
sudo systemctl reload nginx
```

---

## 🔗 相关文档

- [后端 README](./README.md)
- [前端 README](../frontend_vue3/README.md)
- [数据生成说明](./scripts/DATA_GENERATION_README.md)
- [端口配置指南](../PORT_CONFIGURATION_GUIDE.md)

---

**最后更新**：2025年10月30日  
**文档版本**：1.0.0

