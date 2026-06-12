@echo off
setlocal enabledelayedexpansion

echo ==============================================
echo         JMH-MoviePop Backend Server
echo ==============================================
echo.

set "BACKEND_DIR=%~dp0backend"

echo [1/2] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python environment not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo Python environment is ready

echo.
echo [2/2] Starting backend server...
echo Server will be available at http://localhost:8000
echo API docs: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

cd /d "%BACKEND_DIR%"
python run.py

echo.
echo Backend server stopped
pause