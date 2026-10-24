@echo off
rem MetAI Toru - Windows launcher. The first run sets everything up (install_windows.ps1).
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_windows.ps1" -NoShortcuts
    if errorlevel 1 (
        pause
        exit /b 1
    )
)
start "" ".venv\Scripts\pythonw.exe" "%~dp0gui.py"
