@echo off
echo ============================================
echo  Vehicle Maintenance Log - First Time Setup
echo ============================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in your PATH.
    echo.
    echo Please install Python 3.10 or newer from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, check the box that says
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [1/3] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo [3/3] Setup complete!
echo.
echo ============================================
echo  You can now launch the app by double-clicking:
echo  VehicleLog.bat
echo ============================================
echo.
pause
