# PhotoPolymer 数据库系统 - 部署步骤（适配新服务器）

---

## 准备工作：克隆代码

```bash
# 1. 进入工作目录（根据实际情况修改路径）
cd /home/xgs/workspace

# 2. 克隆代码
git clone https://github.com/shuo1104/database-bate-0.3.git
cd database-bate-0.3
```

**📝 记录您的项目路径**：例如 `/home/xgs/workspace/database-bate-0.3`

---

## 第一部分：安装依赖

### 1. 安装系统依赖

```bash
# 更新包列表
sudo apt update

# 安装 PostgreSQL 数据库
sudo apt install postgresql postgresql-contrib -y

# 安装 Nginx
sudo apt install nginx -y

# 安装 Python 虚拟环境工具
sudo apt install python3-venv python3-pip -y

# 安装 Node.js 和 pnpm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
npm install -g pnpm
```

### 2. 创建 Python 虚拟环境

```bash
# 创建虚拟环境目录
mkdir -p ~/venv

# 创建虚拟环境
python3 -m venv ~/venv/database

# 激活虚拟环境
source ~/venv/database/bin/activate

# 安装后端依赖（⚠️ 注意：路径中没有 data_base 目录）
cd ~/workspace/database-bate-0.3/backend_fastapi
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd ~/workspace/database-bate-0.3/frontend_vue3
pnpm install
```

---

## 第二部分：配置路径（⭐ 新服务器必须执行）

### 方法 1: 自动配置（推荐）

```bash
# 返回项目根目录
cd ~/workspace/database-bate-0.3

# 运行自动配置脚本
bash setup_new_server.sh
```

脚本会交互式询问：
- 用户名（默认：当前用户）
- 用户组（默认：当前用户组）
- 项目路径（默认：当前目录）
- 虚拟环境路径（默认：~/venv/database）
- 后端端口（默认：8000）
- 前端端口（默认：8080）

### 方法 2: 手动配置

如果您的服务器环境与默认不同，需要手动修改配置文件中的路径。

**需要修改的文件**：
1. `backend_fastapi/depoly/photopolymer-api.service` - 6处路径
2. `frontend_vue3/depoly/photopolymer-frontend.conf` - 2处路径

详见：`doc/新服务器部署路径修改清单.md`

---

## 第三部分：配置数据库

### 1. 启动 PostgreSQL

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. 创建数据库和用户

```bash
# 切换到 postgres 用户
sudo -u postgres psql
```

在 psql 中执行以下命令：

```sql
CREATE DATABASE photopolymer_formulation_db;
CREATE USER photopolymer_admin WITH PASSWORD 'root';
GRANT ALL PRIVILEGES ON DATABASE photopolymer_formulation_db TO photopolymer_admin;
\q
```

**⚠️ 生产环境安全提示**：请将 `'root'` 替换为强密码！

---

## 第四部分：构建前端

```bash
cd ~/workspace/database-bate-0.3/frontend_vue3
pnpm build
```

验证构建成功：
```bash
ls -la dist/  # 应该看到 index.html 等文件
```

---

## 第五部分：部署服务

### 使用一键部署脚本（推荐）

```bash
cd ~/workspace/database-bate-0.3
bash update_configs.sh
```

脚本会自动完成：
1. ✅ 停止现有服务
2. ✅ 复制后端服务配置到 `/etc/systemd/system/`
3. ✅ 复制前端 Nginx 配置到 `/etc/nginx/sites-available/`
4. ✅ 测试 Nginx 配置
5. ✅ 重新加载 systemd
6. ✅ 启动所有服务
7. ✅ 显示服务状态和端口监听情况

---

## 第六部分：验证部署

### 1. 检查所有服务状态

```bash
# 检查数据库
systemctl status postgresql

# 检查后端
systemctl status photopolymer-api.service

# 检查 Nginx
systemctl status nginx
```

所有服务应该显示 `active (running)` 状态。

### 2. 检查端口

```bash
# 检查后端端口 8000
sudo lsof -i :8000

# 检查 Nginx 端口 8080
sudo lsof -i :8080

# 检查数据库端口 5432
sudo lsof -i :5432
```

### 3. 查看日志

```bash
# 后端日志
sudo journalctl -u photopolymer-api.service -f

# Nginx 访问日志
sudo tail -f /var/log/nginx/photopolymer-access.log

# Nginx 错误日志
sudo tail -f /var/log/nginx/photopolymer-error.log
```

### 4. 访问系统

打开浏览器访问：
- **前端应用**：`http://YOUR_SERVER_IP:8080`
- **后端文档**：`http://YOUR_SERVER_IP:8000/docs`

---

## 第七部分：防火墙配置（如果需要）

```bash
# 允许 8080 端口
sudo ufw allow 8080/tcp

# 允许 SSH（重要！避免被锁定）
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

---

## 故障排查

### 如果后端启动失败

```bash
# 查看详细日志
sudo journalctl -u photopolymer-api.service -n 100 --no-pager

# 常见错误及解决方案：
# ❌ "CHDIR failed: No such file or directory"
#    → 路径配置错误，重新运行 setup_new_server.sh

# ❌ "ModuleNotFoundError"
#    → Python 依赖未安装，重新运行 pip install -r requirements.txt

# ❌ "Database connection failed"
#    → 检查数据库是否创建，用户名密码是否正确

# 手动测试启动
source ~/venv/database/bin/activate
cd ~/workspace/database-bate-0.3/backend_fastapi
python main.py --env=prod
```

### 如果 Nginx 启动失败

```bash
# 测试配置
sudo nginx -t

# 常见错误及解决方案：
# ❌ "No such file or directory" (dist 目录)
#    → 前端未构建，运行 pnpm build

# ❌ "Permission denied"
#    → 权限问题，运行：chmod -R 755 ~/workspace/database-bate-0.3/frontend_vue3/dist

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### 如果数据库连接失败

```bash
# 检查 PostgreSQL 状态
systemctl status postgresql

# 测试连接
psql -U photopolymer_admin -d photopolymer_formulation_db -h localhost
```

---

## 完整启动顺序

```bash
# 1. 启动数据库
sudo systemctl start postgresql

# 2. 启动后端
sudo systemctl start photopolymer-api.service

# 3. 启动 Nginx
sudo systemctl start nginx

# 4. 检查所有服务
systemctl status postgresql photopolymer-api.service nginx
```

---

## 停止所有服务

```bash
# 使用停止脚本
bash stop_system.sh

# 或手动停止
sudo systemctl stop photopolymer-api.service
sudo systemctl stop nginx
```

---

## 📚 相关文档

- **完整部署指南**：`doc/完整部署指南.md`
- **新服务器路径修改**：`doc/新服务器部署路径修改清单.md`
- **快速参考**：`新服务器部署快速参考.md`
- **路径配置说明**：`doc/路径配置说明.md`
- **路径修改总结**：`PATH_CHANGES_SUMMARY.md`

---

**部署完成！** 🎉

