#!/bin/bash

# 材料数据库系统 - 停止脚本
# 用途: 停止所有系统组件

echo "=========================================="
echo "  停止材料数据库系统"
echo "=========================================="
echo ""

# 1. 停止后端 FastAPI
echo "1. 停止后端服务..."
BACKEND_PIDS=$(lsof -t -i:8000 2>/dev/null)
if [ -n "$BACKEND_PIDS" ]; then
    echo "   发现后端进程: $BACKEND_PIDS"
    kill $BACKEND_PIDS
    sleep 2
    
    # 检查是否还在运行
    STILL_RUNNING=$(lsof -t -i:8000 2>/dev/null)
    if [ -n "$STILL_RUNNING" ]; then
        echo "   进程未响应，强制关闭..."
        kill -9 $STILL_RUNNING
    fi
    echo "   ✅ 后端已停止"
else
    echo "   ℹ️  后端未运行"
fi

# 2. 停止前端开发服务器（如果在运行）
echo ""
echo "2. 停止前端开发服务器..."
VITE_PIDS=$(pgrep -f "vite.*frontend_vue3" 2>/dev/null)
if [ -n "$VITE_PIDS" ]; then
    echo "   发现 Vite 进程: $VITE_PIDS"
    kill $VITE_PIDS
    echo "   ✅ 前端开发服务器已停止"
else
    echo "   ℹ️  前端开发服务器未运行"
fi

# 3. 停止 Nginx
echo ""
echo "3. 停止 Nginx..."
if systemctl is-active --quiet nginx; then
    sudo systemctl stop nginx
    echo "   ✅ Nginx 已停止"
else
    echo "   ℹ️  Nginx 未运行"
fi

# 4. 显示状态
echo ""
echo "=========================================="
echo "  系统状态"
echo "=========================================="
echo "后端 (8000端口): $(lsof -i:8000 2>/dev/null && echo '❌ 仍在运行' || echo '✅ 已停止')"
echo "前端 (3000端口): $(lsof -i:3000 2>/dev/null && echo '❌ 仍在运行' || echo '✅ 已停止')"
echo "Nginx (80/8080): $(systemctl is-active nginx 2>/dev/null | grep -q active && echo '❌ 仍在运行' || echo '✅ 已停止')"
echo "PostgreSQL:      $(systemctl is-active postgresql 2>/dev/null | grep -q active && echo '✅ 运行中' || echo '❌ 已停止')"
echo ""
echo "✅ 系统停止完成！"

