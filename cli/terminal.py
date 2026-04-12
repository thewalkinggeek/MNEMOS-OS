# MNEMOS-OS Interactive Terminal
# Copyright (c) 2026 Jonathan Schoenberger
# Licensed under the MIT License

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
    'branding': '#4285f4 bold',
    'version': '#909090',
    'gray': '#909090',
    'white': '#ffffff',
    'magenta': '#ff00ff',
    'cyan': '#00ffff',
    'success': '#00ff00',
    'error': '#ff4444 bg:default', # Explicitly no background
    # Completion menu styling (Modern Dark)
    'completion-menu': 'bg:#222222 #ffffff',
    'completion-menu.completion': 'bg:#222222 #888888',
    'completion-menu.completion.current': 'bg:#4285f4 #ffffff',
    'completion-menu.meta.completion': 'bg:#222222 #aaaaaa',
    'completion-menu.meta.completion.current': 'bg:#4285f4 #ffffff',
    # Toolbar styling
    'toolbar': 'bg:#000000 #909090',
    'toolbar.label': '#909090',
    'toolbar.value': '#ffffff',
    'toolbar.branding': '#4285f4 bold',
})

class MnemosCompleter(Completer):
    def __init__(self):
        # Priority order: Core operations first, utilities last
        self.commands = ['add', 'context', 'scratch', 'file', 'list', 'search', 'purge', 'menu', 'help', 'exit']
        self.aspects = ['PREF', 'BUG', 'ARCH', 'DEP', 'LOG', 'ANTI']
        self.examples = {
            'add': 'Archive a project fact, decision, or preference',
            'context': 'Retrieve dense shorthand briefing for AI agents',
            'scratch': 'Set an active multi-step session plan',
            'file': 'Get context specifically for a code file',
            'list': 'Browse stored memories by project',
            'search': 'Search all memories by keyword (FTS5)',
            'purge': 'Clean stale, low-salience data from Mimir-DB',
            'menu': 'Return to the main launcher menu',
            'help': 'View the detailed command guide',
            'exit': 'Securely disconnect from the memory kernel'
        }

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        tokens = text.split()
        
        if len(tokens) <= 1 and not text.endswith(' '):
            word = tokens[0] if tokens else ""
            for cmd in self.commands:
                if cmd.startswith(word):
                    yield Completion(cmd + " ", start_position=-len(word), display_meta=self.examples.get(cmd, ""))
        
        elif len(tokens) >= 2:
            cmd = tokens[0].lower()
            if cmd == 'add':
                if len(tokens) == 3 and not text.endswith(' '):
                    word = tokens[2]
                    for aspect in self.aspects:
                        if aspect.startswith(word.upper()):
                            yield Completion(aspect + " ", start_position=-len(word))

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
            f'<branding>Mnemos-OS</branding> '
            f'<style class="toolbar.label">workspace </style><style class="toolbar.value">~/{workspace}</style>'
            f'          <style class="toolbar.label">stats </style><style class="toolbar.value">{stats["entities"]} entities / {stats["facts"]} facts</style>'
            f'          <style class="toolbar.label">/mode </style><style class="toolbar.value">Interactive</style>'
        )

    # 1. Clear Screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # 2. Splash Header (Uniform)
    print_formatted_text(HTML('\n 🧠  <branding>Mnemos-OS</branding> <version>v1.0.0</version>\n'))
    print_formatted_text(HTML(' <magenta>&gt;</magenta> <white><b>The Memory Kernel for AI</b></white>\n'))
    print_formatted_text(HTML(' <gray>----------------------------------</gray>\n'))
    
    print_formatted_text(HTML(' <style bg="#333300" color="#ffff00">┌──────────────────────────────────────────────────────────────────────────┐</style>'))
    print_formatted_text(HTML(' <style bg="#333300" color="#ffff00">│ MNEMOS is active. Memories are being automatically distilled and indexed │</style>'))
    print_formatted_text(HTML(' <style bg="#333300" color="#ffff00">│ into the Mimir-DB. Hard-won knowledge is preserved across all sessions.  │</style>'))
    print_formatted_text(HTML(' <style bg="#333300" color="#ffff00">└──────────────────────────────────────────────────────────────────────────┘</style>\n'))

    print_formatted_text(HTML(' <ansigray>                                                                    ? for shortcuts</ansigray>'))
    print_formatted_text(HTML(' <ansigray>TAB to autocomplete</ansigray>\n'))

    while True:
        try:
            # Added branding to prompt so it stays blue even as you scroll
            user_input = session.prompt(
                HTML('<branding>Mnemos-OS</branding> <magenta>&gt;</magenta> '),
                bottom_toolbar=get_toolbar
            )
            
            if not user_input.strip():
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                break

            try:
                args = shlex.split(user_input)
            except ValueError as e:
                print_formatted_text(HTML(f' <error>[!] Parsing error: {e}</error>'))
                continue

            cmd = args[0].lower()

            if cmd == 'add' and len(args) >= 4:
                entity, aspect, text = args[1], args[2].upper(), args[3]
                salience, file_path = 5, None
                if '--salience' in args:
                    try: salience = int(args[args.index('--salience')+1])
                    except: pass
                if '--file' in args:
                    try: file_path = args[args.index('--file')+1]
                    except: pass
                
                row_id = mnemo.add_fact(entity, aspect, text, salience, file_path=file_path)
                if row_id == -1:
                    print_formatted_text(HTML(' <gray>- Ignored (Salience Filter)</gray>'))
                else:
                    msg = f"Fact saved (ID: {row_id})"
                    if file_path: msg += f" linked to {file_path}"
                    print_formatted_text(HTML(f' <success>* {msg}</success>'))

            elif cmd == 'scratch' and len(args) >= 2:
                mnemo.update_scratchpad(args[1])
                print_formatted_text(HTML(' <success>* Scratchpad updated.</success>'))

            elif cmd == 'file' and len(args) >= 2:
                ctx = mnemo.get_file_context(args[1])
                if ctx:
                    print_formatted_text(HTML(f'\n <magenta>[FILE CONTEXT: {args[1]}]</magenta>'))
                    print_formatted_text(HTML(f' <cyan>{ctx}</cyan>\n'))
                else:
                    print_formatted_text(HTML(' <gray>- No specific memories for this file.</gray>'))

            elif cmd == 'context' and len(args) >= 2:
                limit = 15
                if '--limit' in args:
                    try: limit = int(args[args.index('--limit')+1])
                    except: pass
                ctx = mnemo.get_context(args[1], limit=limit)
                print_formatted_text(HTML(f'\n <magenta>[ACTIVE MINDSET: {args[1].upper()}]</magenta>'))
                print_formatted_text(HTML(f' <cyan>{ctx}</cyan>\n'))

            elif cmd == 'search' and len(args) >= 2:
                results = mnemo.search(args[1])
                if not results:
                    print_formatted_text(HTML(' <error>- No matches</error>'))
                else:
                    print_formatted_text(HTML(f'\n <cyan>SEARCH RESULTS:</cyan>'))
                    for r in results:
                        ent, asp, short = r[0], r[1], r[2]
                        header = f"{ent:<12} | {asp:<6} |"
                        print_formatted_text(HTML(f' <gray>{header}</gray> {short}'))
                    print("")

            elif cmd == 'list':
                entity = args[1] if len(args) >= 2 else None
                results = mnemo.list_memories(entity=entity)
                if not results:
                    print_formatted_text(HTML(' <error>- Memory is empty.</error>'))
                else:
                    header_txt = f"ALL MEMORIES:" if not entity else f"MEMORIES FOR {entity.upper()}:"
                    print_formatted_text(HTML(f'\n <cyan>{header_txt}</cyan>'))
                    print_formatted_text(HTML(f' <style color="#9b72f3">ENTITY       | TYPE   | S  | SHORTHAND</style>'))
                    print_formatted_text(HTML(f' <gray>{"-" * 55}</gray>'))
                    for r in results:
                        ent, asp, short, sal = r[0], r[1], r[2], r[3]
                        row_head = f"{ent:<12} | {asp:<6} | {sal:<2} |"
                        print_formatted_text(HTML(f' <gray>{row_head}</gray> {short}'))
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
                print_formatted_text(HTML(f' <magenta>* Purged {deleted} memories (older than {days} days, salience &lt; {min_salience}).</magenta>'))

            elif cmd == 'menu':
                sys.exit(100)

            elif cmd == 'help' or cmd == '?':
                print_formatted_text(HTML(f'\n <magenta>--- MNEMOS COMMAND GUIDE ---</magenta>'))
                print_formatted_text(HTML(f'  <ansiyellow>add &lt;entity&gt; &lt;aspect&gt; "text"</ansiyellow>'))
                print_formatted_text(HTML(f'    <gray>Archive a key project fact, architectural decision, or user preference.</gray>'))
                print_formatted_text(HTML(f'    <gray>Optional: --salience 1-10, --file path/to/file</gray>\n'))
                print_formatted_text(HTML(f'  <ansiyellow>context &lt;entity&gt;</ansiyellow>'))
                print_formatted_text(HTML(f'    <gray>Retrieve a dense shorthand briefing of project context for an AI.</gray>\n'))
                print_formatted_text(HTML(f'  <ansiyellow>scratch "your plan"</ansiyellow>'))
                print_formatted_text(HTML(f'    <gray>Update the active multi-step session plan for task continuity.</gray>\n'))
                print_formatted_text(HTML(f'  <ansiyellow>file "path/to/file"</ansiyellow>'))
                print_formatted_text(HTML(f'    <gray>Retrieve memories linked specifically to a code file.</gray>\n'))
                print_formatted_text(HTML(f'  <ansiyellow>search "query"</ansiyellow>'))
                print_formatted_text(HTML(f'    <gray>Find memories matching keywords using high-speed FTS5.</gray>\n'))
                print_formatted_text(HTML(f'  <ansiyellow>list [entity]</ansiyellow>'))
                print_formatted_text(HTML(f'    <gray>Browse all stored memories, optionally filtered by project.</gray>\n'))
                print_formatted_text(HTML(f'  <ansiyellow>purge [--days N] [--min-salience N]</ansiyellow>'))
                print_formatted_text(HTML(f'    <gray>Surgically clean old, low-salience memories from the DB.</gray>\n'))
                print_formatted_text(HTML(f'  <ansiyellow>menu</ansiyellow>'))
                print_formatted_text(HTML(f'    <gray>Return to the main mode selection screen.</gray>\n'))
                print_formatted_text(HTML(f'  <error>exit</error> or <error>quit</error>'))
                print_formatted_text(HTML(f'    <gray>Securely disconnect from the memory kernel.</gray>\n'))
            
            else:
                if cmd not in ['add', 'context', 'search', 'purge', 'scratch', 'file', 'menu', 'list']:
                    print_formatted_text(HTML(f' <error>[!] Unknown command. Type "help" for info.</error>'))
                else:
                    print_formatted_text(HTML(f' <error>[!] Missing arguments for "{cmd}".</error>'))

        except KeyboardInterrupt:
            print("")
            continue
        except EOFError:
            break
        except Exception as e:
            print_formatted_text(HTML(f' <error>[!] Error: {e}</error>'))

if __name__ == "__main__":
    main()
