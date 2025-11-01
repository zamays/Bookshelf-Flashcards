#!/usr/bin/env python3
"""
Main entry point for Bookshelf Flashcards application.
Provides unified access to both GUI and CLI interfaces.
"""

import sys


def main():
    """Main entry point for the application."""
    # Check if --mode is specified
    mode = 'gui'  # Default to GUI
    
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
            sys.argv.pop(mode_idx)  # Remove --mode
            sys.argv.pop(mode_idx)  # Remove the mode value
    
    # Check for help or no arguments (when no CLI command provided)
    # If no arguments after removing --mode, default to GUI
    if len(sys.argv) == 1:
        mode = 'gui'
    
    if mode == 'gui':
        # Import and run GUI
        from bookshelf_gui import main as gui_main
        gui_main()
    else:  # mode == 'cli'
        # Import and run CLI
        from bookshelf import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
