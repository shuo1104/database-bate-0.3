#!/bin/bash

# PhotoPolymer 配方数据库 - 新服务器路径配置脚本
# 使用方法: bash setup_new_server.sh

set -e

echo "=========================================="
echo "PhotoPolymer 新服务器路径配置向导"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录作为项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}当前项目目录: $SCRIPT_DIR${NC}"
echo ""

# 当前配置（从现有文件中读取）
CURRENT_USER="xgs"
CURRENT_PATH="/home/xgs/workspace/database-bate-0.3"
CURRENT_VENV="/home/xgs/venv/database"

echo -e "${YELLOW}=== 当前配置 ===${NC}"
echo "用户名: $CURRENT_USER"
echo "项目路径: $CURRENT_PATH"
echo "虚拟环境: $CURRENT_VENV"
echo ""

# 询问是否需要修改
echo -e "${YELLOW}=== 新服务器配置 ===${NC}"
echo ""

# 获取新用户名
echo -e "${GREEN}请输入新服务器的用户名 [默认: $(whoami)]:${NC}"
read -r NEW_USER
NEW_USER=${NEW_USER:-$(whoami)}

# 获取新用户组
echo -e "${GREEN}请输入新服务器的用户组 [默认: $(id -gn)]:${NC}"
read -r NEW_GROUP
NEW_GROUP=${NEW_GROUP:-$(id -gn)}

# 获取新项目路径
echo -e "${GREEN}请输入新服务器的项目路径 [默认: $SCRIPT_DIR]:${NC}"
read -r NEW_PATH
NEW_PATH=${NEW_PATH:-$SCRIPT_DIR}

# 获取新虚拟环境路径
DEFAULT_VENV="$HOME/venv/database"
echo -e "${GREEN}请输入新服务器的虚拟环境路径 [默认: $DEFAULT_VENV]:${NC}"
read -r NEW_VENV
NEW_VENV=${NEW_VENV:-$DEFAULT_VENV}

# 获取后端端口
echo -e "${GREEN}请输入后端 API 端口 [默认: 8000]:${NC}"
read -r BACKEND_PORT
BACKEND_PORT=${BACKEND_PORT:-8000}

# 获取前端端口
echo -e "${GREEN}请输入前端 Nginx 端口 [默认: 8080]:${NC}"
read -r FRONTEND_PORT
FRONTEND_PORT=${FRONTEND_PORT:-8080}

echo ""
echo -e "${YELLOW}=== 配置确认 ===${NC}"
echo "用户名: $NEW_USER"
echo "用户组: $NEW_GROUP"
echo "项目路径: $NEW_PATH"
echo "虚拟环境: $NEW_VENV"
echo "后端端口: $BACKEND_PORT"
echo "前端端口: $FRONTEND_PORT"
echo ""

echo -e "${RED}是否确认修改配置文件? (yes/no):${NC}"
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "操作已取消"
    exit 0
fi

echo ""
echo -e "${GREEN}开始修改配置文件...${NC}"
echo ""

# 备份原始文件
echo -e "${YELLOW}[1/4] 备份原始配置文件...${NC}"
cp "$SCRIPT_DIR/backend_fastapi/deploy/photopolymer-api.service" \
   "$SCRIPT_DIR/backend_fastapi/deploy/photopolymer-api.service.backup.$(date +%Y%m%d_%H%M%S)"
cp "$SCRIPT_DIR/frontend_vue3/deploy/photopolymer-frontend.conf" \
   "$SCRIPT_DIR/frontend_vue3/deploy/photopolymer-frontend.conf.backup.$(date +%Y%m%d_%H%M%S)"
echo "✓ 备份完成"
echo ""

# 修改后端服务配置
echo -e "${YELLOW}[2/4] 修改后端服务配置...${NC}"
BACKEND_SERVICE="$SCRIPT_DIR/backend_fastapi/deploy/photopolymer-api.service"

sed -i "s|User=$CURRENT_USER|User=$NEW_USER|g" "$BACKEND_SERVICE"
sed -i "s|Group=$CURRENT_USER|Group=$NEW_GROUP|g" "$BACKEND_SERVICE"
sed -i "s|$CURRENT_PATH|$NEW_PATH|g" "$BACKEND_SERVICE"
sed -i "s|$CURRENT_VENV|$NEW_VENV|g" "$BACKEND_SERVICE"

echo "✓ 后端服务配置已更新"
echo "  文件: $BACKEND_SERVICE"
echo ""

# 修改前端 Nginx 配置
echo -e "${YELLOW}[3/4] 修改前端 Nginx 配置...${NC}"
NGINX_CONF="$SCRIPT_DIR/frontend_vue3/deploy/photopolymer-frontend.conf"

sed -i "s|$CURRENT_PATH|$NEW_PATH|g" "$NGINX_CONF"
sed -i "s|listen 8080;|listen $FRONTEND_PORT;|g" "$NGINX_CONF"
sed -i "s|http://localhost:8000;|http://localhost:$BACKEND_PORT;|g" "$NGINX_CONF"

echo "✓ 前端 Nginx 配置已更新"
echo "  文件: $NGINX_CONF"
echo ""

# 显示修改后的配置
echo -e "${YELLOW}[4/4] 验证配置...${NC}"
echo ""
echo -e "${BLUE}=== 后端服务配置 ===${NC}"
grep -E "^(User|Group|WorkingDirectory|Environment|ExecStart)=" "$BACKEND_SERVICE" || true
echo ""
echo -e "${BLUE}=== 前端 Nginx 配置 ===${NC}"
grep -E "^\s*(listen|root|proxy_pass)" "$NGINX_CONF" || true
echo ""

echo "=========================================="
echo -e "${GREEN}✅ 配置修改完成！${NC}"
echo "=========================================="
echo ""
echo -e "${YELLOW}下一步操作：${NC}"
echo ""
echo "1. 创建虚拟环境："
echo "   mkdir -p $(dirname $NEW_VENV)"
echo "   python3 -m venv $NEW_VENV"
echo "   source $NEW_VENV/bin/activate"
echo "   cd $NEW_PATH/backend_fastapi"
echo "   pip install -r requirements.txt"
echo ""
echo "2. 构建前端："
echo "   cd $NEW_PATH/frontend_vue3"
echo "   pnpm install"
echo "   pnpm build"
echo ""
echo "3. 配置数据库（如果需要）："
echo "   sudo -u postgres psql"
echo "   CREATE DATABASE photopolymer_formulation_db;"
echo "   CREATE USER photopolymer_admin WITH PASSWORD 'your_password';"
echo "   GRANT ALL PRIVILEGES ON DATABASE photopolymer_formulation_db TO photopolymer_admin;"
echo ""
echo "4. 部署服务："
echo "   cd $NEW_PATH"
echo "   bash update_configs.sh"
echo ""
echo "5. 查看备份文件："
echo "   ls -la $SCRIPT_DIR/backend_fastapi/deploy/*.backup.*"
echo "   ls -la $SCRIPT_DIR/frontend_vue3/deploy/*.backup.*"
echo ""
