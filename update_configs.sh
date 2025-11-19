#!/bin/bash

# PhotoPolymer 配方数据库 - 配置文件更新脚本
# 使用方法: bash update_configs.sh

set -e

echo "=========================================="
echo "PhotoPolymer 配置文件更新脚本"
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

echo -e "${YELLOW}项目目录: $BASE_DIR${NC}"
echo ""

# 1. 停止现有服务
echo -e "${GREEN}[1/6] 停止现有服务...${NC}"
sudo systemctl stop photopolymer-api.service 2>/dev/null || echo "后端服务未运行"
echo "✓ 服务已停止"
echo ""

# 2. 更新后端 systemd 服务配置
echo -e "${GREEN}[2/6] 更新后端 systemd 服务配置...${NC}"
sudo cp "$BASE_DIR/backend_fastapi/depoly/photopolymer-api.service" /etc/systemd/system/
echo "✓ 后端服务配置已更新"
echo "  源文件: $BASE_DIR/backend_fastapi/depoly/photopolymer-api.service"
echo "  目标位置: /etc/systemd/system/photopolymer-api.service"
echo ""

# 3. 更新前端 Nginx 配置
echo -e "${GREEN}[3/6] 更新前端 Nginx 配置...${NC}"
sudo cp "$BASE_DIR/frontend_vue3/depoly/photopolymer-frontend.conf" /etc/nginx/sites-available/photopolymer
sudo ln -sf /etc/nginx/sites-available/photopolymer /etc/nginx/sites-enabled/photopolymer
echo "✓ Nginx 配置已更新"
echo "  源文件: $BASE_DIR/frontend_vue3/depoly/photopolymer-frontend.conf"
echo "  目标位置: /etc/nginx/sites-available/photopolymer"
echo ""

# 4. 测试 Nginx 配置
echo -e "${GREEN}[4/6] 测试 Nginx 配置...${NC}"
if sudo nginx -t; then
    echo "✓ Nginx 配置测试通过"
else
    echo -e "${RED}✗ Nginx 配置有误，请检查${NC}"
    exit 1
fi
echo ""

# 5. 重新加载服务
echo -e "${GREEN}[5/6] 重新加载服务配置...${NC}"
sudo systemctl daemon-reload
echo "✓ Systemd 配置已重新加载"
echo ""

# 6. 启动服务
echo -e "${GREEN}[6/6] 启动服务...${NC}"

# 启动后端
sudo systemctl start photopolymer-api.service
sudo systemctl enable photopolymer-api.service
echo "✓ 后端服务已启动"

# 重新加载 Nginx
sudo systemctl reload nginx
echo "✓ Nginx 已重新加载"
echo ""

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 3
echo ""

# 检查服务状态
echo "=========================================="
echo -e "${GREEN}服务状态检查${NC}"
echo "=========================================="
echo ""

echo -e "${YELLOW}后端服务状态:${NC}"
sudo systemctl status photopolymer-api.service --no-pager -l || true
echo ""

echo -e "${YELLOW}Nginx 服务状态:${NC}"
sudo systemctl status nginx --no-pager | head -20 || true
echo ""

# 检查端口
echo "=========================================="
echo -e "${GREEN}端口监听检查${NC}"
echo "=========================================="
echo ""

echo -e "${YELLOW}后端端口 8000:${NC}"
sudo lsof -i :8000 | head -5 || echo "端口 8000 未被监听"
echo ""

echo -e "${YELLOW}前端端口 8080:${NC}"
sudo lsof -i :8080 | head -5 || echo "端口 8080 未被监听"
echo ""

# 显示日志查看命令
echo "=========================================="
echo -e "${GREEN}✅ 配置更新完成！${NC}"
echo "=========================================="
echo ""
echo "📍 访问地址："
echo "  前端应用: http://localhost:8080"
echo "  后端API:  http://localhost:8000"
echo "  API文档:  http://localhost:8000/docs"
echo ""
echo "📊 查看服务状态："
echo "  后端: sudo systemctl status photopolymer-api.service"
echo "  前端: sudo systemctl status nginx"
echo ""
echo "📝 查看日志："
echo "  后端实时日志: sudo journalctl -u photopolymer-api.service -f"
echo "  后端最近日志: sudo journalctl -u photopolymer-api.service -n 100 --no-pager"
echo "  Nginx访问日志: sudo tail -f /var/log/nginx/photopolymer-access.log"
echo "  Nginx错误日志: sudo tail -f /var/log/nginx/photopolymer-error.log"
echo ""
echo "🔧 管理命令："
echo "  重启后端: sudo systemctl restart photopolymer-api.service"
echo "  重启前端: sudo systemctl reload nginx"
echo "  停止所有: bash stop_system.sh"
echo ""

