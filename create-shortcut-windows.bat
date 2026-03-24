@echo off
:: Creates a desktop shortcut for Vehicle Maintenance Log
:: Run this once from the project folder

set "APP_DIR=%~dp0"
set "SHORTCUT=%USERPROFILE%\Desktop\Vehicle Maintenance Log.lnk"

:: Use PowerShell to create the shortcut
powershell -NoProfile -Command ^
    "$ws = New-Object -ComObject WScript.Shell; ^
     $sc = $ws.CreateShortcut('%SHORTCUT%'); ^
     $sc.TargetPath = '%APP_DIR%VehicleLog.bat'; ^
     $sc.WorkingDirectory = '%APP_DIR%'; ^
     $sc.IconLocation = '%APP_DIR%icon.ico,0'; ^
     $sc.Description = 'Track vehicle maintenance, costs, and service history'; ^
     $sc.Save()"

if exist "%SHORTCUT%" (
    echo Desktop shortcut created successfully!
    echo Location: %SHORTCUT%
) else (
    echo ERROR: Could not create shortcut.
    echo Try right-clicking and running as Administrator.
)
echo.
pause
