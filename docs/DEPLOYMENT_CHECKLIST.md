# 生产环境部署检查清单

在将应用部署到生产环境之前，请确保完成以下所有检查项。

## 🔒 安全性检查

### 环境配置
- [ ] 创建 `.env` 文件（不要复制 `env.example`，从头创建）
- [ ] 设置强随机的 `FLASK_SECRET_KEY`（至少32个字符）
  ```bash
  # 生成随机密钥的方法
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] 设置 `FLASK_DEBUG=False`
- [ ] 确认数据库密码已更改（不使用默认的 `root`）
- [ ] `.env` 文件已添加到 `.gitignore`

### 数据库安全
- [ ] 数据库用户使用最小权限原则
- [ ] 数据库不允许远程 root 登录
- [ ] 启用 MySQL 慢查询日志
- [ ] 配置定期数据库备份

### 应用安全
- [ ] 检查所有 SQL 查询使用参数化（无字符串拼接）
- [ ] 确认所有用户输入已验证
- [ ] Session cookie 设置已正确（HTTPS环境下自动启用 Secure）
- [ ] 配置防火墙规则（只开放必要端口）

## 🚀 性能优化

### 应用服务器
- [ ] 不使用 Flask 内置服务器，改用 Gunicorn 或 uWSGI
  ```bash
  # 示例：使用 Gunicorn
  gunicorn -w 4 -b 127.0.0.1:5000 --access-logfile logs/access.log app:app
  ```
- [ ] 配置 Nginx 作为反向代理
- [ ] 启用 Gzip 压缩
- [ ] 配置静态文件缓存

### 数据库优化
- [ ] 添加必要的索引
- [ ] 启用查询缓存
- [ ] 配置连接池（考虑引入 SQLAlchemy）
- [ ] 监控慢查询

## 📊 监控与日志

### 日志配置
- [ ] 确认 `logs/` 目录可写
- [ ] 配置日志轮转（已在代码中配置，最大10MB）
- [ ] 设置日志保留策略
- [ ] 考虑集中式日志管理（如 ELK Stack）

### 监控
- [ ] 设置应用健康检查端点
- [ ] 配置服务器监控（CPU、内存、磁盘）
- [ ] 配置应用性能监控（APM）
- [ ] 设置告警机制

## 🔐 HTTPS 配置

- [ ] 获取 SSL/TLS 证书（Let's Encrypt 免费）
- [ ] 配置 Nginx HTTPS
- [ ] 强制 HTTP 重定向到 HTTPS
- [ ] 验证 `SESSION_COOKIE_SECURE` 生效（自动）
- [ ] 配置 HSTS 头

## 🗄️ 数据库

### 初始化
- [ ] 运行 `create_tables.py` 创建表结构
- [ ] 运行 `seed_data.py` 导入初始数据
- [ ] 运行 `create_admin.py` 创建管理员账号
- [ ] 立即修改默认管理员密码

### 备份策略
- [ ] 配置自动每日备份
- [ ] 测试备份恢复流程
- [ ] 备份存储在异地
- [ ] 加密敏感备份

## 📦 依赖管理

- [ ] 所有依赖已安装 `pip install -r requirements.txt`
- [ ] Python 版本 >= 3.7
- [ ] MySQL 版本 >= 8.0
- [ ] 定期更新依赖（安全补丁）

## 🧪 测试

- [ ] 在类生产环境中完整测试
- [ ] 测试所有用户角色权限
- [ ] 测试数据导入导出功能
- [ ] 压力测试（可选）
- [ ] 安全扫描（可选，如 OWASP ZAP）

## 🔧 系统配置

### 操作系统
- [ ] 更新系统补丁
- [ ] 配置防火墙
- [ ] 禁用不必要的服务
- [ ] 配置时区（与数据库一致）

### 文件权限
- [ ] 应用文件所有者正确
- [ ] `.env` 文件权限 600（只有所有者可读写）
- [ ] 日志目录可写
- [ ] 静态文件可读

## 📝 文档

- [ ] 更新 README.md（如有环境特定配置）
- [ ] 记录服务器配置
- [ ] 记录部署流程
- [ ] 准备回滚方案

## ⚡ 启动前最后检查

### 环境变量检查脚本
```bash
# 检查必要的环境变量
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_DATABASE', 'FLASK_SECRET_KEY']
missing = [var for var in required if not os.getenv(var)]

if missing:
    print(f'❌ 缺少环境变量: {missing}')
    exit(1)
    
if os.getenv('FLASK_DEBUG', 'False').lower() == 'true':
    print('⚠️  警告: DEBUG 模式仍然开启！')
    exit(1)
    
if os.getenv('FLASK_SECRET_KEY') == 'dev-secret-key-change-in-production':
    print('❌ 密钥仍使用默认值！')
    exit(1)

print('✅ 环境变量检查通过')
"
```

### 启动检查
- [ ] 应用可以正常启动
- [ ] 数据库连接成功
- [ ] 可以正常登录
- [ ] 日志正常写入
- [ ] 所有页面可访问

## 🚨 应急预案

- [ ] 准备数据库回滚脚本
- [ ] 准备应用回滚方案
- [ ] 记录关键人员联系方式
- [ ] 准备故障排查文档

## 📞 上线后监控（前24小时）

- [ ] 监控错误日志
- [ ] 监控应用性能
- [ ] 监控数据库性能
- [ ] 监控服务器资源
- [ ] 收集用户反馈

---

## 推荐的 Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 推荐的 Systemd 服务配置

```ini
[Unit]
Description=Chemical Formula Management System
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --access-logfile logs/access.log app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

**完成以上所有检查项后，才可以部署到生产环境！**

