@echo off
echo Cataclysm: Looming Darkness Client
echo ===================================

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Installing requirements...
python -m pip install -r client_requirements.txt

echo Starting client...
python client.py

pause
