"""
Database module for storing book information and summaries.
"""
import sqlite3
from typing import List, Optional


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
        """Create necessary database tables."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(title, author)
            )
        """)
        self.conn.commit()
    def add_book(self, title: str, author: str, summary: Optional[str] = None) -> int:
        """
        Add a book to the database.

        Args:
            title: Book title
            author: Book author
            summary: Book summary (optional)

        Returns:
            Book ID
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO books (title, author, summary) VALUES (?, ?, ?)",
                (title, author, summary)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Book already exists, return existing ID
            cursor.execute(
                "SELECT id FROM books WHERE title = ? AND author = ?",
                (title, author)
            )
            result = cursor.fetchone()
            return result['id'] if result else -1
    def update_summary(self, book_id: int, summary: str):
        """Update the summary for a book."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE books SET summary = ? WHERE id = ?",
            (summary, book_id)
        )
        self.conn.commit()
    def get_book(self, book_id: int) -> Optional[dict]:
        """Get a book by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
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
