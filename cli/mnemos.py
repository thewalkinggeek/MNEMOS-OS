# MNEMOS-OS Script Interface (Non-Interactive)
# Copyright © 2026 Jonathan Schoenberger
# Licensed under the GNU General Public License v3.0 (GPLv3)
# See LICENSE file for full license text.

import sys
import os
import argparse

# Add the parent directory to sys.path so we can import core.engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import MnemosCore

# ANSI Color Constants for standard terminal output
C_GRN = "\033[92m"
C_YLW = "\033[93m"
C_CYN = "\033[96m"
C_RED = "\033[91m"
C_BLU = "\033[94;1m" # Gemini Blue
C_MAG = "\033[35;1m" # Gemini Magenta
C_RST = "\033[0m"
C_BLD = "\033[1m"
C_GRY = "\033[90m"

import json
import socket
import time

class GhostBridge:
    """Zero-latency bridge to the Ghost Kernel daemon."""
    def __init__(self, autostart=True, silent=False):
        self.is_connected = False
        self.silent = silent
        self.pipe_name = r'\\.\pipe\mnemos_ghost' if os.name == 'nt' else '/tmp/mnemos_ghost.sock'
        self._connect()
        if not self.is_connected and autostart and os.environ.get("MNEMOS_NO_AUTOSTART") != "1":
            self.launch_ghost()
            # Wait briefly for the daemon to initialize the IPC channel
            time.sleep(1.5)
            self._connect()

    def _connect(self):
        try:
            if os.name == 'nt':
                import win32file, pywintypes
                self.handle = win32file.CreateFile(
                    self.pipe_name,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0, None, win32file.OPEN_EXISTING, 0, None
                )
                self.is_connected = True
            else:
                self.handle = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.handle.connect(self.pipe_name)
                self.is_connected = True
        except Exception:
            self.is_connected = False

    def launch_ghost(self):
        """Spawns the Ghost Kernel as a detached background process (Self-Healing)."""
        import subprocess
        # Use sys.executable to ensure we use the same venv
        cmd = [sys.executable, os.path.abspath(__file__), "ghost"]
        try:
            if os.name == 'nt':
                # Windows Detached Process flags
                DETACHED_PROCESS = 0x00000008
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                CREATE_NO_WINDOW = 0x08000000
                subprocess.Popen(
                    cmd, 
                    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    close_fds=True
                )
            else:
                # Unix Detached Process
                subprocess.Popen(cmd, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if not self.silent:
                print(f" {C_YLW}[!] Ghost Kernel offline. Waking up Ring -1 daemon...{C_RST}")
        except Exception as e:
            if not self.silent:
                print(f" {C_RED}[!] Failed to auto-launch Ghost: {e}{C_RST}")

    def send(self, command, args=None, branch="main"):
        """Sends a command to the Ghost Kernel and returns the response."""
        if not self.is_connected: return None
        try:
            payload = json.dumps({
                "command": command, 
                "args": args or {},
                "branch": branch
            }).encode('utf-8')
            if os.name == 'nt':
                import win32file
                win32file.WriteFile(self.handle, payload)
                resp, data = win32file.ReadFile(self.handle, 65536)
                return json.loads(data.decode('utf-8'))
            else:
                self.handle.sendall(payload)
                data = self.handle.recv(65536)
                return json.loads(data.decode('utf-8'))
        except Exception:
            return None
        finally:
            if os.name == 'nt':
                import win32file
                win32file.CloseHandle(self.handle)
            else:
                self.handle.close()

def get_active_branch():
    """Reads the active branch from the .mnemos_branch file in the current workspace."""
    branch_file = os.path.join(os.getcwd(), ".mnemos_branch")
    if os.path.exists(branch_file):
        try:
            with open(branch_file, "r") as f:
                return f.read().strip()
        except Exception:
            pass
    return "main"

def set_active_branch(branch_name):
    """Sets the active branch by writing to the .mnemos_branch file."""
    branch_file = os.path.join(os.getcwd(), ".mnemos_branch")
    try:
        with open(branch_file, "w") as f:
            f.write(branch_name)
        return True
    except Exception as e:
        print(f" {C_RED}❌ Error switching branch: {e}{C_RST}")
        return False

def main():
    active_branch = get_active_branch()
    
    # Try to connect to Ghost Kernel for zero-latency
    ghost = GhostBridge()
    if ghost.is_connected:
        # Sync branch state if Ghost is active
        ghost.send("set_branch", {"branch": active_branch})
    
    # Fallback to local core if Ghost isn't running
    mnemo = MnemosCore(branch=active_branch)
    
    parser = argparse.ArgumentParser(description="MNEMOS-OS Command Line Interface")
    subparsers = parser.add_subparsers(dest="command")

    # 1. Add Memory
    add_parser = subparsers.add_parser("add", help="Archive a project fact, decision, or preference")
    add_parser.add_argument("entity")
    add_parser.add_argument("aspect", choices=["PREF", "BUG", "ARCH", "DEP", "LOG", "ANTI"])
    add_parser.add_argument("text")
    add_parser.add_argument("--salience", type=int, default=5)
    add_parser.add_argument("--file")
    add_parser.add_argument("--related", type=int, help="ID of a related memory")

    # 2. Get Context
    ctx_parser = subparsers.add_parser("context", help="Retrieve dense shorthand briefing for AI agents")
    ctx_parser.add_argument("entity")
    ctx_parser.add_argument("--limit", type=int, default=15)

    # 3. Search
    search_parser = subparsers.add_parser("search", help="Search all memories by keyword (FTS5)")
    search_parser.add_argument("query")

    # 4. List
    list_parser = subparsers.add_parser("list", help="Browse stored memories by project")
    list_parser.add_argument("entity", nargs="?")

    # 5. Scratchpad
    scratch_parser = subparsers.add_parser("scratch", help="Set an active multi-step session plan")
    scratch_parser.add_argument("plan")

    # 6. File Context
    file_parser = subparsers.add_parser("file", help="Get context specifically for a code file")
    file_parser.add_argument("path")

    # 7. Purge
    purge_parser = subparsers.add_parser("purge", help="Surgically clean old, low-salience memories")
    purge_parser.add_argument("--days", type=int, default=30)
    purge_parser.add_argument("--min-salience", type=int, default=3)

    # 8. Details (Hydration)
    details_parser = subparsers.add_parser("details", help="Hydrate a shorthand memory into full reasoning")
    details_parser.add_argument("id", type=int)

    # 9. Projects (Discovery)
    subparsers.add_parser("projects", help="List all project entities in the database")

    # 10. Branching (Phase 2)
    branch_parser = subparsers.add_parser("branch", help="List all cognitive branches or create a new one")
    branch_parser.add_argument("name", nargs="?", help="Optional: Name of the new branch to create/list")

    # 11. Checkout (Phase 2)
    checkout_parser = subparsers.add_parser("checkout", help="Switch the active cognitive branch")
    checkout_parser.add_argument("name", help="Name of the branch to switch to")

    # 12. Merge (Phase 2)
    merge_parser = subparsers.add_parser("merge", help="Promote all memories from an experimental branch to main")
    merge_parser.add_argument("source", help="The branch to merge from")
    merge_parser.add_argument("--target", default="main", help="The branch to merge into (default: main)")

    # 13. Delete Branch (Phase 2)
    delete_branch_parser = subparsers.add_parser("delete-branch", help="Delete all memories for a specific branch")
    delete_branch_parser.add_argument("name", help="Name of the branch to delete")

    # 14. Export (v1.2.1)
    export_parser = subparsers.add_parser("export", help="Export memories to a JSON file for portability")
    export_parser.add_argument("file", help="Destination JSON file path")
    export_parser.add_argument("--entity", help="Optional: Filter by project entity")

    # 15. Import (v1.2.1)
    import_parser = subparsers.add_parser("import", help="Import memories from a JSON file")
    import_parser.add_argument("file", help="Source JSON file path")

    # 16. Ghost Kernel (v1.2.1)
    subparsers.add_parser("ghost", help="Launch the Ghost Kernel (Ring -1) zero-latency daemon")

    # 17. Help
    help_parser = subparsers.add_parser("help", help="Show this help message and exit")

    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
        sys.exit(0)

    if args.command == "ghost":
        print(f" {C_BLU}👻 MNEMOS-OS GHOST KERNEL (Ring -1){C_RST}")
        print(f" {C_GRY}Starting zero-latency IPC daemon...{C_RST}")
        from core.ghost import GhostKernel
        try:
            kernel = GhostKernel()
            kernel.start()
        except KeyboardInterrupt:
            print(f"\n {C_RED}[!] Ghost Kernel descending into the void...{C_RST}")
            sys.exit(0)
        except Exception as e:
            print(f" {C_RED}❌ Error launching Ghost Kernel: {e}{C_RST}")
            sys.exit(1)

    if args.command == "add":
        if ghost.is_connected:
            res = ghost.send("add", {
                "entity": args.entity, "aspect": args.aspect, "raw_text": args.text,
                "salience": args.salience, "file_path": args.file, "related_id": args.related
            }, branch=active_branch)
            row_id = res.get("id", -1) if res else -1
        else:
            row_id = mnemo.add_fact(args.entity, args.aspect, args.text, args.salience, file_path=args.file, related_id=args.related)
        
        if row_id == -1:
            print(f" {C_GRY}- Ignored by Salience Filter (too noisy/short){C_RST}")
        else:
            msg = f"Fact saved (ID: {row_id})"
            if args.file: msg += f" linked to {args.file}"
            if args.related: msg += f" related to ID:{args.related}"
            print(f" {C_GRN}[+] {msg}{C_RST}")
    
    elif args.command == "projects":
        if ghost.is_connected:
            res = ghost.send("list_entities")
            entities = res.get("entities", []) if res else []
        else:
            entities = mnemo.list_entities()
            
        if not entities:
            print(f" {C_RED}- No project entities found.{C_RST}")
        else:
            print(f" {C_CYN}KNOWN PROJECT ENTITIES:{C_RST}")
            print(f" {C_MAG}{', '.join(entities)}{C_RST}\n")

    elif args.command == "details":
        if ghost.is_connected:
            res = ghost.send("details", {"memory_id": args.id})
            d = res.get("details") if res else None
        else:
            d = mnemo.get_memory_details(args.id)
            
        if not d:
            print(f" {C_RED}- Memory ID {args.id} not found.{C_RST}")
        else:
            print(f" {C_MAG}--- MEMORY HYDRATION [ID: {args.id}] ---{C_RST}")
            print(f" {C_BLD}ENTITY:{C_RST}  {d['entity']}")
            print(f" {C_BLD}TYPE:{C_RST}    {d['aspect']}")
            print(f" {C_BLD}CREATED:{C_RST} {d['created']}")
            if d['related_id']:
                print(f" {C_BLD}RELATED TO:{C_RST} [ID:{d['related_id']}] {d['related_shorthand']}")
            print(f" {C_CYN}{'-' * 40}{C_RST}")
            print(f" {C_BLD}SHORTHAND:{C_RST} {d['shorthand']}")
            print(f" {C_YLW}--- RAW CONTENT ---{C_RST}")
            print(f" {d['raw']}")
            print(f" {C_MAG}{'-' * 40}{C_RST}\n")

    elif args.command == "context":
        if ghost.is_connected:
            res = ghost.send("context", {"entity": args.entity, "limit": args.limit}, branch=active_branch)
            ctx = res.get("context", "Error retrieving context") if res else "Error"
        else:
            ctx = mnemo.get_context(args.entity, limit=args.limit)
        print(f" {C_MAG}[ACTIVE MINDSET: {args.entity.upper()}]{C_RST}")
        print(f" {C_CYN}{ctx}{C_RST}\n")

    elif args.command == "search":
        if ghost.is_connected:
            res = ghost.send("search", {"query": args.query}, branch=active_branch)
            results = res.get("results", []) if res else []
        else:
            results = mnemo.search(args.query)
            
        if not results:
            print(f" {C_RED}- No matches found.{C_RST}")
        else:
            print(f" {C_CYN}SEARCH RESULTS:{C_RST}")
            print(f" {C_MAG}{'ENTITY':<12} | {'TYPE':<6} | {'SHORTHAND'}{C_RST}")
            print(f" {'-' * 55}")
            for r in results:
                print(f" {C_BLD}{r[0]:<12}{C_RST} | {C_YLW}{r[1]:<6}{C_RST} | {r[2]}")
            print("")

    elif args.command == "list":
        if ghost.is_connected:
            res = ghost.send("list_memories", {"entity": args.entity}, branch=active_branch)
            results = res.get("results", []) if res else []
        else:
            results = mnemo.list_memories(entity=args.entity)
        
        if not results:
            print(f" {C_RED}- Memory is empty.{C_RST}")
        else:
            header = f"ALL MEMORIES:" if not args.entity else f"MEMORIES FOR {args.entity.upper()}:"
            print(f" {C_CYN}{header}{C_RST}")
            print(f" {C_MAG}{'ENTITY':<12} | {'TYPE':<6} | {'S':<2} | {'SHORTHAND'}{C_RST}")
            print(f" {'-' * 55}")
            for r in results:
                print(f" {C_BLD}{str(r[0]):<12}{C_RST} | {C_YLW}{str(r[1]):<6}{C_RST} | {C_RST}{str(r[3]):<2} | {str(r[2])}")
            print("")

    elif args.command == "export":
        count = mnemo.export_json(args.file, entity=args.entity)
        print(f" {C_GRN}✔ Exported {count} memories to '{args.file}'{C_RST}")

    elif args.command == "import":
        count = mnemo.import_json(args.file)
        if count == -1:
            print(f" {C_RED}❌ Import failed: File '{args.file}' not found.{C_RST}")
        else:
            print(f" {C_GRN}✔ Imported {count} memories from '{args.file}'{C_RST}")

    elif args.command == "scratch":
        mnemo.update_scratchpad(args.plan)
        print(f" {C_GRN}✔ Scratchpad updated.{C_RST}")

    elif args.command == "file":
        ctx = mnemo.get_file_context(args.path)
        if ctx:
            print(f" {C_MAG}[FILE CONTEXT: {args.path}]{C_RST}")
            print(f" {C_CYN}{ctx}{C_RST}\n")
        else:
            print(f" {C_YLW}- No specific memories for this file.{C_RST}")
            
    elif args.command == "purge":
        deleted = mnemo.purge_lethe(days=args.days, min_salience=args.min_salience)
        print(f" {C_MAG}🧹 Lethe Protocol: {C_RST}{C_GRN}{deleted} memories purged (>{args.days}d, salience < {args.min_salience}){C_RST}")
    
    elif args.command == "branch":
        with mnemo._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT branch FROM knowledge")
            branches = [row[0] for row in cursor.fetchall()]
            
        active = get_active_branch()
        print(f" {C_CYN}COGNITIVE BRANCHES:{C_RST}")
        for b in branches:
            prefix = f"{C_GRN}* " if b == active else "  "
            print(f" {prefix}{b}{C_RST}")
        
        if args.name and args.name not in branches:
            print(f" {C_YLW}- Branch '{args.name}' is new and will be created on first 'add'.{C_RST}")

    elif args.command == "checkout":
        if set_active_branch(args.name):
            print(f" {C_GRN}✔ Switched to branch '{args.name}'{C_RST}")

    elif args.command == "merge":
        count = mnemo.merge_branch(args.source, args.target)
        print(f" {C_GRN}✔ Merged {count} memories from '{args.source}' into '{args.target}'{C_RST}")

    elif args.command == "delete-branch":
        if args.name == "main":
            print(f" {C_RED}❌ Cannot delete the 'main' branch.{C_RST}")
        else:
            count = mnemo.delete_branch(args.name)
            if get_active_branch() == args.name:
                set_active_branch("main")
            print(f" {C_MAG}🗑  Deleted branch '{args.name}' ({count} memories removed).{C_RST}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
