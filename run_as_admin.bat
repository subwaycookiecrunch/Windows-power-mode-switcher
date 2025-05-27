@echo off
:: Check for administrative privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
    python "%~dp0power_mode_switcher.py"
) else (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: Change to the directory where the batch file is located
cd /d "%~dp0"

:: Run the Python script
echo Starting Power Mode Switcher...
python power_mode_switcher.py

:: Pause so the user can see any error messages
pause
