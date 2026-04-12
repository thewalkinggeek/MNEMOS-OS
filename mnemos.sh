#!/bin/bash

# MNEMOS-OS: Cognitive Memory Layer (Linux/macOS)
# ---------------------------------------------------

# 1. Colors and Symbols
BLUE='\033[1;94m'
MAGENTA='\033[1;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
RED='\033[1;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Ensure we are in the script directory
cd "$(dirname "$0")"

# Fast-path for AI
if [ "$1" == "mcp" ]; then
    source venv/bin/activate &> /dev/null
    python3 cli/mcp_server.py
    exit 0
fi

echo -e ""
echo -e " 🧠  ${BLUE}Mnemos-OS${NC} ${GRAY}v1.0.0${NC}"
echo -e ""
echo -e "${MAGENTA}> ${WHITE}The Memory Kernel for AI${NC}"
echo -e ""
echo -e "${GRAY}----------------------------------${NC}"
echo -e ""

# 2. Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!]${NC} Python3 not found. Please install Python 3.8+."
    exit 1
fi

# 3. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo -e "${GRAY}-${NC} Creating environment..."
    python3 -m venv venv &> /dev/null
fi

# 4. Activate Virtual Environment
source venv/bin/activate

# 5. Upgrade Pip & Install Dependencies
python3 -m pip install --upgrade pip -q
if [ -f "requirements.txt" ]; then
    echo -e "${GRAY}-${NC} Syncing dependencies..."
    pip install -r requirements.txt -q
fi

# 6. Initialize Database if missing
if [ ! -f "data/mnemos.db" ]; then
    echo -e "${GRAY}-${NC} Initializing Mimir-DB..."
    cd data && python3 init_db.py &> /dev/null && cd ..
fi

echo -e "${GREEN}[*]${NC} System online"
echo ""

# 7. Menu Loop
while true; do
    if [ "$1" == "cli" ]; then
        python3 cli/terminal.py
        exit $?
    elif [ -z "$1" ]; then
        echo -e "${WHITE}Select Mode:${NC}"
        echo ""
        echo -e "  ${BLUE}[1]${NC} Interactive Terminal ${GRAY}(Standard Use)${NC}"
        echo -e "  ${BLUE}[2]${NC} MCP Server ${GRAY}(AI Connection / Debug)${NC}"
        echo ""
        
        # Cross-platform prompt logic
        echo -n -e "selection ${MAGENTA}'> '${NC}"
        read choice
        
        if [ "$choice" == "1" ]; then
            python3 cli/terminal.py
            if [ $? -ne 100 ]; then exit 0; fi
        elif [ "$choice" == "2" ]; then
            echo ""
            echo -e "${MAGENTA}[*]${NC} Launching MCP Server..."
            echo -e "${GRAY}[NOTE] This mode is for AI agents. Human input will cause JSON errors.${NC}"
            echo ""
            python3 cli/mcp_server.py
            exit $?
        elif [[ "$choice" == "exit" || "$choice" == "quit" ]]; then
            exit 0
        else
            echo -e "${RED}[!] Invalid selection.${NC}"
        fi
    else
        python3 cli/mnemos.py "$@"
        exit $?
    fi
done
