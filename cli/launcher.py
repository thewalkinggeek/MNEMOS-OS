# MNEMOS-OS Transparent Launcher
# Copyright (c) 2026 Jonathan Schoenberger
# Licensed under the GNU General Public License v3.0 (GPLv3)

import sys
import os
import subprocess

# Ensure the root directory is in sys.path before importing from cli
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from cli.mnemos import get_console

console = get_console()

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
        console.print(f"[magenta][*] Launching MCP Server...[/magenta]")
        console.print(f"[gray][NOTE] This mode is for AI agents. Human input will cause JSON errors.[/gray]\n")
        subprocess.run([sys.executable, os.path.join("cli", "mcp_server.py")])

    elif cmd == "ghost":
        # Launch Ghost Kernel (Foreground Mode)
        console.print(f"[magenta][*] Launching Ghost Kernel (Foreground)...[/magenta]")
        console.print(f"[gray][NOTE] Zero-latency daemon now active. Press Ctrl+C to stop.[/gray]\n")
        subprocess.run([sys.executable, os.path.join("cli", "mnemos.py"), "ghost"])
        
    else:
        # Fallback: Pass to mnemos.py (Direct Command Mode)
        subprocess.run([sys.executable, os.path.join("cli", "mnemos.py")] + args)

if __name__ == "__main__":
    main()
