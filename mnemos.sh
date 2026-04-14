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
if [ "$1" == "ghost" ]; then
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
