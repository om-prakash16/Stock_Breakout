@echo off
TITLE Market Analytics System - Setup Only
echo ==================================================
echo Market Analytics System - Initial Setup (Windows)
echo ==================================================

REM Check for Python
py --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed.
    pause
    exit /b
)

REM Check for Node.js
node --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed.
    pause
    exit /b
)

echo.
echo [1/3] Setting up Python Virtual Environment...
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Creating venv...
    py -m venv venv
)

call venv\Scripts\activate.bat

echo.
echo [2/3] Installing Python Dependencies...
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b
)

echo.
echo [3/3] Installing Frontend Dependencies...
cd frontend
IF NOT EXIST "node_modules" (
    call npm install
)
cd ..

echo.
echo ==================================================
echo Setup Complete!
echo Run run_windows.bat to start the system.
echo ==================================================
pause
