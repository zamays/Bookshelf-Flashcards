"""
Main CLI application for Bookshelf Flashcards.
"""
import argparse
import os
from typing import Optional

from database import BookDatabase
from ai_service import SummaryGenerator
from book_parser import parse_book_file


class BookshelfApp:
    """Main application class for managing bookshelf flashcards."""
    
    def __init__(self, db_path: str = "bookshelf.db", quiet: bool = False):
        """Initialize the application."""
        self.db = BookDatabase(db_path)
        self.ai_service = None
        self.quiet = quiet
        self._init_ai_service()
    
    def _init_ai_service(self):
        """Initialize AI service if API key is available."""
        try:
            self.ai_service = SummaryGenerator()
        except ValueError as e:
            if not self.quiet:
                print(f"Warning: {e}")
                print("AI summary generation will not be available.")
    
    def add_book_from_file(self, file_path: str):
        """
        Add books from a file.
        
        Args:
            file_path: Path to file containing book titles
        """
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return
        
        print(f"Reading books from {file_path}...")
        books = parse_book_file(file_path)
        
        if not books:
            print("No books found in file.")
            return
        
        print(f"Found {len(books)} book(s) in file.")
        
        for title, author in books:
            if author:
                self._add_single_book(title, author)
            else:
                # Check if there are multiple books with this title
                existing = self.db.search_books_by_title(title)
                
                if existing:
                    print(f"\nBook '{title}' already exists in database:")
                    for idx, book in enumerate(existing, 1):
                        print(f"  {idx}. {book['author']}")
                    
                    author = input(f"Enter author for '{title}': ").strip()
                    if author:
                        self._add_single_book(title, author)
                    else:
                        print(f"Skipping '{title}' (no author provided)")
                else:
                    # No existing books with this title, ask for author
                    author = input(f"Enter author for '{title}': ").strip()
                    if author:
                        self._add_single_book(title, author)
                    else:
                        print(f"Skipping '{title}' (no author provided)")
    
    def _add_single_book(self, title: str, author: str):
        """Add a single book to the database with summary generation."""
        print(f"\nAdding: '{title}' by {author}")
        
        # Add book to database
        book_id = self.db.add_book(title, author)
        
        if book_id == -1:
            print(f"  Book already exists in database.")
            return
        
        # Check if book already has a summary
        book = self.db.get_book(book_id)
        if book and book.get('summary'):
            print(f"  Book already has a summary.")
            return
        
        # Generate summary if AI service is available
        if self.ai_service:
            print(f"  Generating summary...")
            try:
                summary = self.ai_service.generate_summary(title, author)
                self.db.update_summary(book_id, summary)
                print(f"  ✓ Summary generated and saved.")
            except Exception as e:
                print(f"  Error generating summary: {e}")
        else:
            print(f"  ✓ Book added (no summary - AI service not available)")
    
    def add_book_interactive(self):
        """Add a book interactively through prompts."""
        print("\n=== Add New Book ===")
        title = input("Enter book title: ").strip()
        if not title:
            print("Title cannot be empty.")
            return
        
        author = input("Enter book author: ").strip()
        if not author:
            print("Author cannot be empty.")
            return
        
        self._add_single_book(title, author)
    
    def view_books(self):
        """View all books in the bookshelf."""
        books = self.db.get_all_books()
        
        if not books:
            print("\nNo books in your bookshelf yet. Add some books to get started!")
            return
        
        print(f"\n=== Your Bookshelf ({len(books)} books) ===")
        for idx, book in enumerate(books, 1):
            print(f"\n{idx}. '{book['title']}' by {book['author']}")
            if book['summary']:
                print(f"   Added: {book['created_at']}")
            else:
                print(f"   Added: {book['created_at']} (no summary)")
    
    def flashcard_mode(self):
        """Display books in flashcard mode for memory refreshing."""
        books = self.db.get_all_books()
        
        if not books:
            print("\nNo books in your bookshelf yet. Add some books to get started!")
            return
        
        print(f"\n=== Flashcard Mode ({len(books)} books) ===")
        print("Press Enter to see the next book, or 'q' to quit.\n")
        
        for idx, book in enumerate(books, 1):
            print(f"\n--- Book {idx}/{len(books)} ---")
            print(f"Title: {book['title']}")
            print(f"Author: {book['author']}")
            
            if book['summary']:
                input("\nPress Enter to see summary...")
                print(f"\nSummary:")
                print(f"{book['summary']}")
            else:
                print("\n(No summary available)")
            
            if idx < len(books):
                response = input(f"\nPress Enter for next book, or 'q' to quit: ").strip().lower()
                if response == 'q':
                    break
        
        print("\n=== End of Flashcards ===")
    
    def close(self):
        """Close the application and database connection."""
        self.db.close()


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Bookshelf Flashcards - Remember what you've read",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add books from a file
  python3 bookshelf.py add-file books.txt
  
  # Add a book interactively
  python3 bookshelf.py add
  
  # View all books
  python3 bookshelf.py list
  
  # Start flashcard mode
  python3 bookshelf.py flashcard
  
  # Suppress API key warnings
  python3 bookshelf.py --quiet list
        """
    )
    
    parser.add_argument(
        'command',
        choices=['add', 'add-file', 'list', 'flashcard'],
        help='Command to execute'
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='File path (required for add-file command)'
    )
    parser.add_argument(
        '--db',
        default='bookshelf.db',
        help='Database file path (default: bookshelf.db)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress warnings (e.g., missing API key warning)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.command == 'add-file' and not args.file:
        parser.error("add-file command requires a file path")
    
    # Create application instance
    app = BookshelfApp(args.db, quiet=args.quiet)
    
    try:
        if args.command == 'add-file':
            app.add_book_from_file(args.file)
        elif args.command == 'add':
            app.add_book_interactive()
        elif args.command == 'list':
            app.view_books()
        elif args.command == 'flashcard':
            app.flashcard_mode()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    finally:
        app.close()


if __name__ == "__main__":
    main()
