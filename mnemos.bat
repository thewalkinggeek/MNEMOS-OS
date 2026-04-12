@echo off
setlocal

TITLE MNEMOS-OS
cd /d "%~dp0"

:: 1. Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python not found. Please install Python 3.8+.
    pause
    exit /b 1
)

:: 2. Venv Sync
if not exist "venv\" (
    echo - Creating isolated environment...
    python -m venv venv >nul
)

call venv\Scripts\activate.bat

if exist "requirements.txt" (
    :: Run silently to avoid prompt flashing during MCP startup
    python -m pip install -r requirements.txt -q
)

:: 3. Routing
if /i "%~1"=="mcp" goto :RUN_MCP
if /i "%~1"=="cli" goto :RUN_CLI
if "%~1"=="" goto :RUN_LAUNCHER

:: Argument Mode (Pass-through)
python cli\mnemos.py %*
goto :EOF

:RUN_LAUNCHER
python cli\launcher.py
goto :EOF

:RUN_CLI
python cli\terminal.py
goto :EOF

:RUN_MCP
python cli\mcp_server.py
goto :EOF
