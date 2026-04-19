# MNEMOS-OS Ghost Kernel (IPC Listener)
# Copyright (c) 2026 Jonathan Schoenberger
# Licensed under the GNU General Public License v3.0 (GPLv3)

import os
import sys
import json
import threading
import sqlite3
import time

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.engine import MnemosCore

# Platform-specific IPC
if os.name == 'nt':
    import win32pipe, win32file, pywintypes
    PIPE_NAME = r'\\.\pipe\mnemos_ghost'
else:
    import socket
    SOCKET_PATH = '/tmp/mnemos_ghost.sock'

class GhostKernel:
    def __init__(self):
        self.core = MnemosCore()
        self.running = True
        self.start_time = time.time()
        # ANSI Colors
        self.C_CYN = "\033[96m"
        self.C_GRY = "\033[90m"
        self.C_RST = "\033[0m"
        self.C_BLU = "\033[94;1m"
        
        print(f" {self.C_BLU}[*] Ghost Kernel active.{self.C_RST} {self.C_GRY}(Branch: {self.core.branch}){self.C_RST}")

    def handle_client(self, handle):
        """Processes a single IPC request with micro-second precision logging."""
        start = time.time()
        try:
            if os.name == 'nt':
                resp, data = win32file.ReadFile(handle, 65536)
                request = json.loads(data.decode('utf-8'))
            else:
                data = handle.recv(65536)
                request = json.loads(data.decode('utf-8'))

            command = request.get("command")
            args = request.get("args", {})
            branch = request.get("branch", "main")
            
            result = self.route_command(command, args, branch)
            
            response_data = json.dumps(result).encode('utf-8')
            if os.name == 'nt':
                win32file.WriteFile(handle, response_data)
            else:
                handle.sendall(response_data)
                
            elapsed = (time.time() - start) * 1000
            print(f" {self.C_GRY}[{command.upper()}] {elapsed:.2f}ms{self.C_RST}")
                
        except Exception as e:
            print(f" [!] Error: {e}")
        finally:
            if os.name == 'nt':
                win32file.CloseHandle(handle)
            else:
                handle.close()

    def route_command(self, command, args, branch):
        """Maps IPC commands to MnemosCore methods with branch awareness."""
        try:
            # Inject branch into args for methods that support it
            if command in ["add", "context", "search", "list_memories", "update_scratchpad"]:
                args["branch_name"] = branch

            if command == "add":
                return {"id": self.core.add_fact(**args)}
            elif command == "context":
                # Ensure auto_hydrate is passed if present
                return {"context": self.core.get_context(**args)}
            elif command == "search":
                return {"results": self.core.search(**args)}
            elif command == "details":
                return {"details": self.core.get_memory_details(**args)}
            elif command == "list_entities":
                return {"entities": self.core.list_entities()}
            elif command == "list_memories":
                return {"results": self.core.list_memories(**args)}
            elif command == "update_scratchpad":
                return {"success": self.core.update_scratchpad(**args)}
            elif command == "update_task":
                return {"success": self.core.update_task(**args)}
            elif command == "ping":
                return {"status": "alive", "version": "1.2.2"}
            elif command == "stop":
                self.running = False
                return {"status": "descending"}
            else:
                return {"error": f"Unknown command: {command}"}
        except Exception as e:
            return {"error": str(e)}

    def run_windows(self):
        """Windows-specific Named Pipe listener loop with multi-instancing."""
        print(f"[*] Listening on {PIPE_NAME} (Multi-Instance)")
        
        def pipe_worker():
            while self.running:
                handle = None
                try:
                    handle = win32pipe.CreateNamedPipe(
                        PIPE_NAME,
                        win32pipe.PIPE_ACCESS_DUPLEX,
                        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                        20, 65536, 65536, 0, None
                    )
                    win32pipe.ConnectNamedPipe(handle, None)
                    # Start a new thread for this specific client to free up this pipe worker immediately
                    threading.Thread(target=self.handle_client, args=(handle,), daemon=True).start()
                except Exception as e:
                    if handle:
                        win32file.CloseHandle(handle)
                    if self.running:
                        time.sleep(0.1)

        # Start multiple workers to ensure at least one is always waiting for ConnectNamedPipe
        for _ in range(5):
            threading.Thread(target=pipe_worker, daemon=True).start()
            
        while self.running:
            time.sleep(0.5)

    def start(self):
        if os.name == 'nt':
            # run_windows now manages its own life cycle and workers
            self.run_windows()
        else:
            listener_thread = threading.Thread(target=self.run_unix, daemon=True)
            listener_thread.start()
            # Keep the main thread alive until 'stop' command is received
            while self.running:
                time.sleep(0.5)
            
        print(f" {self.C_GRY}[!] Closing MÍMIR-DB connections...{self.C_RST}")
        self.core.close()
        print(f" {self.C_BLU}[✔] Ghost Kernel successfully descended into the void.{self.C_RST}")

if __name__ == "__main__":
    ghost = GhostKernel()
    try:
        ghost.start()
    except KeyboardInterrupt:
        print("\n[*] Ghost Kernel descending into the void...")
        sys.exit(0)
