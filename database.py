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
from models import User


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
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE CHECK(length(email) <= 254),
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified INTEGER DEFAULT 0
            )
        """)
        
        # Create books table with user_id foreign key
        # Note: UNIQUE constraint is on (title, author) only for backwards compatibility
        # Application-level logic ensures books are unique per user
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK(length(title) <= 500),
                author TEXT NOT NULL CHECK(length(author) <= 200),
                summary TEXT CHECK(summary IS NULL OR length(summary) <= 10000),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                UNIQUE(title, author),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
        
        # Migration: Add user_id column if it doesn't exist (for backwards compatibility)
        cursor.execute("PRAGMA table_info(books)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN user_id INTEGER")
            self.conn.commit()
    def add_book(self, title: str, author: str, summary: Optional[str] = None, 
                 user_id: Optional[int] = None) -> int:
        """
        Add a book to the database with input validation.

        Args:
            title: Book title
            author: Book author
            summary: Book summary (optional)
            user_id: User ID who owns this book (optional)

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
        
        # Check for existing book first (application-level duplicate check)
        if user_id is None:
            cursor.execute(
                "SELECT id FROM books WHERE title = ? AND author = ? AND user_id IS NULL",
                (validated_title, validated_author)
            )
        else:
            cursor.execute(
                "SELECT id FROM books WHERE title = ? AND author = ? AND user_id = ?",
                (validated_title, validated_author, user_id)
            )
        existing = cursor.fetchone()
        if existing:
            return existing['id']
        
        # Insert new book
        try:
            cursor.execute(
                "INSERT INTO books (title, author, summary, user_id) VALUES (?, ?, ?, ?)",
                (validated_title, validated_author, validated_summary, user_id)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # This shouldn't happen due to the check above, but handle it anyway
            # Might occur due to race conditions
            cursor.execute(
                "SELECT id FROM books WHERE title = ? AND author = ?",
                (validated_title, validated_author)
            )
            result = cursor.fetchone()
            return result['id'] if result else -1
    def update_summary(self, book_id: int, summary: str, user_id: Optional[int] = None):
        """
        Update the summary for a book with validation.
        
        Args:
            book_id: Book ID to update
            summary: New summary text
            user_id: User ID (optional, for authorization check)
            
        Raises:
            ValidationError: If input validation fails
        """
        from validation import validate_summary
        
        # Validate inputs
        validated_id = validate_book_id(book_id)
        validated_summary = validate_summary(summary)
        
        cursor = self.conn.cursor()
        if user_id is not None:
            # Update only if book belongs to user
            cursor.execute(
                "UPDATE books SET summary = ? WHERE id = ? AND user_id = ?",
                (validated_summary, validated_id, user_id)
            )
        else:
            # No user specified (backwards compatibility)
            cursor.execute(
                "UPDATE books SET summary = ? WHERE id = ?",
                (validated_summary, validated_id)
            )
        self.conn.commit()
    def get_book(self, book_id: int, user_id: Optional[int] = None) -> Optional[dict]:
        """
        Get a book by ID with validation.
        
        Args:
            book_id: Book ID to retrieve
            user_id: User ID (optional, for authorization check)
            
        Returns:
            Book dictionary or None if not found
            
        Raises:
            ValidationError: If book_id is invalid
        """
        # Validate book_id
        validated_id = validate_book_id(book_id)
        
        cursor = self.conn.cursor()
        if user_id is not None:
            # Get book only if it belongs to user or has no owner
            cursor.execute(
                "SELECT * FROM books WHERE id = ? AND (user_id = ? OR user_id IS NULL)", 
                (validated_id, user_id)
            )
        else:
            # No user specified (backwards compatibility)
            cursor.execute("SELECT * FROM books WHERE id = ?", (validated_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    def get_all_books(self, user_id: Optional[int] = None) -> List[dict]:
        """
        Get all books from the database.
        
        Args:
            user_id: User ID to filter books (optional)
            
        Returns:
            List of book dictionaries
        """
        cursor = self.conn.cursor()
        if user_id is not None:
            # Get books belonging to user or with no owner
            cursor.execute(
                "SELECT * FROM books WHERE user_id = ? OR user_id IS NULL ORDER BY created_at DESC",
                (user_id,)
            )
        else:
            # No user specified (backwards compatibility)
            cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    def search_books_by_title(self, title: str) -> List[dict]:
        """Search for books by title."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books WHERE title = ?", (title,))
        return [dict(row) for row in cursor.fetchall()]
    def create_user(self, email: str, password_hash: str) -> int:
        """
        Create a new user account.
        
        Args:
            email: User's email address
            password_hash: Hashed password
            
        Returns:
            User ID
            
        Raises:
            sqlite3.IntegrityError: If user already exists
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User object or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        if result:
            return User(
                user_id=result['id'],
                email=result['email'],
                password_hash=result['password_hash'],
                created_at=result['created_at'],
                verified=bool(result['verified'])
            )
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User object or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return User(
                user_id=result['id'],
                email=result['email'],
                password_hash=result['password_hash'],
                created_at=result['created_at'],
                verified=bool(result['verified'])
            )
        return None
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
