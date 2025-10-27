@echo off
chcp 65001 >nul
echo ========================================
echo   启动 光创化物 R^&D 配方管理系统
echo ========================================
echo.

echo [1/4] 检查环境...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

echo ✅ Python 已安装
echo ✅ Node.js 已安装
echo.

echo [2/4] 启动后端服务...
cd /d "%~dp0backend_fastapi"
start "后端服务 - FastAPI" cmd /k "python main.py run --env=dev"
echo ✅ 后端服务启动中...（新窗口）
echo    地址: http://localhost:8000
echo    文档: http://localhost:8000/docs
echo.

echo [3/4] 等待后端启动 (5秒)...
timeout /t 5 /nobreak >nul
echo.

echo [4/4] 启动前端服务...
cd /d "%~dp0frontend_vue3"

REM 检查是否需要安装依赖
if not exist "node_modules\" (
    echo ⚠️  未检测到 node_modules，正在安装依赖...
    echo    这可能需要几分钟时间...
    call pnpm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败，尝试使用 npm...
        call npm install
    )
)

start "前端服务 - Vue3" cmd /k "pnpm dev"
echo ✅ 前端服务启动中...（新窗口）
echo    地址: http://localhost:3000
echo.

echo ========================================
echo   🎉 所有服务已启动！
echo ========================================
echo.
echo   后端服务: http://localhost:8000
echo   API 文档: http://localhost:8000/docs
echo   前端应用: http://localhost:3000
echo.
echo   提示：两个服务窗口将保持打开状态
echo   关闭窗口即可停止对应服务
echo.

timeout /t 3 >nul
start http://localhost:3000

echo 按任意键关闭此窗口...
pause >nul

