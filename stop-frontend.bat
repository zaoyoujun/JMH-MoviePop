@echo off
chcp 65001 >nul
echo ==============================================
echo         JMH-MoviePop 前端停止脚本
echo ==============================================
echo.

echo 正在查找并终止 Vite 开发服务器...
echo.

:: 查找并终止所有 node.exe 进程（Vite 通常以 node 运行）
tasklist | findstr /i "node.exe" >nul
if %errorlevel% equ 0 (
    echo 找到以下 node 进程：
    tasklist | findstr /i "node.exe"
    echo.
    echo 正在终止进程...
    taskkill /f /im node.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo 前端服务已成功停止
    ) else (
        echo 停止服务时出现错误
    )
) else (
    echo 未找到运行中的 node 进程，服务可能已停止
)

echo.
pause