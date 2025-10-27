@echo off
chcp 65001 >nul
echo ============================================================
echo 停止所有 Python 进程并重启后端
echo ============================================================
echo.

echo [1/3] 停止所有 Python 进程...
taskkill /F /IM python.exe /T >nul 2>&1
if %ERRORLEVEL%==0 (
    echo     ✓ Python 进程已停止
) else (
    echo     - 没有运行中的 Python 进程
)
timeout /t 2 /nobreak >nul

echo.
echo [2/3] 等待端口释放...
timeout /t 3 /nobreak >nul
echo     ✓ 端口已释放

echo.
echo [3/3] 启动后端服务...
cd /d "%~dp0backend_fastapi"
echo     启动目录: %CD%
echo.
echo ============================================================
echo 后端服务启动中...
echo 环境: dev
echo 端口: 8000
echo ============================================================
echo.

python main.py run --env=dev

pause

