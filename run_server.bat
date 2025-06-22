@echo off
echo Cataclysm: Looming Darkness Server
echo ===================================

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Creating required directories...
if not exist "accounts" mkdir accounts
if not exist "world" mkdir world
if not exist "log" mkdir log

echo Starting server...
python server.py

pause
