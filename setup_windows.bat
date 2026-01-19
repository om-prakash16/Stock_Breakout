@echo off
TITLE Market Analytics System - Setup Only
echo ==================================================
echo Market Analytics System - Initial Setup (Windows)
echo ==================================================

REM Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and try again.
    pause
    exit /b
)

REM Check for Node.js
node --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js (LTS) and try again.
    pause
    exit /b
)

echo.
echo [1/3] Setting up Python Virtual Environment...
IF NOT EXIST "venv" (
    echo Creating venv...
    python -m venv venv
)
call venv\Scripts\activate

echo.
echo [2/3] Installing Python Dependencies...
pip install -r backend\requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b
)

echo.
echo [3/3] Installing Frontend Dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing node modules...
    call npm install
)
cd ..

echo.
echo ==================================================
echo Setup Complete!
echo You can now run 'run_windows.bat' to start the system.
echo ==================================================
pause
