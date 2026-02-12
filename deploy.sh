#!/bin/bash

# PhotoPolymer Formulation Database - 一键部署脚本
# 使用方法: bash deploy.sh

set -e

echo "=========================================="
echo "PhotoPolymer 配方数据库 - 部署脚本"
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

# 1. 部署后端API
echo -e "${GREEN}[1/5] 部署后端API服务...${NC}"
sudo cp backend_fastapi/depoly/photopolymer-api.service /etc/systemd/system/
echo "✓ 后端服务文件已复制"

# 2. 部署前端nginx配置
echo -e "${GREEN}[2/5] 部署前端nginx配置...${NC}"
sudo cp frontend_vue3/depoly/photopolymer-frontend.conf /etc/nginx/sites-available/photopolymer
sudo ln -sf /etc/nginx/sites-available/photopolymer /etc/nginx/sites-enabled/photopolymer
echo "✓ Nginx配置已安装"

# 3. 测试nginx配置
echo -e "${GREEN}[3/5] 测试nginx配置...${NC}"
if sudo nginx -t; then
    echo "✓ Nginx配置测试通过"
else
    echo -e "${RED}✗ Nginx配置有误，请检查${NC}"
    exit 1
fi

# 4. 重新加载systemd和nginx
echo -e "${GREEN}[4/5] 重新加载服务...${NC}"
sudo systemctl daemon-reload
sudo systemctl reload nginx
echo "✓ 服务配置已重新加载"

# 5. 启动服务
echo -e "${GREEN}[5/5] 启动服务...${NC}"

# 启动后端
sudo systemctl start photopolymer-api
sudo systemctl enable photopolymer-api
echo "✓ 后端API服务已启动"

# 重启nginx
sudo systemctl restart nginx
echo "✓ Nginx已重启"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 部署完成！${NC}"
echo "=========================================="
echo ""
echo "📍 访问地址："
echo "  前端应用: http://localhost:8080"
echo "  后端API:  http://localhost:8000"
echo "  API文档:  http://localhost:8000/docs"
echo ""
echo "📊 查看服务状态："
echo "  后端: sudo systemctl status photopolymer-api"
echo "  前端: sudo systemctl status nginx"
echo ""
echo "📝 查看日志："
echo "  后端: sudo journalctl -u photopolymer-api -f"
echo "  前端: sudo tail -f /var/log/nginx/photopolymer-access.log"
echo ""
echo "💡 提示："
echo "  - 前端使用8080端口（避免需要root权限）"
echo "  - 首次访问请按 Ctrl+Shift+R 强制刷新浏览器缓存"
echo "  - 确保虚拟环境位于: ~/venv/database/"
echo ""

