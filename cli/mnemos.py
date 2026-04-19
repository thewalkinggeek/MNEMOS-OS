# MNEMOS-OS Script Interface (Non-Interactive)
# Copyright © 2026 Jonathan Schoenberger
# Licensed under the GNU General Public License v3.0 (GPLv3)
# See LICENSE file for full license text.

import sys
import os
import argparse
import json
import socket
import time
import hashlib

# Add the parent directory to sys.path so we can import core.engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import MnemosCore
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

def get_console():
    """Returns a Rich console with the MNEMOS-OS theme."""
    return Console(theme=Theme({
        "branding": "bright_blue bold",
        "version": "grey50",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "info": "cyan",
        "magenta": "bright_magenta",
        "gray": "grey50",
        "bold": "bold",
    }))

console = get_console()

class GhostBridge:
    """Zero-latency bridge to the Ghost Kernel daemon."""
    def __init__(self, autostart=True, silent=False):
        self.is_connected = False
        self.silent = silent
        
        # Calculate unique IPC name for this workspace
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        workspace_hash = hashlib.md5(base_dir.encode('utf-8')).hexdigest()[:8]
        
        if os.name == 'nt':
            self.pipe_name = fr'\\.\pipe\mnemos_ghost_{workspace_hash}'
        else:
            self.pipe_name = f'/tmp/mnemos_ghost_{workspace_hash}.sock'
        
        # FAILSAFE: Never autostart if we are already attempting to launch the ghost
        if len(sys.argv) > 1 and sys.argv[1].lower() == "ghost":
            autostart = False
            
        self._connect()
        if not self.is_connected and autostart and os.environ.get("MNEMOS_NO_AUTOSTART") != "1":
            self.launch_ghost()
            # Wait briefly for the daemon to initialize the IPC channel
            time.sleep(1.5)
            self._connect()

    def _connect(self):
        try:
            if os.name == 'nt':
                import win32file
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
                CREATE_NO_WINDOW = 0x08000000
                subprocess.Popen(
                    cmd, 
                    creationflags=CREATE_NO_WINDOW, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    close_fds=True
                )
            else:
                subprocess.Popen(cmd, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if not self.silent:
                console.print(f" [warning][!] Ghost Kernel offline. Waking up Ring -1 daemon...[/warning]")
        except Exception as e:
            if not self.silent:
                console.print(f" [error][!] Failed to auto-launch Ghost: {e}[/error]")

    def send(self, command, args=None, branch="main"):
        """Sends a command to the Ghost Kernel and returns the response."""
        self._connect()
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
            try:
                if os.name == 'nt':
                    import win32file
                    win32file.CloseHandle(self.handle)
                else:
                    self.handle.close()
            except: pass
            self.is_connected = False

def get_active_branch():
    """Reads the active branch from the .mnemos_branch file."""
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
        console.print(f" [error]❌ Error switching branch: {e}[/error]")
        return False

def main():
    parser = argparse.ArgumentParser(description="MNEMOS-OS Command Line Interface")
    subparsers = parser.add_subparsers(dest="command")

    # Command Definitions
    add_parser = subparsers.add_parser("add", help="Archive a project fact, decision, or preference")
    add_parser.add_argument("entity")
    add_parser.add_argument("aspect", choices=["PREF", "BUG", "ARCH", "DEP", "LOG", "ANTI"])
    add_parser.add_argument("text")
    add_parser.add_argument("--salience", type=int, default=5)
    add_parser.add_argument("--file")
    add_parser.add_argument("--related", type=int, help="ID of a related memory")

    ctx_parser = subparsers.add_parser("context", help="Retrieve dense shorthand briefing for AI agents")
    ctx_parser.add_argument("entity")
    ctx_parser.add_argument("--limit", type=int, default=15)

    search_parser = subparsers.add_parser("search", help="Search all memories by keyword (FTS5)")
    search_parser.add_argument("query")

    list_parser = subparsers.add_parser("list", help="Browse stored memories by project")
    list_parser.add_argument("entity", nargs="?")

    subparsers.add_parser("scratch", help="Set an active multi-step session plan").add_argument("plan")
    subparsers.add_parser("file", help="Get context specifically for a code file").add_argument("path")

    purge_parser = subparsers.add_parser("purge", help="Surgically clean old, low-salience memories")
    purge_parser.add_argument("--days", type=int, default=30)
    purge_parser.add_argument("--min-salience", type=int, default=3)

    subparsers.add_parser("details", help="Hydrate a shorthand memory into full reasoning").add_argument("id", type=int)
    subparsers.add_parser("projects", help="List all project entities in the database")

    branch_parser = subparsers.add_parser("branch", help="List or create cognitive branches")
    branch_parser.add_argument("name", nargs="?")

    subparsers.add_parser("checkout", help="Switch the active branch").add_argument("name")
    
    merge_parser = subparsers.add_parser("merge", help="Promote memories from one branch to another")
    merge_parser.add_argument("source")
    merge_parser.add_argument("--target", default="main")

    subparsers.add_parser("delete-branch", help="Delete a specific branch").add_argument("name")

    export_parser = subparsers.add_parser("export", help="Export memories to JSON")
    export_parser.add_argument("file")
    export_parser.add_argument("--entity")

    subparsers.add_parser("import", help="Import memories from JSON").add_argument("file")
    subparsers.add_parser("ghost", help="Launch the Ghost Kernel daemon")
    subparsers.add_parser("stop", help="Terminate the Ghost Kernel daemon")
    subparsers.add_parser("ping", help="Verify Ghost Kernel status")
    subparsers.add_parser("help", help="Show this help message")

    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
        sys.exit(0)

    if args.command == "ghost":
        console.print(f"\n [branding]👻 MNEMOS-OS GHOST KERNEL (Ring -1)[/branding]")
        console.print(f" [gray]Starting zero-latency IPC daemon...[/gray]")
        from core.ghost import GhostKernel
        try:
            kernel = GhostKernel()
            kernel.start()
        except KeyboardInterrupt:
            console.print(f"\n [error][!] Ghost Kernel descending into the void...[/error]")
            sys.exit(0)
        except Exception as e:
            console.print(f" [error]❌ Error launching Ghost Kernel: {e}[/error]")
            sys.exit(1)

    active_branch = get_active_branch()
    ghost = GhostBridge()
    mnemo = MnemosCore(branch=active_branch)

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
            console.print(f" [gray]- Ignored by Salience Filter (too noisy/short)[/gray]")
        else:
            msg = f"Fact saved (ID: {row_id})"
            if args.file: msg += f" linked to {args.file}"
            if args.related: msg += f" related to ID:{args.related}"
            console.print(f" [success][+] {msg}[/success]")
    
    elif args.command == "projects":
        if ghost.is_connected:
            res = ghost.send("list_entities")
            entities = res.get("entities", []) if res else []
        else:
            entities = mnemo.list_entities()
            
        if not entities:
            console.print(f" [error]- No project entities found.[/error]")
        else:
            table = Table(title="KNOWN PROJECT ENTITIES", title_style="info")
            table.add_column("Entity Name", style="magenta")
            for ent in entities:
                table.add_row(ent)
            console.print(table)

    elif args.command == "details":
        if ghost.is_connected:
            res = ghost.send("details", {"memory_id": args.id})
            d = res.get("details") if res else None
        else:
            d = mnemo.get_memory_details(args.id)
            
        if not d:
            console.print(f" [error]- Memory ID {args.id} not found.[/error]")
        else:
            content = f"[bold]ENTITY:[/bold]  {d['entity']}\n"
            content += f"[bold]TYPE:[/bold]    {d['aspect']}\n"
            content += f"[bold]CREATED:[/bold] {d['created']}\n"
            if d['related_id']:
                content += f"[bold]RELATED:[/bold] [ID:{d['related_id']}] {d['related_shorthand']}\n"
            content += "\n[info]SHORTHAND:[/info]\n"
            content += f"{d['shorthand']}\n"
            content += "\n[warning]--- RAW CONTENT ---[/warning]\n"
            content += f"{d['raw']}"
            
            console.print(Panel(content, title=f"MEMORY HYDRATION [ID: {args.id}]", border_style="magenta"))

    elif args.command == "context":
        if ghost.is_connected:
            res = ghost.send("context", {"entity": args.entity, "limit": args.limit}, branch=active_branch)
            ctx = res.get("context", "Error retrieving context") if res else "Error"
        else:
            ctx = mnemo.get_context(args.entity, limit=args.limit)
        
        console.print(Panel(Text(ctx, style="info"), title=f"ACTIVE MINDSET: {args.entity.upper()}", border_style="magenta"))

    elif args.command == "search":
        if ghost.is_connected:
            res = ghost.send("search", {"query": args.query}, branch=active_branch)
            results = res.get("results", []) if res else []
        else:
            results = mnemo.search(args.query)
            
        if not results:
            console.print(f" [error]- No matches found for '{args.query}'.[/error]")
        else:
            table = Table(title=f"SEARCH RESULTS: {args.query}", title_style="info")
            table.add_column("ENTITY", style="bold", width=12)
            table.add_column("TYPE", style="warning", width=6)
            table.add_column("SHORTHAND")
            for r in results:
                table.add_row(r[0], r[1], r[2])
            console.print(table)

    elif args.command == "list":
        if ghost.is_connected:
            res = ghost.send("list_memories", {"entity": args.entity}, branch=active_branch)
            results = res.get("results", []) if res else []
        else:
            results = mnemo.list_memories(entity=args.entity)
        
        if not results:
            console.print(f" [error]- Memory is empty.[/error]")
        else:
            title = "ALL MEMORIES" if not args.entity else f"MEMORIES FOR {args.entity.upper()}"
            table = Table(title=title, title_style="info")
            table.add_column("ENTITY", style="bold", width=12)
            table.add_column("TYPE", style="warning", width=6)
            table.add_column("S", style="gray", width=2)
            table.add_column("SHORTHAND")
            for r in results:
                table.add_row(str(r[0]), str(r[1]), str(r[3]), str(r[2]))
            console.print(table)

    elif args.command == "export":
        count = mnemo.export_json(args.file, entity=args.entity)
        console.print(f" [success]✔ Exported {count} memories to '{args.file}'[/success]")

    elif args.command == "import":
        count = mnemo.import_json(args.file)
        if count == -1:
            console.print(f" [error]❌ Import failed: File '{args.file}' not found.[/error]")
        else:
            console.print(f" [success]✔ Imported {count} memories from '{args.file}'[/success]")

    elif args.command == "scratch":
        mnemo.update_scratchpad(args.plan)
        console.print(f" [success]✔ Scratchpad updated.[/success]")

    elif args.command == "file":
        ctx = mnemo.get_file_context(args.path)
        if ctx:
            console.print(Panel(Text(ctx, style="info"), title=f"FILE CONTEXT: {args.path}", border_style="magenta"))
        else:
            console.print(f" [warning]- No specific memories for this file.[/warning]")
            
    elif args.command == "purge":
        deleted = mnemo.purge_lethe(days=args.days, min_salience=args.min_salience)
        console.print(f" [magenta]🧹 Lethe Protocol: [success]{deleted} memories purged (>{args.days}d, salience < {args.min_salience})[/success][/magenta]")
    
    elif args.command == "branch":
        with mnemo._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT branch FROM knowledge")
            branches = [row[0] for row in cursor.fetchall()]
            
        active = get_active_branch()
        console.print(f"\n [info]COGNITIVE BRANCHES:[/info]")
        for b in branches:
            prefix = "[success]* [/success]" if b == active else "  "
            console.print(f" {prefix}{b}")
        
        if args.name and args.name not in branches:
            console.print(f" [warning]- Branch '{args.name}' is new and will be created on first 'add'.[/warning]")

    elif args.command == "checkout":
        if set_active_branch(args.name):
            console.print(f" [success]✔ Switched to branch '{args.name}'[/success]")

    elif args.command == "merge":
        count = mnemo.merge_branch(args.source, args.target)
        console.print(f" [success]✔ Merged {count} memories from '{args.source}' into '{args.target}'[/success]")

    elif args.command == "delete-branch":
        if args.name == "main":
            console.print(f" [error]❌ Cannot delete the 'main' branch.[/error]")
        else:
            count = mnemo.delete_branch(args.name)
            if get_active_branch() == args.name:
                set_active_branch("main")
            console.print(f" [magenta]🗑  Deleted branch '{args.name}' ({count} memories removed).[/magenta]")
    
    elif args.command == "stop":
        if ghost.is_connected:
            ghost.send("stop")
            console.print(f" [magenta]👻 Ghost Kernel descending into the void...[/magenta]")
        else:
            console.print(f" [gray]- Ghost Kernel is already offline.[/gray]")

    elif args.command == "ping":
        if ghost.is_connected:
            res = ghost.send("ping")
            status = res.get("status", "unknown")
            version = res.get("version", "?.?.?")
            console.print(f" [success][✔] Ghost Kernel: {status.upper()} (v{version})[/success]")
        else:
            console.print(f" [error][!] Ghost Kernel: OFFLINE[/error]")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
