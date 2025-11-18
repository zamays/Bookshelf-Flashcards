"""
Database module for storing book information and summaries.
"""
import sqlite3
from typing import List, Optional
from validation import (
    validate_all_book_data,
    validate_book_id,
    ValidationError
)


class BookDatabase:
    """Database handler for bookshelf application."""

    def __init__(self, db_path: str = "bookshelf.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        # check_same_thread=False allows SQLite to be used in multi-threaded Flask app
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    def _create_tables(self):
        """Create necessary database tables with length constraints."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK(length(title) <= 500),
                author TEXT NOT NULL CHECK(length(author) <= 200),
                summary TEXT CHECK(summary IS NULL OR length(summary) <= 10000),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(title, author)
            )
        """)
        self.conn.commit()
    def add_book(self, title: str, author: str, summary: Optional[str] = None) -> int:
        """
        Add a book to the database with input validation.

        Args:
            title: Book title
            author: Book author
            summary: Book summary (optional)

        Returns:
            Book ID, or -1 if book already exists

        Raises:
            ValidationError: If input validation fails
        """
        # Validate all inputs before adding to database
        validated_title, validated_author, validated_summary = validate_all_book_data(
            title, author, summary
        )
        
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO books (title, author, summary) VALUES (?, ?, ?)",
                (validated_title, validated_author, validated_summary)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Book already exists, return existing ID
            cursor.execute(
                "SELECT id FROM books WHERE title = ? AND author = ?",
                (validated_title, validated_author)
            )
            result = cursor.fetchone()
            return result['id'] if result else -1
    def update_summary(self, book_id: int, summary: str):
        """
        Update the summary for a book with validation.
        
        Args:
            book_id: Book ID to update
            summary: New summary text
            
        Raises:
            ValidationError: If input validation fails
        """
        from validation import validate_summary
        
        # Validate inputs
        validated_id = validate_book_id(book_id)
        validated_summary = validate_summary(summary)
        
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE books SET summary = ? WHERE id = ?",
            (validated_summary, validated_id)
        )
        self.conn.commit()
    def get_book(self, book_id: int) -> Optional[dict]:
        """
        Get a book by ID with validation.
        
        Args:
            book_id: Book ID to retrieve
            
        Returns:
            Book dictionary or None if not found
            
        Raises:
            ValidationError: If book_id is invalid
        """
        # Validate book_id
        validated_id = validate_book_id(book_id)
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (validated_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    def get_all_books(self) -> List[dict]:
        """Get all books from the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    def search_books_by_title(self, title: str) -> List[dict]:
        """Search for books by title."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books WHERE title = ?", (title,))
        return [dict(row) for row in cursor.fetchall()]
    def close(self):
        """Close the database connection."""
        self.conn.close()
