#!/usr/bin/env python3
"""
Debug script to test importing bookshelf_gui module.
"""
import sys
import traceback

try:
    print("Attempting to import bookshelf_gui...")
    import bookshelf_gui  # noqa: F401, pylint: disable=unused-import
    print("Success!")
except Exception as e:
    print(f"\nError type: {type(e).__name__}")
    print(f"Error message: {str(e)}\n")
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)
