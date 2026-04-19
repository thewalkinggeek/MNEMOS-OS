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
if /i "%~1"=="setup" goto :RUN_SETUP
if /i "%~1"=="ghost" goto :RUN_GHOST
if /i "%~1"=="mcp" goto :RUN_MCP
if /i "%~1"=="cli" goto :RUN_CLI
if "%~1"=="" goto :RUN_LAUNCHER

:: Argument Mode (Pass-through)
python cli\mnemos.py %*
goto :EOF

:RUN_SETUP
echo [MNEMOS-OS SETUP]
echo - Ensuring dependencies are installed...
python -m pip install -r requirements.txt -q
echo - Registering MNEMOS-OS MCP Server with Gemini CLI...
:: Use the full path to the batch script itself for the MCP command
set "SCRIPT_PATH=%~f0"
gemini mcp add mnemos-os "%SCRIPT_PATH%" mcp 2>nul
if errorlevel 1 (
    echo [!] Gemini CLI not found or registration failed.
    echo [!] Please manually add the MCP server using:
    echo     gemini mcp add mnemos-os "%SCRIPT_PATH%" mcp
) else (
    echo [+] MNEMOS-OS MCP Server registered successfully.
)
echo [✔] Setup complete. Use 'mnemos mcp' to verify.
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

:RUN_GHOST
python cli\mnemos.py ghost
goto :EOF
