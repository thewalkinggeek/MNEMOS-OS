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
            f'<style class="toolbar.label">workspace (/directory) </style><style class="toolbar.value">~/{workspace}</style>'
            f'          <style class="toolbar.label">stats </style><style class="toolbar.value">{stats["entities"]} entities / {stats["facts"]} facts</style>'
            f'          <style class="toolbar.label">/mode </style><style class="toolbar.value">Interactive</style>'
        )

    # 1. Clear Screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # 2. Splash Header (Fixed tag names to match style keys)
    print_formatted_text(HTML('\n 🧠  <branding>MNEMOS-OS</branding> <version>v1.2.2</version>\n'), style=mnemos_style)
    print_formatted_text(HTML(' <magenta>&gt;</magenta> <white><b>The Memory Kernel for AI</b></white>\n'), style=mnemos_style)
    print_formatted_text(HTML(' <gray>----------------------------------</gray>\n'), style=mnemos_style)
    
    # Yellow warning box
    print_formatted_text(HTML(' <style color="ansiyellow">┌──────────────────────────────────────────────────────────────────────────┐</style>'), style=mnemos_style)
    print_formatted_text(HTML(' <style color="ansiyellow">│ MNEMOS-OS is active. Memories are being automatically distilled and indexed │</style>'), style=mnemos_style)
    print_formatted_text(HTML(' <style color="ansiyellow">│ into the Mimir-DB. Hard-won knowledge is preserved across all sessions.  │</style>'), style=mnemos_style)
    print_formatted_text(HTML(' <style color="ansiyellow">└──────────────────────────────────────────────────────────────────────────┘</style>\n'), style=mnemos_style)

    print_formatted_text(HTML(' <gray>[TAB] to autocomplete or ? for Help</gray>\n'), style=mnemos_style)

    while True:
        try:
            # Minimalist prompt: Blue branding + Magenta >
            user_input = session.prompt(
                HTML('<magenta>&gt;</magenta> '),
                bottom_toolbar=get_toolbar
            )
            
            if not user_input.strip():
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                # Check if Ghost is running and offer to kill it
                from cli.mnemos import GhostBridge
                ghost = GhostBridge(autostart=False, silent=True)
                if ghost.is_connected:
                    print_formatted_text(HTML(' <yellow>! Ghost Kernel is still active in the background.</yellow>'), style=mnemos_style)
                    confirm = session.prompt(HTML(' <white>Shut down the background daemon? (y/N): </white>'))
                    if confirm.lower() == 'y':
                        ghost.send("stop")
                        print_formatted_text(HTML(' <success>* Ghost Kernel terminated.</success>'), style=mnemos_style)
                break

            try:
                args = shlex.split(user_input)
            except ValueError as e:
                print_formatted_text(HTML(f' <error>[!] Parsing error: {e}</error>'), style=mnemos_style)
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
                    print_formatted_text(HTML(' <gray>- Ignored (Salience Filter)</gray>'), style=mnemos_style)
                else:
                    msg = f"Fact saved (ID: {row_id})"
                    if file_path: msg += f" linked to {file_path}"
                    if related_id: msg += f" related to ID:{related_id}"
                    print_formatted_text(HTML(f' <success>* {msg}</success>'), style=mnemos_style)

            elif cmd == 'details' and len(args) >= 2:
                try: mem_id = int(args[1])
                except: continue
                d = mnemo.get_memory_details(mem_id)
                if not d:
                    print_formatted_text(HTML(f' <error>- Memory ID {mem_id} not found.</error>'), style=mnemos_style)
                else:
                    print_formatted_text(HTML(f'\n <magenta>--- MEMORY HYDRATION [ID: {mem_id}] ---</magenta>'), style=mnemos_style)
                    print_formatted_text(HTML(f' <b>ENTITY:</b>  {d["entity"]}'), style=mnemos_style)
                    print_formatted_text(HTML(f' <b>TYPE:</b>    {d["aspect"]}'), style=mnemos_style)
                    print_formatted_text(HTML(f' <b>CREATED:</b> {d["created"]}'), style=mnemos_style)
                    if d['related_id']:
                        print_formatted_text(HTML(f" <b>RELATED:</b> [ID:{d['related_id']}] {d['related_shorthand']}"), style=mnemos_style)
                    print_formatted_text(HTML(f' <gray>{"-" * 40}</gray>'), style=mnemos_style)
                    print_formatted_text(HTML(f' <b>SHORTHAND:</b> {d["shorthand"]}'), style=mnemos_style)
                    print_formatted_text(HTML(f' <yellow>--- RAW CONTENT ---</yellow>'), style=mnemos_style)
                    print_formatted_text(HTML(f' {d["raw"]}'), style=mnemos_style)
                    print_formatted_text(HTML(f' <magenta>{"-" * 40}</magenta>\n'), style=mnemos_style)

            elif cmd == 'projects':
                entities = mnemo.list_entities()
                if not entities:
                    print_formatted_text(HTML(' <error>- No project entities found.</error>'), style=mnemos_style)
                else:
                    print_formatted_text(HTML(f'\n <cyan>KNOWN PROJECT ENTITIES:</cyan>'), style=mnemos_style)
                    print_formatted_text(HTML(f' <magenta>{", ".join(entities)}</magenta>\n'), style=mnemos_style)

            elif cmd == 'scratch' and len(args) >= 2:
                mnemo.update_scratchpad(args[1])
                print_formatted_text(HTML(' <success>* Scratchpad updated.</success>'), style=mnemos_style)

            elif cmd == 'file' and len(args) >= 2:
                ctx = mnemo.get_file_context(args[1])
                if ctx:
                    print_formatted_text(HTML(f'\n <magenta>[FILE CONTEXT: {args[1]}]</magenta>'), style=mnemos_style)
                    print_formatted_text(HTML(f' <cyan>{ctx}</cyan>\n'), style=mnemos_style)
                else:
                    print_formatted_text(HTML(' <gray>- No specific memories for this file.</gray>'), style=mnemos_style)

            elif cmd == 'context' and len(args) >= 2:
                limit = 15
                if '--limit' in args:
                    try: limit = int(args[args.index('--limit')+1])
                    except: pass
                ctx = mnemo.get_context(args[1], limit=limit)
                print_formatted_text(HTML(f'\n <magenta>[ACTIVE MINDSET: {args[1].upper()}]</magenta>'), style=mnemos_style)
                print_formatted_text(HTML(f' <cyan>{ctx}</cyan>\n'), style=mnemos_style)

            elif cmd == 'search' and len(args) >= 2:
                results = mnemo.search(args[1])
                if not results:
                    print_formatted_text(HTML(' <error>- No matches</error>'), style=mnemos_style)
                else:
                    print_formatted_text(HTML(f'\n <cyan>SEARCH RESULTS:</cyan>'), style=mnemos_style)
                    for r in results:
                        ent, asp, short = str(r[0]), str(r[1]), str(r[2])
                        header = f"{ent:<12} | {asp:<6} |"
                        print_formatted_text(HTML(f' <gray>{header}</gray> {short}'), style=mnemos_style)
                    print("")

            elif cmd == 'list':
                entity = args[1] if len(args) >= 2 else None
                results = mnemo.list_memories(entity=entity)
                if not results:
                    print_formatted_text(HTML(' <error>- Memory is empty.</error>'), style=mnemos_style)
                else:
                    header_txt = f"ALL MEMORIES:" if not entity else f"MEMORIES FOR {entity.upper()}:"
                    print_formatted_text(HTML(f'\n <cyan>{header_txt}</cyan>'), style=mnemos_style)
                    print_formatted_text(HTML(f' <magenta>ENTITY       | TYPE   | S  | SHORTHAND</magenta>'), style=mnemos_style)
                    print_formatted_text(HTML(f' <gray>{"-" * 55}</gray>'), style=mnemos_style)
                    for r in results:
                        ent, asp, short, sal = str(r[0]), str(r[1]), str(r[2]), str(r[3])
                        row_head = f"{ent:<12} | {asp:<6} | {sal:<2} |"
                        print_formatted_text(HTML(f' <gray>{row_head}</gray> {short}'), style=mnemos_style)
                    print("")

            elif cmd == 'purge':
                days, min_salience = 30, 3
                if '--days' in args:
                    try: days = int(args[args.index('--days')+1])
                    except: pass
                if '--min-salience' in args:
                    try: min_salience = int(args[args.index('--min-salience')+1])
                    except: pass
                
                deleted = mnemo.purge_lethe(days=days, min_salience=min_salience)
                print_formatted_text(HTML(f' <magenta>* Purged {deleted} memories (older than {days} days, salience &lt; {min_salience}).</magenta>'), style=mnemos_style)

            elif cmd == 'branch':
                with mnemo.conn:
                    cursor = mnemo.conn.cursor()
                    cursor.execute("SELECT DISTINCT branch FROM knowledge")
                    branches = [row[0] for row in cursor.fetchall()]
                
                from cli.mnemos import get_active_branch
                active = get_active_branch()
                print_formatted_text(HTML(f'\n <cyan>COGNITIVE BRANCHES:</cyan>'), style=mnemos_style)
                for b in branches:
                    prefix = HTML('<success>* </success>') if b == active else '  '
                    print_formatted_text(HTML(f' {prefix}{b}'), style=mnemos_style)
                print("")

            elif cmd == 'checkout' and len(args) >= 2:
                from cli.mnemos import set_active_branch
                if set_active_branch(args[1]):
                    mnemo.set_branch(args[1])
                    print_formatted_text(HTML(f' <success>* Switched to branch "{args[1]}"</success>'), style=mnemos_style)

            elif cmd == 'merge' and len(args) >= 2:
                source = args[1]
                target = 'main'
                if '--target' in args:
                    try: target = args[args.index('--target')+1]
                    except: pass
                count = mnemo.merge_branch(source, target)
                print_formatted_text(HTML(f' <success>* Merged {count} memories from "{source}" into "{target}"</success>'), style=mnemos_style)

            elif cmd == 'delete-branch' and len(args) >= 2:
                name = args[1]
                if name == 'main':
                    print_formatted_text(HTML(' <error>[!] Cannot delete the "main" branch.</error>'), style=mnemos_style)
                else:
                    count = mnemo.delete_branch(name)
                    from cli.mnemos import get_active_branch, set_active_branch
                    if get_active_branch() == name:
                        set_active_branch('main')
                        mnemo.set_branch('main')
                    print_formatted_text(HTML(f' <magenta>* Deleted branch "{name}" ({count} memories removed).</magenta>'), style=mnemos_style)

            elif cmd == 'export' and len(args) >= 2:
                file_path = args[1]
                entity = None
                if '--entity' in args:
                    try: entity = args[args.index('--entity')+1]
                    except: pass
                count = mnemo.export_json(file_path, entity=entity)
                print_formatted_text(HTML(f' <success>* Exported {count} memories to "{file_path}"</success>'), style=mnemos_style)

            elif cmd == 'import' and len(args) >= 2:
                file_path = args[1]
                count = mnemo.import_json(file_path)
                if count == -1:
                    print_formatted_text(HTML(f' <error>[!] Import failed: File "{file_path}" not found.</error>'), style=mnemos_style)
                else:
                    print_formatted_text(HTML(f' <success>* Imported {count} memories from "{file_path}"</success>'), style=mnemos_style)

            elif cmd == 'help' or cmd == '?':
                print_formatted_text(HTML(f'\n <magenta>--- MNEMOS COMMAND GUIDE ---</magenta>'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>add &lt;entity&gt; &lt;aspect&gt; "text"</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Archive a key project fact, architectural decision, or user preference.</gray>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Optional: --salience 1-10, --file path, --related ID</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>details &lt;ID&gt;</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Hydrate a shorthand memory into full reasoning and see logic links.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>projects</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>List all project entities (knowledge bases) in the system.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>context &lt;entity&gt;</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Retrieve a dense shorthand briefing of project context for an AI.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>scratch "your plan"</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Update the active multi-step session plan for task continuity.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>file "path/to/file"</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Retrieve memories linked specifically to a code file.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>search "query"</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Find memories matching keywords using high-speed FTS5.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>list [entity]</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Browse all stored memories, optionally filtered by project.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>branch</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>List all known cognitive branches.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>checkout &lt;name&gt;</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Switch the active cognitive branch context.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>merge &lt;source&gt; [--target main]</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Promote experimental memories to the stable main bank.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>delete-branch &lt;name&gt;</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Surgically remove an experimental branch and its facts.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>export &lt;file&gt; [--entity name]</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Dump project lore into a structured JSON file for sharing.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>import &lt;file&gt;</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Import a lore package into the Mimir-DB.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <yellow>purge [--days N] [--min-salience N]</yellow>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Surgically clean old, low-salience memories from the DB.</gray>\n'), style=mnemos_style)
                print_formatted_text(HTML(f'  <error>exit</error> or <error>quit</error>'), style=mnemos_style)
                print_formatted_text(HTML(f'    <gray>Securely disconnect from the memory kernel.</gray>\n'), style=mnemos_style)
            
            else:
                if cmd not in ['add', 'context', 'search', 'purge', 'scratch', 'file', 'list', 'branch', 'checkout', 'merge', 'delete-branch', 'export', 'import']:
                    print_formatted_text(HTML(f' <error>[!] Unknown command. Type "help" for info.</error>'), style=mnemos_style)
                else:
                    print_formatted_text(HTML(f' <error>[!] Missing arguments for "{cmd}".</error>'), style=mnemos_style)

        except KeyboardInterrupt:
            print("")
            continue
        except EOFError:
            break
        except Exception as e:
            print_formatted_text(HTML(f' <error>[!] Error: {e}</error>'), style=mnemos_style)

if __name__ == "__main__":
    main()
