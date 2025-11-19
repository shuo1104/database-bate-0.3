#!/bin/bash

# PhotoPolymer 配方数据库 - 安装依赖并部署
# 使用方法: bash install_and_deploy.sh

set -e

echo "=========================================="
echo "PhotoPolymer 配方数据库 - 自动安装部署"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取脚本所在目录作为项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$SCRIPT_DIR"

# 切换到项目目录
echo -e "${YELLOW}项目目录: $BASE_DIR${NC}"
cd "$BASE_DIR"

# 1. 安装nginx
echo -e "${GREEN}[1/6] 检查并安装nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    echo "Nginx未安装，正在安装..."
    sudo apt update
    sudo apt install -y nginx
    echo "✓ Nginx安装完成"
else
    echo "✓ Nginx已安装"
fi

# 2. 创建nginx配置目录（如果不存在）
echo -e "${GREEN}[2/6] 配置nginx目录...${NC}"
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

# 确保nginx.conf包含sites-enabled
if ! grep -q "sites-enabled" /etc/nginx/nginx.conf; then
    echo "添加sites-enabled配置..."
    sudo sed -i '/http {/a\    include /etc/nginx/sites-enabled/*;' /etc/nginx/nginx.conf
fi
echo "✓ Nginx目录配置完成"

# 3. 部署后端API
echo -e "${GREEN}[3/6] 部署后端API服务...${NC}"
sudo cp backend_fastapi/depoly/photopolymer-api.service /etc/systemd/system/
echo "✓ 后端服务文件已复制"

# 4. 部署前端nginx配置
echo -e "${GREEN}[4/6] 部署前端nginx配置...${NC}"
sudo cp frontend_vue3/depoly/photopolymer-frontend.conf /etc/nginx/sites-available/photopolymer
sudo ln -sf /etc/nginx/sites-available/photopolymer /etc/nginx/sites-enabled/photopolymer

# 删除默认配置（如果存在）
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    sudo rm /etc/nginx/sites-enabled/default
    echo "✓ 已移除默认nginx配置"
fi
echo "✓ Nginx配置已安装"

# 5. 测试nginx配置
echo -e "${GREEN}[5/6] 测试nginx配置...${NC}"
if sudo nginx -t; then
    echo "✓ Nginx配置测试通过"
else
    echo -e "${RED}✗ Nginx配置有误，请检查${NC}"
    exit 1
fi

# 6. 启动服务
echo -e "${GREEN}[6/6] 启动服务...${NC}"

# 重新加载systemd
sudo systemctl daemon-reload

# 启动后端
sudo systemctl restart photopolymer-api
sudo systemctl enable photopolymer-api
echo "✓ 后端API服务已启动"

# 启动nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
echo "✓ Nginx已启动"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 安装部署完成！${NC}"
echo "=========================================="
echo ""
echo "服务状态："
echo "  后端API: http://localhost:8000"
echo "  前  端:  http://localhost"
echo ""
echo "查看服务状态："
echo "  后端: sudo systemctl status photopolymer-api"
echo "  前端: sudo systemctl status nginx"
echo ""
echo "查看日志："
echo "  后端: sudo journalctl -u photopolymer-api -f"
echo "  前端: sudo tail -f /var/log/nginx/photopolymer-access.log"
echo ""
echo "停止服务："
echo "  sudo systemctl stop photopolymer-api"
echo "  sudo systemctl stop nginx"
echo ""

