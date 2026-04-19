# MNEMOS-OS Interactive Terminal
# Copyright (c) 2026 Jonathan Schoenberger
# Licensed under the GNU General Public License v3.0 (GPLv3)
# See LICENSE file for full license text.

import sys
import os
import shlex
from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.engine import MnemosCore
from cli.mnemos import get_console, get_active_branch, set_active_branch
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = get_console()

# Define style matching Gemini CLI aesthetic exactly
mnemos_style = Style.from_dict({
    'branding': 'ansibrightblue bold',
    'version': 'ansigray',
    'gray': 'ansigray',
    'white': 'ansiwhite',
    'magenta': 'ansimagenta',
    'cyan': 'ansicyan',
    'yellow': 'ansiyellow',
    'success': 'ansigreen',
    'error': 'ansired',
    # Completion menu styling
    'completion-menu': 'bg:#222222 #ffffff',
    'completion-menu.completion': 'bg:#222222 #888888',
    'completion-menu.completion.current': 'bg:ansibrightblue #ffffff',
    'completion-menu.meta.completion': 'bg:#222222 #aaaaaa',
    'completion-menu.meta.completion.current': 'bg:ansibrightblue #ffffff',
    # Toolbar styling
    'toolbar': 'ansigray',
    'toolbar.label': 'ansigray',
    'toolbar.value': 'ansiwhite',
})

class MnemosCompleter(Completer):
    def __init__(self):
        self.commands = ['add', 'context', 'scratch', 'file', 'list', 'search', 'purge', 'exit', 'help', 'details', 'projects', 'branch', 'checkout', 'merge', 'delete-branch', 'export', 'import']
        self.aspects = ['PREF', 'BUG', 'ARCH', 'DEP', 'LOG', 'ANTI']
        self.examples = {
            'add': 'Archive a project fact, decision, or preference',
            'details': 'Hydrate a shorthand memory into full reasoning',
            'projects': 'List all project entities in the database',
            'context': 'Retrieve dense shorthand briefing for AI agents',
            'scratch': 'Set an active multi-step session plan',
            'file': 'Get context specifically for a code file',
            'list': 'Browse stored memories by project',
            'search': 'Search all memories by keyword (FTS5)',
            'branch': 'List or create cognitive branches',
            'checkout': 'Switch the active cognitive branch',
            'merge': 'Promote experimental memories to main',
            'delete-branch': 'Surgically remove an experimental branch',
            'export': 'Dump project lore into a JSON file',
            'import': 'Load a technical lore package from JSON',
            'purge': 'Clean stale, low-salience data from Mimir-DB',
            'help': 'View the detailed command guide',
            'exit': 'Securely disconnect from the memory kernel'
        }

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        tokens = text.split()
        
        # Command completion
        if len(tokens) == 0 or (len(tokens) == 1 and not text.endswith(' ')):
            word = tokens[0] if tokens else ""
            for cmd in self.commands:
                if cmd.startswith(word.lower()):
                    yield Completion(cmd + " ", start_position=-len(word), display_meta=self.examples.get(cmd, ""))
        
        # Sub-command/Argument completion
        elif len(tokens) >= 2:
            cmd = tokens[0].lower()
            if cmd == 'add':
                # Suggest aspects for 'add <entity> [HERE]'
                if len(tokens) == 3 and not text.endswith(' '):
                    word = tokens[2]
                    for aspect in self.aspects:
                        if aspect.startswith(word.upper()):
                            yield Completion(aspect + " ", start_position=-len(word))
                elif len(tokens) == 2 and text.endswith(' '):
                    for aspect in self.aspects:
                        yield Completion(aspect + " ", start_position=0)

