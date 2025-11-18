#!/bin/bash
# 网络配置诊断脚本

echo "=========================================="
echo "网络配置诊断"
echo "=========================================="
echo ""

# 1. 检查局域网 IP
echo "【1】局域网 IP 地址："
hostname -I | awk '{print $1}'
echo ""

# 2. 检查公网 IP
echo "【2】公网 IP 地址："
PUBLIC_IP=$(curl -s --max-time 5 ifconfig.me)
if [ -n "$PUBLIC_IP" ]; then
    echo "$PUBLIC_IP"
    
    # 判断是否是公网IP
    if [[ $PUBLIC_IP =~ ^192\.168\. ]] || [[ $PUBLIC_IP =~ ^10\. ]] || [[ $PUBLIC_IP =~ ^172\.(1[6-9]|2[0-9]|3[0-1])\. ]]; then
        echo "⚠️  这是一个局域网IP，不是公网IP"
        echo "   您可能在路由器后面，需要配置端口转发"
    else
        echo "✓ 这是一个公网IP"
    fi
else
    echo "✗ 无法获取公网IP（可能没有外网连接）"
fi
echo ""

# 3. 检查端口监听状态
echo "【3】端口监听状态："
echo "前端端口 8080："
if netstat -tlnp 2>/dev/null | grep -q ":8080"; then
    echo "✓ 正在监听"
    netstat -tlnp 2>/dev/null | grep ":8080"
else
    echo "✗ 未监听"
fi
echo ""

echo "后端端口 8000："
if netstat -tlnp 2>/dev/null | grep -q ":8000"; then
    echo "✓ 正在监听"
    netstat -tlnp 2>/dev/null | grep ":8000"
else
    echo "✗ 未监听"
fi
echo ""

# 4. 检查防火墙状态
echo "【4】防火墙状态："
if command -v ufw &> /dev/null; then
    sudo ufw status | grep -E "8080|8000|Status"
else
    echo "未安装 ufw"
fi
echo ""

# 5. 检查当前配置
echo "【5】当前配置："
echo "后端 CORS 配置："
grep -A 5 "ALLOW_ORIGINS" ~/workspace/database/data_base/backend_fastapi/app/config/settings.py | grep "http://"
echo ""

echo "前端 API 地址："
grep "VITE_API_BASE_URL" ~/workspace/database/data_base/frontend_vue3/.env.production
echo ""

# 6. 访问建议
echo "=========================================="
echo "【访问建议】"
echo "=========================================="
echo ""

LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "✓ 局域网访问（同一网络下的设备）："
echo "  http://$LOCAL_IP:8080"
echo ""

if [ -n "$PUBLIC_IP" ] && ! [[ $PUBLIC_IP =~ ^192\.168\. ]] && ! [[ $PUBLIC_IP =~ ^10\. ]]; then
    echo "✓ 公网访问（需要配置防火墙和端口转发）："
    echo "  http://$PUBLIC_IP:8080"
    echo ""
    echo "  需要做的配置："
    echo "  1. 开放防火墙端口: sudo ufw allow 8080/tcp"
    echo "  2. 如果在路由器后面，需要配置端口转发"
    echo "  3. 修改配置文件中的IP地址为: $PUBLIC_IP"
else
    echo "⚠️  无公网IP，外网无法直接访问"
    echo ""
    echo "  解决方案："
    echo "  1. 联系网络运营商获取公网IP"
    echo "  2. 配置路由器端口转发（如果有公网IP）"
    echo "  3. 使用内网穿透工具（ngrok, frp, cpolar等）"
fi
echo ""

echo "=========================================="

