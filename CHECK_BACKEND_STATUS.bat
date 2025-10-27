@echo off
chcp 65001 >nul
echo ============================================================
echo 检查后端服务状态
echo ============================================================
echo.

echo [1] 检查 Python 进程...
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Select-Object Id,StartTime,Path | Format-Table"

echo.
echo [2] 检查 8000 端口占用...
netstat -ano | findstr :8000

echo.
echo [3] 测试后端健康检查...
curl -s http://localhost:8000/health 2>nul
if %ERRORLEVEL%==0 (
    echo.
    echo     ✓ 后端服务正常运行
) else (
    echo.
    echo     ✗ 后端服务未响应
)

echo.
echo [4] 测试日志 API...
curl -s "http://localhost:8000/api/v1/logs/statistics" 2>nul
if %ERRORLEVEL%==0 (
    echo.
    echo     ✓ 日志 API 可访问
) else (
    echo.
    echo     ✗ 日志 API 不可访问（可能需要认证）
)

echo.
pause

