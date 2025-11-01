#!/usr/bin/env python3
"""
Main entry point for Bookshelf Flashcards application.
Provides unified access to both GUI and CLI interfaces.
"""

import sys


def main():
    """Main entry point for the application."""
    # Check if --mode is specified
    mode = None
    
    # Look for --mode in arguments
    if '--mode' in sys.argv:
        mode_idx = sys.argv.index('--mode')
        if mode_idx + 1 < len(sys.argv):
            mode = sys.argv[mode_idx + 1]
            # Validate mode
            if mode not in ['gui', 'cli']:
                print(f"Error: Invalid mode '{mode}'. Use 'gui' or 'cli'.", file=sys.stderr)
                print("\nUsage examples:")
                print("  python3 main.py                        # Launch GUI (default)")
                print("  python3 main.py --mode gui             # Launch GUI")
                print("  python3 main.py --mode cli list        # Launch CLI and list books")
                print("  python3 main.py --mode cli add-file books.txt  # Launch CLI and add books")
                sys.exit(1)
            # Remove --mode and its value from sys.argv
            # After first pop, the mode value moves to mode_idx position
            sys.argv.pop(mode_idx)  # Remove --mode
            sys.argv.pop(mode_idx)  # Remove the mode value (which is now at mode_idx)
        else:
            # --mode provided but no value
            print("Error: --mode requires a value ('gui' or 'cli').", file=sys.stderr)
            print("\nUsage examples:")
            print("  python3 main.py                        # Launch GUI (default)")
            print("  python3 main.py --mode gui             # Launch GUI")
            print("  python3 main.py --mode cli list        # Launch CLI and list books")
            print("  python3 main.py --mode cli add-file books.txt  # Launch CLI and add books")
            sys.exit(1)
    
    # If mode not specified, default based on remaining arguments
    # If no arguments after program name, default to GUI
    # If there are CLI commands, default to CLI
    if mode is None:
        if len(sys.argv) == 1:
            mode = 'gui'
        else:
            # Check if first remaining arg looks like a CLI command
            if sys.argv[1] in ['add', 'add-file', 'list', 'flashcard']:
                mode = 'cli'
            else:
                mode = 'gui'
    
    if mode == 'gui':
        # Import and run GUI
        # Update sys.argv[0] to match the expected module name
        sys.argv[0] = 'bookshelf_gui.py'
        from bookshelf_gui import main as gui_main
        gui_main()
    else:  # mode == 'cli'
        # Import and run CLI
        # Update sys.argv[0] to match the expected module name
        sys.argv[0] = 'bookshelf.py'
        from bookshelf import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
