@echo off
chcp 65001 >nul
cls
echo ================================================
echo   光创化物 R&D 配方管理系统 - 开发环境启动
echo ================================================
echo.

echo [1/3] 检查环境...
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
echo ✓ Python 已安装

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)
echo ✓ Node.js 已安装

REM 检查 pnpm
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo ⚠ 未检测到 pnpm，将使用 npm
    set USE_NPM=1
) else (
    echo ✓ pnpm 已安装
    set USE_NPM=0
)

echo.
echo [2/3] 启动后端服务 (FastAPI)...
echo.
cd /d "%~dp0backend_fastapi"
start "后端服务 - FastAPI" cmd /k "python main.py run --env=dev"
timeout /t 3 /nobreak >nul
cd /d "%~dp0"

echo.
echo [3/3] 启动前端服务 (Vue3)...
echo.
cd /d "%~dp0frontend_vue3"

REM 检查是否已安装依赖
if not exist "node_modules" (
    echo 首次运行，正在安装依赖...
    if %USE_NPM%==1 (
        call npm install
    ) else (
        call pnpm install
    )
)

if %USE_NPM%==1 (
    start "前端服务 - Vue3" cmd /k "npm run dev"
) else (
    start "前端服务 - Vue3" cmd /k "pnpm dev"
)

cd /d "%~dp0"

echo.
echo ================================================
echo   ✓ 服务启动完成！
echo ================================================
echo.
echo 📌 后端服务: http://localhost:8000
echo    API文档: http://localhost:8000/docs
echo.
echo 📌 前端服务: http://localhost:3000
echo.
echo 按任意键关闭此窗口...
pause >nul

