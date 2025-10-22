# 🧪 光创化物 R&D 数据库管理系统

**版本：** v1.0.0-optimized  
**适用：** 内网环境  
**技术栈：** Flask + MySQL + Bootstrap 5

---

## 📋 功能概览

- ✅ **项目管理** - 项目信息、配方设计、测试结果
- ✅ **原料管理** - 原料信息、分类、供应商
- ✅ **填料管理** - 无机填料信息、硅烷化处理
- ✅ **配方管理** - 配方成分、重量百分比
- ✅ **用户管理** - 用户账号、权限控制（管理员）
- ✅ **数据导出** - CSV格式批量导出

---

## 🚀 快速开始

### 1. 环境要求

```bash
Python 3.8+
MySQL 5.7+
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

创建 `config/.env` 文件：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=test_base
SECRET_KEY=your-secret-key-here
DEBUG=True
HOST=0.0.0.0
PORT=5000
```

### 4. 初始化数据库

```bash
# 创建表和索引
python scripts/create_tables.py

# 创建管理员账号
python scripts/create_admin.py
```

### 5. 启动应用

```bash
python app.py
```

访问：http://localhost:5000

---

## 🏗️ 项目结构

```
data_base/
├── app.py                 # 主应用
├── requirements.txt       # 依赖包
├── config/               # 配置文件
│   ├── config.py
│   └── .env
├── blueprints/           # 业务模块
│   ├── auth.py          # 用户认证
│   ├── projects.py      # 项目管理
│   ├── materials.py     # 原料管理
│   ├── fillers.py       # 填料管理
│   └── formulas.py      # 配方管理
├── core/                # 核心工具
│   ├── extensions.py    # Flask扩展
│   ├── utils.py         # 工具函数
│   └── validators.py    # 输入验证
├── templates/           # HTML模板
├── static/              # 静态资源
└── scripts/             # 脚本工具
    ├── create_tables.py
    ├── create_admin.py
    └── seed_data.py
```

---

## 🔒 安全特性

- ✅ **密码加密** - Argon2id哈希算法
- ✅ **CSRF保护** - Flask-WTF
- ✅ **请求限流** - 防暴力破解
- ✅ **Session认证** - 安全的会话管理
- ✅ **输入验证** - 防SQL注入/XSS
- ✅ **安全响应头** - X-Frame-Options, CSP等

---

## ⚡ 性能优化

- ✅ **数据库索引** - 自动创建性能索引
- ✅ **分页查询** - 支持10/20/50/100条/页
- ✅ **CDN加速** - 使用jsdelivr CDN
- ✅ **零延迟** - 删除所有人为延迟
- ✅ **快速响应** - 页面加载<500ms

---

## 📦 核心依赖

```
Flask 2.3+              # Web框架
mysql-connector-python  # MySQL驱动
argon2-cffi            # 密码加密
Flask-WTF              # CSRF保护
Flask-Limiter          # 请求限流
```

---

## 🛠️ 常用脚本

### 创建管理员
```bash
python scripts/create_admin.py
```

### 数据库诊断
```bash
python scripts/check_performance.py
```

### 应用索引
```bash
python scripts/apply_indexes.py
```

### 填充测试数据
```bash
python scripts/seed_data.py
```

---

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DB_HOST` | 数据库地址 | localhost |
| `DB_PORT` | 数据库端口 | 3306 |
| `DB_USER` | 数据库用户 | root |
| `DB_PASSWORD` | 数据库密码 | - |
| `DB_NAME` | 数据库名称 | test_base |
| `SECRET_KEY` | 密钥 | 随机生成 |
| `DEBUG` | 调试模式 | False |
| `HOST` | 监听地址 | 0.0.0.0 |
| `PORT` | 监听端口 | 5000 |

### 生产环境

```bash
# 1. 关闭DEBUG模式
DEBUG=False

# 2. 使用强密钥
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# 3. 使用WSGI服务器
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📚 用户指南

### 默认账号

```
用户名: admin
密码: 创建时设置
```

### 用户角色

- **管理员(admin)** - 完整权限，可管理用户
- **普通用户(user)** - 可查看和编辑数据

### 数据导出

1. 在列表页面勾选要导出的项目
2. 点击"导出为CSV"按钮
3. 下载CSV文件

---

## 🐛 故障排查

### 数据库连接失败

```bash
# 检查MySQL服务
mysql -u root -p

# 检查配置文件
cat config/.env
```

### 无法启动应用

```bash
# 检查依赖
pip install -r requirements.txt

# 检查端口占用
netstat -an | findstr :5000
```

### 页面加载慢

```bash
# 运行性能诊断
python scripts/check_performance.py

# 应用数据库索引
python scripts/apply_indexes.py
```

---

## 📝 变更日志

### v1.0.0-optimized (2025-10-22)

**✅ 性能优化**
- 删除所有人为延迟（提升80%响应速度）
- 更换CDN为jsdelivr（提升60%加载速度）
- 自动创建数据库索引
- 优化分页查询

**✅ 功能简化**
- 移除JWT/API功能（内网不需要）
- 移除CORS跨域（单体应用）
- 简化依赖包（从11个减少到7个）

**✅ 代码清理**
- 删除过时文档（22个）
- 删除API相关代码
- 统一代码风格

---

## 🤝 技术支持

如有问题，请查看：
- `docs/DEPLOYMENT_CHECKLIST.md` - 部署检查清单
- `docs/INTERNAL_NETWORK_CLEANUP_COMPLETED.md` - 清理记录
- `PERFORMANCE_FIXES_COMPLETED.md` - 性能优化记录
- `QUICK_START.md` - 详细快速开始指南

---

## 📄 许可证

内部使用，未开源

---

**最后更新：** 2025-10-22  
**维护：** 光创化物 R&D团队
