"""Library module for managing a collection of books."""
import json
from pathlib import Path
from typing import List, Optional
from book import Book


class BookLibrary:
    """Manages a collection of books."""
    
    def __init__(self, data_file: str = "library.json"):
        """Initialize the library with a data file."""
        self.data_file = Path(data_file)
        self.books: List[Book] = []
        self.load()
    
    def add_book(self, title: str, author: str, is_read: bool = False, notes: Optional[str] = None):
        """Add a new book to the library."""
        book = Book(title=title, author=author, is_read=is_read, notes=notes)
        self.books.append(book)
        self.save()
        return book
    
    def get_books(self, include_unread: bool = True) -> List[Book]:
        """Get all books, optionally filtering out unread books.
        
        Args:
            include_unread: If True, returns all books. If False, returns only read books.
        
        Returns:
            List of books based on filter criteria.
        """
        if include_unread:
            return self.books.copy()
        return [book for book in self.books if book.is_read]
    
    def find_book(self, title: str) -> Optional[Book]:
        """Find a book by title (case-insensitive)."""
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None
    
    def mark_book_as_read(self, title: str) -> bool:
        """Mark a book as read by title.
        
        Returns:
            True if book was found and marked, False otherwise.
        """
        book = self.find_book(title)
        if book:
            book.mark_as_read()
            self.save()
            return True
        return False
    
    def mark_book_as_unread(self, title: str) -> bool:
        """Mark a book as unread by title.
        
        Returns:
            True if book was found and marked, False otherwise.
        """
        book = self.find_book(title)
        if book:
            book.mark_as_unread()
            self.save()
            return True
        return False
    
    def save(self):
        """Save the library to the data file."""
        data = [book.to_dict() for book in self.books]
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load the library from the data file."""
        if self.data_file.exists() and self.data_file.stat().st_size > 0:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.books = [Book.from_dict(book_data) for book_data in data]
