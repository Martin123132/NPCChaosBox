@echo off
setlocal
cd /d "%~dp0"

if not defined NPC_CHAOS_HOME set "NPC_CHAOS_HOME=%~dp0user-data"
if not exist "%NPC_CHAOS_HOME%" mkdir "%NPC_CHAOS_HOME%"
if not exist "%~dp0temp" mkdir "%~dp0temp"
set "TEMP=%~dp0temp"
set "TMP=%~dp0temp"

set "PYTHON_CMD="
call :check_python python
if defined PYTHON_CMD goto run_app
call :check_python py -3
if defined PYTHON_CMD goto run_app

echo NPC Chaos Box needs Python 3.10 or newer.
echo.
echo What to do:
echo   1. Go to https://www.python.org/downloads/windows/
echo   2. Download and install Python.
echo   3. Tick "Add python.exe to PATH" during install.
echo   4. Double-click START_NPCChaos_WINDOWS.bat again.
echo.
echo NPC Chaos Box has not changed your system settings.
echo Your app data folder would be:
echo   %NPC_CHAOS_HOME%
echo.
pause
exit /b 1

:run_app
echo Starting NPC Chaos Box with %PYTHON_CMD% ...
echo Data folder:
echo   %NPC_CHAOS_HOME%
echo.
echo Your browser should open in a moment.
echo.
%PYTHON_CMD% -m npc_chaos_app.app
pause
exit /b 0

:check_python
%* -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=%*"
exit /b 0

