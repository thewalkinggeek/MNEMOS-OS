# MNEMOS-OS Script Interface (Non-Interactive)
# Copyright © 2026 Jonathan Schoenberger
# Licensed under the MIT License

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

def main():
    mnemo = MnemosCore()
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

    # 9. Help
    help_parser = subparsers.add_parser("help", help="Show this help message and exit")

    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
        sys.exit(0)

    if args.command == "add":
        row_id = mnemo.add_fact(args.entity, args.aspect, args.text, args.salience, file_path=args.file, related_id=args.related)
        if row_id == -1:
            print(f" {C_GRY}- Ignored by Salience Filter (too noisy/short){C_RST}")
        else:
            msg = f"Fact saved (ID: {row_id})"
            if args.file: msg += f" linked to {args.file}"
            if args.related: msg += f" related to ID:{args.related}"
            print(f" {C_GRN}✔ {msg}{C_RST}")
    
    elif args.command == "details":
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
        ctx = mnemo.get_context(args.entity, limit=args.limit)
        print(f" {C_MAG}[ACTIVE MINDSET: {args.entity.upper()}]{C_RST}")
        print(f" {C_CYN}{ctx}{C_RST}\n")

    elif args.command == "search":
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
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
