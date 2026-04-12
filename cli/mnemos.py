import sys
import os
import argparse

# Add the parent directory to sys.path so we can import core.engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import MnemosCore

# ANSI Color Constants
C_GRN = "\033[92m"
C_YLW = "\033[93m"
C_CYN = "\033[96m"
C_RED = "\033[91m"
C_BLU = "\033[94m"
C_MAG = "\033[95m"
C_RST = "\033[0m"
C_BLD = "\033[1m"

def main():
    mnemo = MnemosCore()
    parser = argparse.ArgumentParser(description="MNEMOS-OS CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Add Fact
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("entity")
    add_parser.add_argument("aspect", choices=["PREF", "BUG", "ARCH", "DEP", "LOG"])
    add_parser.add_argument("text")
    add_parser.add_argument("--salience", type=int, default=5)

    # Get Context
    ctx_parser = subparsers.add_parser("context")
    ctx_parser.add_argument("entity")
    ctx_parser.add_argument("--limit", type=int, default=15)

    # Search
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")

    # Purge
    purge_parser = subparsers.add_parser("purge")

    args = parser.parse_args()

    if args.command == "add":
        row_id = mnemo.add_fact(args.entity, args.aspect, args.text, args.salience)
        if row_id == -1:
            print(f"{C_YLW}⏳ Fact ignored by Salience Filter (too noisy/short).{C_RST}")
        else:
            print(f"{C_GRN}✅ Fact carved into stone (ID: {row_id}){C_RST}")
    
    elif args.command == "context":
        ctx = mnemo.get_context(args.entity, limit=args.limit)
        print(f"\n{C_MAG}🧠 [ACTIVE MINDSET: {args.entity.upper()}]{C_RST}")
        print(f"{C_CYN}{ctx}{C_RST}\n")

    elif args.command == "search":
        results = mnemo.search(args.query)
        if not results:
            print(f"{C_RED}No matches found in MÍMIR.{C_RST}")
        else:
            print(f"\n{C_YLW}🔍 SEARCH RESULTS:{C_RST}")
            print(f"{C_BLU}{'ENTITY':<12} | {'TYPE':<6} | {'SHORTHAND'}{C_RST}")
            print("-" * 50)
            for r in results:
                color = C_GRN if r[1] == "PREF" else C_RED if r[1] == "BUG" else C_CYN
                print(f"{C_BLD}{r[0]:<12}{C_RST} | {color}{r[1]:<6}{C_RST} | {r[2]}")
            print("")
            
    elif args.command == "purge":
        deleted = mnemo.purge_lethe()
        print(f"{C_MAG}🧹 Lethe Protocol complete. {C_RST}{C_GRN}{deleted} stale memories purged.{C_RST}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
