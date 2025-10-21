# 快速启动指南

## 🚀 5分钟快速上手

### 1. 克隆项目

```bash
git clone <repository>
cd data_base
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# Windows激活
venv\Scripts\activate

# Linux/Mac激活
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 复制环境变量模板
copy config\.env.example .env

# 编辑.env，配置数据库信息
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password
# DB_DATABASE=test_base
```

### 4. 初始化数据库

```bash
# 创建数据库表
python scripts/create_tables.py

# 导入初始数据
python scripts/seed_data.py

# 创建管理员账号（用户名:admin 密码:admin123）
python scripts/create_admin.py
```

### 5. 启动应用

```bash
# 开发模式
python app.py
```

### 6. 访问应用

- **Web界面**: http://localhost:5000
- **API文档**: http://localhost:5000/api/docs/swagger
- **默认登录**: 
  - 用户名: `admin`
  - 密码: `admin123`

---

## 📖 主要功能

### Web应用（传统界面）

1. **项目管理**: 创建、编辑化学配方项目
2. **原料管理**: 管理原材料信息
3. **填料管理**: 管理无机填料
4. **配方管理**: 查看和管理配方成分
5. **测试结果**: 记录和查看测试数据

### RESTful API（前后端分离）

1. **认证API**: JWT令牌登录
2. **项目API**: CRUD操作
3. **用户API**: 用户管理（管理员）
4. **Swagger文档**: 在线测试API

---

## 🔧 开发指南

### 运行测试

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行所有测试
pytest

# 查看覆盖率
pytest --cov=. --cov-report=html
```

### 代码质量检查

```bash
# 代码格式化
black .

# 代码检查
flake8 .

# 类型检查
mypy .
```

### API开发

```javascript
// 1. 登录获取令牌
const response = await fetch('http://localhost:5000/api/v1/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
    })
});

const { data } = await response.json();
const token = data.access_token;

// 2. 使用令牌访问API
const projects = await fetch('http://localhost:5000/api/v1/projects', {
    headers: {'Authorization': `Bearer ${token}`}
});
```

---

## 📁 项目结构

```
data_base/
├── app.py              # 主应用
├── api/                # API模块（JWT认证）
├── blueprints/         # Web路由
├── core/               # 核心工具（utils, validators）
├── config/             # 配置文件
├── scripts/            # 工具脚本
├── sql/                # SQL文件
├── docs/               # 文档（5450行）
├── templates/          # HTML模板
└── tests/              # 单元测试（42个）
```

详细结构：[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 📚 文档导航

### 必读文档

1. **README.md** - 项目完整文档
2. **PROJECT_STRUCTURE.md** - 项目结构说明
3. **docs/API_GUIDE.md** - API使用指南（700行）

### API开发

4. **Swagger UI** - http://localhost:5000/api/docs/swagger
5. **docs/API_GUIDE.md** - 包含React/Vue示例

### 部署

6. **docs/DEPLOYMENT_CHECKLIST.md** - 部署检查清单
7. **scripts/deploy.sh** - 自动化部署脚本

### 改进历史

8. **docs/CHANGELOG.md** - 详细更新日志
9. **docs/improvements/** - 四轮改进报告
10. **docs/reports/** - 最终总结报告

---

## ❓ 常见问题

### Q: 如何修改管理员密码？

A: 登录后访问个人资料页面修改

### Q: 如何添加新用户？

A: 管理员登录后，访问用户管理页面

### Q: 如何使用API？

A: 访问 http://localhost:5000/api/docs/swagger 在线测试

### Q: 数据库连接失败？

A: 检查 `.env` 文件中的数据库配置

### Q: 如何部署到生产环境？

A: 运行 `./scripts/deploy.sh`

---

## 🆘 获取帮助

### 文档

- [完整文档](README.md)
- [API文档](docs/API_GUIDE.md)
- [安全报告](docs/SECURITY_REPORT.md)

### 在线工具

- Swagger UI: http://localhost:5000/api/docs/swagger
- 诊断页面: http://localhost:5000/diagnostic

---

## 🎯 下一步

1. ✅ 启动应用
2. ✅ 登录管理后台
3. ✅ 创建第一个项目
4. ✅ 查看API文档
5. ✅ 尝试API调用

---

**版本**: 1.0  
**更新日期**: 2025-10-21

