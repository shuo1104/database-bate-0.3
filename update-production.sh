#!/bin/bash
# 更新生产环境脚本 - 自动检测项目路径

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "更新生产环境 (8080端口)"
echo "=========================================="

# 获取脚本所在目录作为项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
FRONTEND_DIR="$PROJECT_ROOT/frontend_vue3"

echo -e "${YELLOW}项目根目录: $PROJECT_ROOT${NC}"
echo ""

# 1. 重新构建前端
echo -e "${GREEN}步骤 1/4: 重新构建前端...${NC}"
cd "$FRONTEND_DIR"
npm run build
echo -e "${GREEN}✓ 前端构建完成${NC}"
echo ""

# 2. 更新 Nginx 配置（替换占位符为实际路径）
echo -e "${GREEN}步骤 2/4: 更新 Nginx 配置...${NC}"
NGINX_CONF_TEMPLATE="$FRONTEND_DIR/depoly/photopolymer-frontend.conf"
NGINX_CONF_TEMP="/tmp/photopolymer-frontend.conf.tmp"

# 替换占位符
sed "s|__PROJECT_ROOT__|$PROJECT_ROOT|g" "$NGINX_CONF_TEMPLATE" > "$NGINX_CONF_TEMP"

# 复制到系统目录
sudo cp "$NGINX_CONF_TEMP" /etc/nginx/sites-available/photopolymer-frontend.conf
rm "$NGINX_CONF_TEMP"
echo -e "${GREEN}✓ Nginx 配置已更新${NC}"
echo ""

# 3. 测试 Nginx 配置
echo -e "${GREEN}步骤 3/4: 测试 Nginx 配置...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}✓ Nginx 配置测试通过${NC}"
else
    echo -e "${RED}✗ Nginx 配置有误，请检查${NC}"
    exit 1
fi
echo ""

# 4. 重启 Nginx
echo -e "${GREEN}步骤 4/4: 重启 Nginx...${NC}"
sudo systemctl reload nginx
echo -e "${GREEN}✓ Nginx 已重启${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ 生产环境更新完成！${NC}"
echo "=========================================="
echo ""
echo "现在可以访问 http://localhost:8080/ 查看更新后的应用"
echo ""

