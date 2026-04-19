#!/bin/bash

# MNEMOS-OS: Cognitive Memory Layer (Linux/macOS)
# ---------------------------------------------------

# Ensure we are in the script directory
cd "$(dirname "$0")"

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 not found. Please install Python 3.8+."
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "- Creating environment..."
    python3 -m venv venv &> /dev/null
fi

# 3. Activate Virtual Environment
source venv/bin/activate

# 4. Upgrade Pip & Install Dependencies (Silent for MCP support)
python3 -m pip install --upgrade pip -q
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt -q
fi

# 5. Routing
if [ "$1" == "setup" ]; then
    echo "[MNEMOS-OS SETUP]"
    echo "- Ensuring dependencies are installed..."
    python3 -m pip install -r requirements.txt -q
    echo "- Registering MNEMOS-OS MCP Server with Gemini CLI..."
    # Get the absolute path to this script
    SCRIPT_PATH="$(realpath "$0")"
    if command -v gemini &> /dev/null; then
        gemini mcp add mnemos-os "$SCRIPT_PATH" mcp
        echo "[+] MNEMOS-OS MCP Server registered successfully."
    else
        echo "[!] Gemini CLI not found. Please manually register using:"
        echo "    gemini mcp add mnemos-os \"$SCRIPT_PATH\" mcp"
    fi
    echo "[✔] Setup complete."
    exit 0
elif [ "$1" == "ghost" ]; then
    python3 cli/mnemos.py ghost
    exit $?
elif [ "$1" == "mcp" ]; then
    python3 cli/mcp_server.py
    exit $?
elif [ "$1" == "cli" ]; then
    python3 cli/terminal.py
    exit $?
elif [ -z "$1" ]; then
    python3 cli/launcher.py
    exit $?
else
    python3 cli/mnemos.py "$@"
    exit $?
fi
