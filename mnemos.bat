@echo off
setlocal enabledelayedexpansion

:: Force UTF-8 for emoji support
chcp 65001 >nul

:: Define Basic Colors
set "ESC="
set "BLU=%ESC%[94;1m"
set "MAG=%ESC%[35;1m"
set "WHT=%ESC%[37;1m"
set "GRY=%ESC%[90m"
set "RST=%ESC%[0m"
set "RED=%ESC%[31;1m"

TITLE MNEMOS-OS
cd /d "%~dp0"

:: 1. AI Fast-Path (Must be 100% silent)
if "%~1"=="mcp" goto :RUN_MCP

:: 2. Splash Header (Human only)
echo.
echo  🧠  %BLU%Mnemos-OS%RST% %GRY%v1.0.0%RST%
echo.
echo  %MAG%^>%RST% %WHT%The Memory Kernel for AI%RST%
echo.
echo  %GRY%----------------------------------%RST%
echo.

:: 3. Basic Python Check
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  %RED%[!] Python not found. Please install Python 3.8+.%RST%
    pause
    exit /b 1
)

:: 4. Venv Sync
if not exist "venv\" (
    echo  %GRY%-%RST% Creating isolated environment...
    python -m venv venv >nul
)

:: Activate the environment
call venv\Scripts\activate.bat

:: 5. Routing
if "%~1"=="cli" goto :RUN_CLI
if "%~1"=="" goto :MENU

:: Argument Mode (Pass-through)
python cli\mnemos.py %*
goto :EOF

:MENU
echo  %WHT%Select Mode:%RST%
echo.
echo  %BLU%[1]%RST% Interactive Terminal %GRY%(Standard Use)%RST%
echo  %BLU%[2]%RST% MCP Server %GRY%(AI Connection / Debug)%RST%
echo.
set /p choice="selection %MAG%^>%RST% "

if "!choice!"=="1" goto :RUN_CLI
if "!choice!"=="2" (
    echo.
    echo  %MAG%[*]%RST% Launching MCP Server...
    echo  %GRY%[NOTE] This mode is for AI agents. Human input will cause JSON errors.%RST%
    echo.
    goto :RUN_MCP
)

echo %RED%Invalid selection.%RST%
pause
exit /b 1

:RUN_CLI
python cli\terminal.py
if !ERRORLEVEL! EQU 100 goto :MENU
goto :EOF

:RUN_MCP
if not defined VIRTUAL_ENV (
    call venv\Scripts\activate.bat >nul 2>&1
)
python cli\mcp_server.py
