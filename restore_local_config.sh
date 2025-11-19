#!/bin/bash
# 恢复所有配置文件到本地访问模式
# 使用方法: bash restore_local_config.sh

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "恢复本地访问配置"
echo "=========================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. 恢复后端配置
echo -e "${YELLOW}[1/3] 恢复后端配置...${NC}"
if [ -f "backend_fastapi/app/config/settings.py.backup" ]; then
    cp backend_fastapi/app/config/settings.py.backup backend_fastapi/app/config/settings.py
    echo -e "${GREEN}✓ 后端配置已恢复${NC}"
else
    echo -e "${RED}✗ 后端配置备份文件不存在${NC}"
    exit 1
fi

# 2. 恢复前端配置
echo -e "${YELLOW}[2/3] 恢复前端环境变量...${NC}"
if [ -f "frontend_vue3/.env.production.backup" ]; then
    cp frontend_vue3/.env.production.backup frontend_vue3/.env.production
    echo -e "${GREEN}✓ 前端环境变量已恢复${NC}"
else
    echo -e "${RED}✗ 前端配置备份文件不存在${NC}"
    exit 1
fi

# 3. 恢复 Nginx 配置
echo -e "${YELLOW}[3/3] 恢复 Nginx 配置...${NC}"
if [ -f "frontend_vue3/depoly/photopolymer-frontend.conf.backup" ]; then
    cp frontend_vue3/depoly/photopolymer-frontend.conf.backup frontend_vue3/depoly/photopolymer-frontend.conf
    echo -e "${GREEN}✓ Nginx 配置已恢复${NC}"
else
    echo -e "${RED}✗ Nginx 配置备份文件不存在${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 配置文件恢复完成！${NC}"
echo "=========================================="
echo ""
echo "接下来请手动执行以下命令完成恢复："
echo ""
echo -e "${YELLOW}1. 重新构建前端：${NC}"
echo "   cd frontend_vue3"
echo "   pnpm build"
echo ""
echo -e "${YELLOW}2. 更新 Nginx 配置：${NC}"
echo "   sudo cp frontend_vue3/depoly/photopolymer-frontend.conf /etc/nginx/sites-available/photopolymer"
echo "   sudo nginx -t"
echo "   sudo systemctl restart nginx"
echo ""
echo -e "${YELLOW}3. 重启后端服务：${NC}"
echo "   sudo systemctl restart photopolymer-api"
echo ""
echo -e "${YELLOW}4. 关闭防火墙端口（可选）：${NC}"
echo "   sudo ufw delete allow 8080/tcp"
echo "   sudo ufw delete allow 8000/tcp"
echo "   sudo ufw reload"
echo ""
echo -e "${YELLOW}5. 验证本地访问：${NC}"
echo "   curl http://localhost:8080"
echo "   curl http://localhost:8000/api/v1/health"
echo ""
echo "=========================================="
echo ""

# 询问是否立即执行后续步骤
read -p "是否立即重新构建前端并重启服务？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}开始重新构建前端...${NC}"
    cd frontend_vue3
    pnpm build
    cd ..
    
    echo ""
    echo -e "${YELLOW}更新 Nginx 配置...${NC}"
    sudo cp frontend_vue3/depoly/photopolymer-frontend.conf /etc/nginx/sites-available/photopolymer
    sudo nginx -t
    
    echo ""
    echo -e "${YELLOW}重启服务...${NC}"
    sudo systemctl restart nginx
    sudo systemctl restart photopolymer-api
    
    echo ""
    echo -e "${GREEN}✅ 所有操作完成！${NC}"
    echo ""
    echo "服务状态："
    sudo systemctl status nginx --no-pager -l
    sudo systemctl status photopolymer-api --no-pager -l
else
    echo ""
    echo "请手动执行上述命令完成恢复。"
fi

echo ""

