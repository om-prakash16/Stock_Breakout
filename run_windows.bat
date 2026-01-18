@echo off
TITLE Market Analytics System
echo ==================================================
echo Market Analytics System - Launcher (Windows)
echo ==================================================

if not exist "venv" (
    echo [ERROR] Virtual environment not found.
    echo Please run 'setup_windows.bat' first.
    pause
    exit /b
)

echo Activating environment...
call venv\Scripts\activate

echo Starting servers...
echo The dashboard will be available at http://localhost:3000
echo Ctrl+C to stop.
echo.

venv\Scripts\python.exe start_servers.py
pause
