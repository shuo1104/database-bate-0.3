# 启动应用前的准备工作清单

## ✅ 完整准备步骤

### 步骤1: 安装Python依赖 📦

```bash
# 确保在项目根目录
cd d:\WorkSpace\workspace\data_base

# 安装所有依赖（12个包）
pip install -r requirements.txt
```

**依赖列表**:
- Flask>=2.3.0
- mysql-connector-python>=8.0.33
- argon2-cffi>=23.1.0
- Werkzeug>=2.3.0
- python-dotenv>=1.0.0
- Flask-WTF>=1.1.0
- Flask-Limiter>=3.5.0
- Flask-CORS>=4.0.0
- PyJWT>=2.8.0
- flask-swagger-ui>=4.11.1
- apispec>=6.3.0
- marshmallow>=3.20.0

---

### 步骤2: 配置环境变量 ⚙️

```bash
# 复制环境变量模板
copy config\.env.example .env

# 或者在项目根目录创建 .env 文件
```

**编辑 `.env` 文件，配置以下内容**:

```ini
# Flask配置
FLASK_SECRET_KEY=your-super-secret-key-change-this
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Session配置
SESSION_LIFETIME=28800

# 数据库配置（重要！）
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_DATABASE=test_base
DB_CHARSET=utf8mb4

# CORS配置
CORS_ENABLED=True
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

**⚠️ 必须修改的配置**:
- `DB_PASSWORD` - 你的MySQL密码
- `FLASK_SECRET_KEY` - 生成一个随机密钥

**生成随机密钥**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 步骤3: 启动MySQL数据库 🗄️

确保MySQL服务正在运行：

```bash
# Windows
net start MySQL80

# 或者通过服务管理器启动
services.msc
```

**验证MySQL连接**:
```bash
mysql -u root -p
# 输入密码
# 如果能连接，说明MySQL正常
```

---

### 步骤4: 创建数据库和表 🏗️

```bash
# 创建数据库和所有表
python scripts\create_tables.py
```

**预期输出**:
```
[INFO] 开始创建数据库和表...
[INFO] 数据库 'test_base' 已创建
[INFO] 表 'tbl_Users' 已创建
[INFO] 表 'tbl_ProjectInfo' 已创建
...
[INFO] 所有表创建完成！
```

---

### 步骤5: 导入初始配置数据 📥

```bash
# 导入项目类型、原料类别等配置数据
python scripts\seed_data.py
```

**预期输出**:
```
[INFO] 开始导入配置数据...
[INFO] 项目类型数据已导入
[INFO] 原料类别数据已导入
[INFO] 填料类型数据已导入
[INFO] 配置数据导入完成！
```

---

### 步骤6: 创建管理员账号 👤

```bash
# 创建默认管理员账号
python scripts\create_admin.py
```

**默认管理员信息**:
- 用户名: `admin`
- 密码: `admin123`
- 角色: 管理员

**⚠️ 重要提示**: 首次登录后请立即修改密码！

---

### 步骤7: （可选）应用数据库索引优化 ⚡

```bash
# 在MySQL中执行索引优化SQL
mysql -u root -p test_base < sql\database_indexes.sql
```

这会创建30+个索引，提升查询性能2-10倍。

---

### 步骤8: 启动应用 🚀

```bash
python app.py
```

**预期输出**:
```
[INFO] 日志系统配置完成。
[INFO] CSRF 保护已启用
[INFO] CORS 已启用 - 允许的源: [...]
[INFO] 请求频率限制已启用
[INFO] 所有 Blueprints 已注册（包括 API v1）
[INFO] 启动应用服务器 - Host: 0.0.0.0, Port: 5000, Debug: True
 * Running on http://0.0.0.0:5000
```

---

## 🧪 验证清单

启动成功后，访问以下URL验证：

| 功能 | URL | 预期结果 |
|------|-----|----------|
| 首页 | http://localhost:5000 | 重定向到登录页 |
| 登录 | http://localhost:5000/login | 显示登录表单 |
| 诊断 | http://localhost:5000/diagnostic | 显示系统信息 |
| API文档 | http://localhost:5000/api/docs/swagger | Swagger UI界面 |
| API健康 | http://localhost:5000/api/v1/health | 返回JSON |

---

## ⚠️ 常见问题排查

### 问题1: ModuleNotFoundError

**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
pip install -r requirements.txt
```

---

### 问题2: 数据库连接失败

**错误**: `数据库连接失败: Access denied for user`

**解决**:
1. 检查 `.env` 文件中的数据库配置
2. 确认MySQL服务正在运行
3. 验证用户名和密码正确

---

### 问题3: 表已存在

**错误**: `Table 'xxx' already exists`

**解决**:
这是正常的警告，可以忽略。或者删除数据库重新创建：

```sql
DROP DATABASE IF EXISTS test_base;
```

然后重新运行 `python scripts\create_tables.py`

---

### 问题4: CSRF token缺失

**错误**: `CSRF验证失败: The CSRF token is missing`

**解决**: 已修复！所有表单都已添加CSRF token。

---

### 问题5: 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# Windows - 查找占用5000端口的进程
netstat -ano | findstr :5000

# 结束进程（PID是上面查到的进程ID）
taskkill /PID <PID> /F

# 或者在.env中修改端口
FLASK_PORT=5001
```

---

## 📋 快速检查脚本

使用自动检查脚本：

```bash
python CHECK_READY.py
```

这会检查：
- ✅ Python版本
- ✅ 依赖安装情况
- ✅ 环境变量配置
- ✅ MySQL连接
- ✅ 数据库表
- ✅ 管理员账号

---

## 🎯 完整命令序列（首次部署）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 创建并配置 .env
copy config\.env.example .env
notepad .env  # 编辑配置

# 3. 初始化数据库
python scripts\create_tables.py
python scripts\seed_data.py
python scripts\create_admin.py

# 4. （可选）应用索引优化
mysql -u root -p test_base < sql\database_indexes.sql

# 5. 启动应用
python app.py
```

**预计耗时**: 5-10分钟

---

## ✅ 成功标志

当你看到以下输出，说明一切正常：

```
[INFO] 启动应用服务器 - Host: 0.0.0.0, Port: 5000, Debug: True
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

然后访问 http://localhost:5000 应该能看到登录页面！

---

**创建日期**: 2025-10-21  
**适用版本**: v1.0