def main():
    mnemo = MnemosCore()
    history_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", ".history")
    
    session = PromptSession(
        history=FileHistory(history_file),
        completer=MnemosCompleter(),
        auto_suggest=AutoSuggestFromHistory(),
        style=mnemos_style,
        complete_while_typing=True
    )

    def get_toolbar():
        stats = mnemo.get_stats()
        workspace = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return HTML(
            f'<style class="toolbar.label">workspace </style><style class="toolbar.value">~/{workspace}</style>'
            f'          <style class="toolbar.label">stats </style><style class="toolbar.value">{stats["entities"]} entities / {stats["facts"]} facts</style>'
            f'          <style class="toolbar.label">mode </style><style class="toolbar.value">Interactive</style>'
        )

    # 1. Clear Screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # 2. Splash Header
    console.print(f"\n 🧠  [branding]MNEMOS-OS[/branding] [version]v1.2.3[/version]\n")
    console.print(f" [magenta]>[/magenta] [bold]The Memory Kernel for AI[/bold]\n")
    
    warning_box = Panel(
        "MNEMOS-OS is [success]\[active][/success]. Memories are being automatically distilled and indexed\n"
        "into the Mimir-DB. Hard-won knowledge is preserved across all sessions.",
        border_style="yellow",
        title="[warning]SYSTEM STATUS[/warning]",
        expand=False
    )
    console.print(warning_box)
    console.print(f"\n [gray]\[TAB] to autocomplete or ? for Help[/gray]\n")

    while True:
        try:
            # Multi-line prompt for "Input Field" feel with branch indicator
            active_b = get_active_branch()
            
            prompt_msg = [
                ('class:gray', f'┌───( '),
                ('class:branding', 'MNEMOS'),
                ('class:gray', ' )-[ '),
                ('class:magenta', active_b),
                ('class:gray', ' ]\n'),
                ('class:magenta', '└─> '),
            ]

            user_input = session.prompt(
                prompt_msg,
                bottom_toolbar=get_toolbar
            )
            
            if not user_input.strip():
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                # Check if Ghost is running and offer to kill it
                from cli.mnemos import GhostBridge
                ghost = GhostBridge(autostart=False, silent=True)
                if ghost.is_connected:
                    console.print(" [warning]! Ghost Kernel is still active in the background.[/warning]")
                    confirm = session.prompt(HTML(' <white>Shut down the background daemon? (y/N): </white>'))
                    if confirm.lower() == 'y':
                        ghost.send("stop")
                        console.print(" [success]* Ghost Kernel terminated.[/success]")
                break

            try:
                args = shlex.split(user_input)
            except ValueError as e:
                console.print(f" [error][!] Parsing error: {e}[/error]")
                continue

            cmd = args[0].lower()

            if cmd == 'add' and len(args) >= 4:
                entity, aspect, text = args[1], args[2].upper(), args[3]
                salience, file_path, related_id = 5, None, None
                if '--salience' in args:
                    try: salience = int(args[args.index('--salience')+1])
                    except: pass
                if '--file' in args:
                    try: file_path = args[args.index('--file')+1]
                    except: pass
                if '--related' in args:
                    try: related_id = int(args[args.index('--related')+1])
                    except: pass
                
                row_id = mnemo.add_fact(entity, aspect, text, salience, file_path=file_path, related_id=related_id)
                if row_id == -1:
                    console.print(" [gray]- Ignored (Salience Filter)[/gray]")
                else:
                    msg = f"Fact saved (ID: {row_id})"
                    if file_path: msg += f" linked to {file_path}"
                    if related_id: msg += f" related to ID:{related_id}"
                    console.print(f" [success]* {msg}[/success]")

            elif cmd == 'details' and len(args) >= 2:
                try: mem_id = int(args[1])
                except: continue
                d = mnemo.get_memory_details(mem_id)
                if not d:
                    console.print(f" [error]- Memory ID {mem_id} not found.[/error]")
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
                    console.print(Panel(content, title=f"MEMORY HYDRATION [ID: {mem_id}]", border_style="magenta"))

            elif cmd == 'projects':
                entities = mnemo.list_entities()
                if not entities:
                    console.print(" [error]- No project entities found.[/error]")
                else:
                    table = Table(title="KNOWN PROJECT ENTITIES", title_style="info")
                    table.add_column("Entity Name", style="magenta")
                    for ent in entities:
                        table.add_row(ent)
                    console.print(table)

            elif cmd == 'scratch' and len(args) >= 2:
                mnemo.update_scratchpad(args[1])
                console.print(" [success]* Scratchpad updated.[/success]")

            elif cmd == 'file' and len(args) >= 2:
                ctx = mnemo.get_file_context(args[1])
                if ctx:
                    console.print(Panel(Text(ctx, style="info"), title=f"FILE CONTEXT: {args[1]}", border_style="magenta"))
                else:
                    console.print(" [gray]- No specific memories for this file.[/gray]")

            elif cmd == 'context' and len(args) >= 2:
                limit = 15
                if '--limit' in args:
                    try: limit = int(args[args.index('--limit')+1])
                    except: pass
                ctx = mnemo.get_context(args[1], limit=limit)
                console.print(Panel(Text(ctx, style="info"), title=f"ACTIVE MINDSET: {args[1].upper()}", border_style="magenta"))

            elif cmd == 'search' and len(args) >= 2:
                results = mnemo.search(args[1])
                if not results:
                    console.print(" [error]- No matches found.[/error]")
                else:
                    table = Table(title=f"SEARCH RESULTS: {args[1]}", title_style="info")
                    table.add_column("ENTITY", style="bold", width=12)
                    table.add_column("TYPE", style="warning", width=6)
                    table.add_column("SHORTHAND")
                    for r in results:
                        table.add_row(str(r[0]), str(r[1]), str(r[2]))
                    console.print(table)

            elif cmd == 'list':
                entity = args[1] if len(args) >= 2 else None
                results = mnemo.list_memories(entity=entity)
                if not results:
                    console.print(" [error]- Memory is empty.[/error]")
                else:
                    title = "ALL MEMORIES" if not entity else f"MEMORIES FOR {entity.upper()}"
                    table = Table(title=title, title_style="info")
                    table.add_column("ENTITY", style="bold", width=12)
                    table.add_column("TYPE", style="warning", width=6)
                    table.add_column("S", style="gray", width=2)
                    table.add_column("SHORTHAND")
                    for r in results:
                        table.add_row(str(r[0]), str(r[1]), str(r[3]), str(r[2]))
                    console.print(table)

            elif cmd == 'purge':
                days, min_salience = 30, 3
                if '--days' in args:
                    try: days = int(args[args.index('--days')+1])
                    except: pass
                if '--min-salience' in args:
                    try: min_salience = int(args[args.index('--min-salience')+1])
                    except: pass
                
                deleted = mnemo.purge_lethe(days=days, min_salience=min_salience)
                console.print(f" [magenta]* Purged {deleted} memories (older than {days} days, salience < {min_salience}).[/magenta]")

            elif cmd == 'branch':
                with mnemo.conn:
                    cursor = mnemo.conn.cursor()
                    cursor.execute("SELECT DISTINCT branch FROM knowledge")
                    branches = [row[0] for row in cursor.fetchall()]
                
                active = get_active_branch()
                console.print("\n [info]COGNITIVE BRANCHES:[/info]")
                for b in branches:
                    prefix = "[success]* [/success]" if b == active else "  "
                    console.print(f" {prefix}{b}")
                console.print("")

            elif cmd == 'checkout' and len(args) >= 2:
                if set_active_branch(args[1]):
                    mnemo.set_branch(args[1])
                    console.print(f" [success]* Switched to branch \"{args[1]}\"[/success]")

            elif cmd == 'merge' and len(args) >= 2:
                source = args[1]
                target = 'main'
                if '--target' in args:
                    try: target = args[args.index('--target')+1]
                    except: pass
                count = mnemo.merge_branch(source, target)
                console.print(f" [success]* Merged {count} memories from \"{source}\" into \"{target}\"[/success]")

            elif cmd == 'delete-branch' and len(args) >= 2:
                name = args[1]
                if name == 'main':
                    console.print(" [error][!] Cannot delete the \"main\" branch.[/error]")
                else:
                    count = mnemo.delete_branch(name)
                    if get_active_branch() == name:
                        set_active_branch('main')
                        mnemo.set_branch('main')
                    console.print(f" [magenta]* Deleted branch \"{name}\" ({count} memories removed).[/magenta]")

            elif cmd == 'export' and len(args) >= 2:
                file_path = args[1]
                entity = None
                if '--entity' in args:
                    try: entity = args[args.index('--entity')+1]
                    except: pass
                count = mnemo.export_json(file_path, entity=entity)
                console.print(f" [success]* Exported {count} memories to \"{file_path}\"[/success]")

            elif cmd == 'import' and len(args) >= 2:
                file_path = args[1]
                count = mnemo.import_json(file_path)
                if count == -1:
                    console.print(f" [error][!] Import failed: File \"{file_path}\" not found.[/error]")
                else:
                    console.print(f" [success]* Imported {count} memories from \"{file_path}\"[/success]")

            elif cmd == 'help' or cmd == '?':
                guide = f"[magenta]--- MNEMOS COMMAND GUIDE ---[/magenta]\n"
                guide += "  [warning]add <entity> <aspect> \"text\"[/warning]\n"
                guide += "    [gray]Archive a key project fact, architectural decision, or user preference.[/gray]\n"
                guide += "    [gray]Optional: --salience 1-10, --file path, --related ID[/gray]\n\n"
                guide += "  [warning]details <ID>[/warning]\n"
                guide += "    [gray]Hydrate a shorthand memory into full reasoning and see logic links.[/gray]\n\n"
                guide += "  [warning]projects[/warning]\n"
                guide += "    [gray]List all project entities (knowledge bases) in the system.[/gray]\n\n"
                guide += "  [warning]context <entity>[/warning]\n"
                guide += "    [gray]Retrieve a dense shorthand briefing of project context for an AI.[/gray]\n\n"
                guide += "  [warning]scratch \"your plan\"[/warning]\n"
                guide += "    [gray]Update the active multi-step session plan for task continuity.[/gray]\n\n"
                guide += "  [warning]file \"path/to/file\"[/warning]\n"
                guide += "    [gray]Retrieve memories linked specifically to a code file.[/gray]\n\n"
                guide += "  [warning]search \"query\"[/warning]\n"
                guide += "    [gray]Find memories matching keywords using high-speed FTS5.[/gray]\n\n"
                guide += "  [warning]list [entity][/warning]\n"
                guide += "    [gray]Browse all stored memories, optionally filtered by project.[/gray]\n\n"
                guide += "  [warning]branch[/warning]\n"
                guide += "    [gray]List all known cognitive branches.[/gray]\n\n"
                guide += "  [warning]checkout <name>[/warning]\n"
                guide += "    [gray]Switch the active cognitive branch context.[/gray]\n\n"
                guide += "  [warning]merge <source> [--target main][/warning]\n"
                guide += "    [gray]Promote experimental memories to the stable main bank.[/gray]\n\n"
                guide += "  [warning]delete-branch <name>[/warning]\n"
                guide += "    [gray]Surgically remove an experimental branch and its facts.[/gray]\n\n"
                guide += "  [warning]export <file> [--entity name][/warning]\n"
                guide += "    [gray]Dump project lore into a structured JSON file for sharing.[/gray]\n\n"
                guide += "  [warning]import <file>[/warning]\n"
                guide += "    [gray]Import a lore package into the Mimir-DB.[/gray]\n\n"
                guide += "  [warning]purge [--days N] [--min-salience N][/warning]\n"
                guide += "    [gray]Surgically clean old, low-salience memories from the DB.[/gray]\n\n"
                guide += "  [error]exit[/error] or [error]quit[/error]\n"
                guide += "    [gray]Securely disconnect from the memory kernel.[/gray]"
                console.print(guide)
            
            else:
                if cmd not in ['add', 'context', 'search', 'purge', 'scratch', 'file', 'list', 'branch', 'checkout', 'merge', 'delete-branch', 'export', 'import']:
                    console.print(" [error][!] Unknown command. Type \"help\" for info.[/error]")
                else:
                    console.print(f" [error][!] Missing arguments for \"{cmd}\".[/error]")

        except KeyboardInterrupt:
            print("")
            continue
        except EOFError:
            break
        except Exception as e:
            console.print(f" [error][!] Error: {e}[/error]")

if __name__ == "__main__":
    main()
