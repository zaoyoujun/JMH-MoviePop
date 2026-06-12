@echo off
chcp 65001 >nul
echo ==============================================
echo         JMH-MoviePop 后端停止脚本
echo ==============================================
echo.

echo 正在查找并终止后端服务...
echo.

tasklist | findstr /i "python.exe" >nul
if %errorlevel% equ 0 (
    echo 找到以下 Python 进程：
    tasklist | findstr /i "python.exe"
    echo.
    echo 正在终止进程...
    taskkill /f /im python.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo 后端服务已成功停止
    ) else (
        echo 停止服务时出现错误
    )
) else (
    echo 未找到运行中的 Python 进程，服务可能已停止
)

echo.
pause