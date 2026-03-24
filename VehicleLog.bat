@echo off
:: Vehicle Maintenance Log - Launcher
:: Double-click this file to start the app

cd /d "%~dp0"

:: Check if setup has been run
if not exist "venv\Scripts\python.exe" (
    echo.
    echo The app has not been set up yet.
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

:: Launch the app
start "" venv\Scripts\pythonw.exe main.py
