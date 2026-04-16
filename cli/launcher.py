# MNEMOS-OS Transparent Launcher
# Copyright (c) 2026 Jonathan Schoenberger
# Licensed under the GNU General Public License v3.0 (GPLv3)

import sys
import os
import subprocess

def main():
    # Enable ANSI escape sequences on Windows
    if os.name == 'nt':
        os.system("")
        
    # Get subcommand if any
    args = sys.argv[1:]
    cmd = args[0].lower() if args else "cli"
    
    if cmd == "cli":
        # Default: Go straight to Interactive Terminal
        subprocess.run([sys.executable, os.path.join("cli", "terminal.py")])
        
    elif cmd == "mcp":
        # Launch MCP Server (Debug/Manual Mode)
        print(f"\033[35;1m[*] Launching MCP Server...\033[0m")
        print(f"\033[90m[NOTE] This mode is for AI agents. Human input will cause JSON errors.\033[0m\n")
        subprocess.run([sys.executable, os.path.join("cli", "mcp_server.py")])

    elif cmd == "ghost":
        # Launch Ghost Kernel (Foreground Mode)
        print(f"\033[35;1m[*] Launching Ghost Kernel (Foreground)...\033[0m")
        print(f"\033[90m[NOTE] Zero-latency daemon now active. Press Ctrl+C to stop.\033[0m\n")
        subprocess.run([sys.executable, os.path.join("cli", "mnemos.py"), "ghost"])
        
    else:
        # Fallback: Pass to mnemos.py (Direct Command Mode)
        subprocess.run([sys.executable, os.path.join("cli", "mnemos.py")] + args)

if __name__ == "__main__":
    main()
