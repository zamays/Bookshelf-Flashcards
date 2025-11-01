#!/usr/bin/env python3
import sys
import traceback

try:
    print("Attempting to import bookshelf_gui...")
    from bookshelf_gui import main
    print("Success!")
except Exception as e:
    print(f"\nError type: {type(e).__name__}")
    print(f"Error message: {str(e)}\n")
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)
