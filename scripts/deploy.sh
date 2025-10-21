#!/bin/bash
# 生产环境部署脚本
# 使用方法: ./deploy.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "化学配方管理系统 - 生产环境部署"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}错误: 请不要使用root用户运行此脚本${NC}"
    exit 1
fi

# 1. 检查Python版本
echo -e "\n${YELLOW}[1/10] 检查Python版本...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.7.0"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}错误: 需要Python 3.7或更高版本，当前版本: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python版本: $python_version${NC}"

# 2. 检查必要的环境变量文件
echo -e "\n${YELLOW}[2/10] 检查环境配置...${NC}"
if [ ! -f ".env.production" ]; then
    echo -e "${RED}错误: 未找到 .env.production 文件${NC}"
    echo "请复制 env.production.example 并配置："
    echo "  cp env.production.example .env.production"
    exit 1
fi
echo -e "${GREEN}✓ .env.production 文件存在${NC}"

# 3. 创建虚拟环境
echo -e "\n${YELLOW}[3/10] 创建/更新虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境已创建${NC}"
else
    echo -e "${GREEN}✓ 虚拟环境已存在${NC}"
fi

# 4. 激活虚拟环境并安装依赖
echo -e "\n${YELLOW}[4/10] 安装依赖...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 5. 检查数据库连接
echo -e "\n${YELLOW}[5/10] 检查数据库连接...${NC}"
python3 <<EOF
import sys
try:
    from dotenv import load_dotenv
    load_dotenv('.env.production')
    import config_production as config
    import mysql.connector
    conn = mysql.connector.connect(**{k: v for k, v in config.DB_CONFIG.items() if k not in ['pool_name', 'pool_size', 'pool_reset_session']})
    conn.close()
    print("✓ 数据库连接成功")
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")
    sys.exit(1)
EOF
if [ $? -ne 0 ]; then
    exit 1
fi

# 6. 检查数据库表是否存在
echo -e "\n${YELLOW}[6/10] 检查数据库表...${NC}"
echo "如果是首次部署，请先运行: python create_tables.py"
echo "然后运行: python seed_data.py"
read -p "数据库表已创建？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}请先初始化数据库${NC}"
    exit 1
fi

# 7. 运行数据库优化（可选）
echo -e "\n${YELLOW}[7/10] 数据库性能优化...${NC}"
read -p "是否应用数据库索引优化？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD < database_indexes.sql
    echo -e "${GREEN}✓ 索引优化已应用${NC}"
else
    echo "跳过索引优化"
fi

# 8. 创建日志目录
echo -e "\n${YELLOW}[8/10] 创建日志目录...${NC}"
mkdir -p logs
chmod 755 logs
echo -e "${GREEN}✓ 日志目录已准备${NC}"

# 9. 运行测试（可选）
echo -e "\n${YELLOW}[9/10] 运行测试...${NC}"
read -p "是否运行测试套件？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install -r requirements-dev.txt
    pytest -v
    if [ $? -ne 0 ]; then
        echo -e "${RED}测试失败！请修复后再部署${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 所有测试通过${NC}"
else
    echo "跳过测试"
fi

# 10. 生成启动脚本
echo -e "\n${YELLOW}[10/10] 生成启动脚本...${NC}"
cat > start_production.sh <<'SCRIPT'
#!/bin/bash
# 生产环境启动脚本

source venv/bin/activate
export APP_CONFIG=config_production

# 使用gunicorn启动（推荐）
if command -v gunicorn &> /dev/null; then
    gunicorn -c gunicorn_config.py app:app
else
    echo "警告: gunicorn未安装，使用Flask内置服务器（不推荐用于生产环境）"
    python app.py
fi
SCRIPT

chmod +x start_production.sh
echo -e "${GREEN}✓ 启动脚本已创建: ./start_production.sh${NC}"

# 11. 创建gunicorn配置
cat > gunicorn_config.py <<'GUNICORN'
# Gunicorn配置文件
import multiprocessing
import os

# 绑定地址
bind = "127.0.0.1:5000"

# Worker进程数（CPU核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# Worker类（默认sync，可选：gevent, eventlet）
worker_class = "sync"

# 超时时间（秒）
timeout = 120

# 保持连接数
keepalive = 5

# 日志
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# 进程名称
proc_name = "formula_manager"

# Daemon模式（可选）
# daemon = True

# PID文件
pidfile = "logs/gunicorn.pid"
GUNICORN

echo -e "${GREEN}✓ Gunicorn配置已创建${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "下一步："
echo "  1. 安装gunicorn: pip install gunicorn"
echo "  2. 启动应用: ./start_production.sh"
echo "  3. 配置Nginx反向代理（见 DEPLOYMENT_CHECKLIST.md）"
echo "  4. 配置SSL证书"
echo "  5. 设置Systemd服务（可选）"
echo ""
echo "监控："
echo "  - 应用日志: tail -f logs/app.log"
echo "  - 错误日志: tail -f logs/error.log"
echo "  - Gunicorn日志: tail -f logs/gunicorn_access.log"
echo ""

