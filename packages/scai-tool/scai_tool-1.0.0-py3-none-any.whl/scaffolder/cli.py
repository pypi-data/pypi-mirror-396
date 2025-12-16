import argparse
import sys
import os
from .core import parse_tree, execute_actions

def main():
    parser = argparse.ArgumentParser(description="Generate directory structures from AI text trees.")
    parser.add_argument('file', nargs='?', help="Text file containing the tree structure (optional if using stdin or --gui)")
    parser.add_argument('--gui', action='store_true', help="Launch the graphical interface")
    parser.add_argument('--target', default=os.getcwd(), help="Target base directory (default: current dir)")
    parser.add_argument('--preview', action='store_true', help="Show what would happen without creating files")
    
    args = parser.parse_args()

    # 1. Launch GUI if requested 
    if args.gui:
        # We import gui here to avoid tkinter checks if just using CLI
        from .gui import run_gui
        run_gui()
        return

    # 2. Input Handling (File vs Pipe vs Empty)
    content = ""
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
    elif not sys.stdin.isatty():
        # Read from pipe
        content = sys.stdin.read()
    else:
        # No input provided, default to GUI for better UX
        print("No input detected. Launching GUI...")
        from .gui import run_gui
        run_gui()
        return

    # 3. Process
    print(f"Target Base: {args.target}")
    actions = parse_tree(content, args.target)
    
    if not actions:
        print("No valid structure detected in input.")
        sys.exit(1)

    # 4. Execute
    print("--- processing ---")
    for msg in execute_actions(actions, dry_run=args.preview):
        print(msg)

if __name__ == "__main__":
    main()