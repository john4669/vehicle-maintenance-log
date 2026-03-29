@echo off
echo ============================================
echo  Building Vehicle Maintenance Log
echo ============================================
echo.

call venv\Scripts\activate
pyinstaller VehicleLog.spec --clean

if errorlevel 1 (
    echo.
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Build complete!
echo  Output: dist\VehicleMaintenanceLog.exe
echo ============================================
echo.
pause
