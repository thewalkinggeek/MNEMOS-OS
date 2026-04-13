# MNEMOS-OS Launcher
# Copyright (c) 2026 Jonathan Schoenberger
# Licensed under the GNU General Public License v3.0 (GPLv3)
# See LICENSE file for full license text.

import sys
import os
import subprocess

# Colors
BLU = "\033[94;1m"
MAG = "\033[35;1m"
WHT = "\033[37;1m"
GRY = "\033[90m"
RST = "\033[0m"
RED = "\033[31;1m"

def main():
    # Enable ANSI escape sequences on Windows
    if os.name == 'nt':
        os.system("")
        
    def show_menu():
        os.system('cls' if os.name == 'nt' else 'clear')
        print()
        print(f" 🧠  {BLU}MNEMOS-OS{RST} {GRY}v1.2.0{RST}")
        print()
        print(f" {MAG}>{RST} {WHT}The Memory Kernel for AI{RST}")
        print()
        print(f" {GRY}----------------------------------{RST}")
        print()
        print(f" {WHT}Select Mode:{RST}")
        print()
        print(f" {BLU}[1]{RST} Interactive Terminal {GRY}(Standard Use){RST}")
        print(f" {BLU}[2]{RST} MCP Server {GRY}(AI Connection / Debug){RST}")
        print()

    show_menu()
    
    while True:
        try:
            choice = input(f" selection {MAG}>{RST} ").strip()
            
            if choice == "1":
                while True:
                    # Run the interactive terminal
                    res = subprocess.run([sys.executable, os.path.join("cli", "terminal.py")])
                    # 100 means 'menu' command was typed
                    if res.returncode == 100:
                        show_menu()
                        break
                    else:
                        # Exited normally
                        return
                        
            elif choice == "2":
                print()
                print(f" {MAG}[*]{RST} Launching MCP Server...")
                print(f" {GRY}[NOTE] This mode is for AI agents. Human input will cause JSON errors.{RST}")
                print()
                subprocess.run([sys.executable, os.path.join("cli", "mcp_server.py")])
                return
                
            else:
                print(f" {RED}Invalid selection. Please enter 1 or 2.{RST}")
                
        except KeyboardInterrupt:
            print()
            sys.exit(0)
        except EOFError:
            print()
            sys.exit(0)

if __name__ == "__main__":
    main()
