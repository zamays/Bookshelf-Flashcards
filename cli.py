"""Command-line interface for the Bookshelf Flashcards application."""
import sys
from library import BookLibrary


def print_books(books, title="Books"):
    """Print a list of books in a formatted way."""
    if not books:
        print(f"\n{title}: None")
        return
    
    print(f"\n{title}:")
    print("-" * 80)
    for i, book in enumerate(books, 1):
        status = "✓ Read" if book.is_read else "○ Unread"
        print(f"{i}. {book.title} by {book.author} [{status}]")
        if book.notes:
            print(f"   Notes: {book.notes}")
    print("-" * 80)


def show_help():
    """Display help information."""
    help_text = """
Bookshelf Flashcards - Manage your book library and refresh your memory

Commands:
  add <title> <author> [--read] [--notes "text"]
      Add a new book to your library
      --read: Mark the book as read when adding
      --notes: Add notes about the book

  list [--read-only]
      List all books in your library
      --read-only: Show only books you have read

  mark-read <title>
      Mark a book as read

  mark-unread <title>
      Mark a book as unread

  find <title>
      Find a book by title

  help
      Show this help message

Examples:
  python cli.py add "The Great Gatsby" "F. Scott Fitzgerald" --read
  python cli.py list --read-only
  python cli.py mark-read "The Great Gatsby"
"""
    print(help_text)


def main():
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    library = BookLibrary()
    
    if command == "help":
        show_help()
    
    elif command == "add":
        if len(sys.argv) < 4:
            print("Error: 'add' command requires title and author")
            print("Usage: add <title> <author> [--read] [--notes \"text\"]")
            return
        
        title = sys.argv[2]
        author = sys.argv[3]
        is_read = "--read" in sys.argv
        
        # Parse notes if provided
        notes = None
        if "--notes" in sys.argv:
            notes_idx = sys.argv.index("--notes")
            if notes_idx + 1 < len(sys.argv):
                notes = sys.argv[notes_idx + 1]
        
        book = library.add_book(title, author, is_read=is_read, notes=notes)
        status = "read" if book.is_read else "unread"
        print(f"✓ Added '{book.title}' by {book.author} (marked as {status})")
    
    elif command == "list":
        read_only = "--read-only" in sys.argv
        books = library.get_books(include_unread=not read_only)
        
        if read_only:
            print_books(books, "Books You Have Read")
        else:
            print_books(books, "All Books in Library")
        
        if not read_only:
            read_count = sum(1 for b in books if b.is_read)
            unread_count = len(books) - read_count
            print(f"\nTotal: {len(books)} books ({read_count} read, {unread_count} unread)")
        else:
            print(f"\nTotal: {len(books)} books read")
    
    elif command == "mark-read":
        if len(sys.argv) < 3:
            print("Error: 'mark-read' command requires a book title")
            return
        
        title = sys.argv[2]
        if library.mark_book_as_read(title):
            print(f"✓ Marked '{title}' as read")
        else:
            print(f"✗ Book '{title}' not found in library")
    
    elif command == "mark-unread":
        if len(sys.argv) < 3:
            print("Error: 'mark-unread' command requires a book title")
            return
        
        title = sys.argv[2]
        if library.mark_book_as_unread(title):
            print(f"✓ Marked '{title}' as unread")
        else:
            print(f"✗ Book '{title}' not found in library")
    
    elif command == "find":
        if len(sys.argv) < 3:
            print("Error: 'find' command requires a book title")
            return
        
        title = sys.argv[2]
        book = library.find_book(title)
        if book:
            print_books([book], f"Found: {title}")
        else:
            print(f"✗ Book '{title}' not found in library")
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'help' to see available commands")


if __name__ == "__main__":
    main()
