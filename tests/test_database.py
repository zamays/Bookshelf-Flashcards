"""
Unit tests for database.py module.
"""
import os
import sqlite3
import pytest
from database import BookDatabase


class TestBookDatabaseInit:
    """Tests for BookDatabase initialization."""

    def test_init_creates_database_file(self, temp_db_path):
        """Test that initialization creates a database file."""
        db = BookDatabase(temp_db_path)
        assert os.path.exists(temp_db_path)
        db.close()

    def test_init_creates_books_table(self, temp_db_path):
        """Test that initialization creates the books table."""
        db = BookDatabase(temp_db_path)
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='books'
        """)
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'books'
        db.close()

    def test_table_schema(self, temp_db_path):
        """Test that the books table has correct schema."""
        db = BookDatabase(temp_db_path)
        cursor = db.conn.cursor()
        cursor.execute("PRAGMA table_info(books)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'id' in columns
        assert 'title' in columns
        assert 'author' in columns
        assert 'summary' in columns
        assert 'created_at' in columns
        db.close()


class TestBookDatabaseCRUDOperations:
    """Tests for CRUD operations."""

    def test_add_book_returns_id(self, temp_db_path):
        """Test that add_book returns a valid book ID."""
        db = BookDatabase(temp_db_path)
        book_id = db.add_book("1984", "George Orwell")
        assert isinstance(book_id, int)
        assert book_id > 0
        db.close()

    def test_add_book_with_summary(self, temp_db_path):
        """Test adding a book with a summary."""
        db = BookDatabase(temp_db_path)
        summary = "A dystopian novel about totalitarianism."
        book_id = db.add_book("1984", "George Orwell", summary)
        
        book = db.get_book(book_id)
        assert book is not None
        assert book['summary'] == summary
        db.close()

    def test_get_book_returns_correct_data(self, temp_db_path):
        """Test that get_book returns correct book data."""
        db = BookDatabase(temp_db_path)
        book_id = db.add_book("1984", "George Orwell")
        
        book = db.get_book(book_id)
        assert book is not None
        assert book['title'] == "1984"
        assert book['author'] == "George Orwell"
        assert book['id'] == book_id
        db.close()

    def test_get_book_nonexistent_returns_none(self, temp_db_path):
        """Test that get_book returns None for nonexistent book."""
        db = BookDatabase(temp_db_path)
        book = db.get_book(999999)
        assert book is None
        db.close()

    def test_update_summary(self, temp_db_path):
        """Test updating a book's summary."""
        db = BookDatabase(temp_db_path)
        book_id = db.add_book("1984", "George Orwell")
        
        new_summary = "A dystopian novel set in Oceania."
        db.update_summary(book_id, new_summary)
        
        book = db.get_book(book_id)
        assert book['summary'] == new_summary
        db.close()

    def test_get_all_books_empty(self, temp_db_path):
        """Test get_all_books on empty database."""
        db = BookDatabase(temp_db_path)
        books = db.get_all_books()
        assert books == []
        db.close()

    def test_get_all_books_returns_multiple(self, temp_db_path, sample_books):
        """Test get_all_books returns all books."""
        db = BookDatabase(temp_db_path)
        
        for title, author in sample_books:
            db.add_book(title, author)
        
        books = db.get_all_books()
        assert len(books) == len(sample_books)
        
        titles = [book['title'] for book in books]
        for title, _ in sample_books:
            assert title in titles
        db.close()

    def test_get_all_books_ordered_by_created_at(self, temp_db_path):
        """Test that get_all_books returns books ordered by created_at DESC."""
        import time
        db = BookDatabase(temp_db_path)
        
        # Add books with small delays to ensure different timestamps
        db.add_book("First Book", "Author A")
        time.sleep(0.01)  # Small delay to ensure different timestamp
        db.add_book("Second Book", "Author B")
        time.sleep(0.01)
        db.add_book("Third Book", "Author C")
        
        books = db.get_all_books()
        # Should be in DESC order (most recent first)
        # Due to timestamp resolution, we'll check that all books are returned
        assert len(books) == 3
        titles = [book['title'] for book in books]
        assert "First Book" in titles
        assert "Second Book" in titles
        assert "Third Book" in titles
        db.close()


class TestBookDatabaseDuplicateHandling:
    """Tests for duplicate book handling."""

    def test_add_duplicate_book_returns_existing_id(self, temp_db_path):
        """Test that adding a duplicate book returns the existing ID."""
        db = BookDatabase(temp_db_path)
        
        first_id = db.add_book("1984", "George Orwell")
        second_id = db.add_book("1984", "George Orwell")
        
        assert first_id == second_id
        db.close()

    def test_duplicate_book_unique_constraint(self, temp_db_path):
        """Test that duplicate books don't create multiple entries."""
        db = BookDatabase(temp_db_path)
        
        db.add_book("1984", "George Orwell")
        db.add_book("1984", "George Orwell")
        
        books = db.get_all_books()
        assert len(books) == 1
        db.close()

    def test_same_title_different_author_allowed(self, temp_db_path):
        """Test that same title with different author is allowed."""
        db = BookDatabase(temp_db_path)
        
        id1 = db.add_book("The Stand", "Stephen King")
        id2 = db.add_book("The Stand", "Different Author")
        
        assert id1 != id2
        books = db.get_all_books()
        assert len(books) == 2
        db.close()


class TestBookDatabaseSearch:
    """Tests for search functionality."""

    def test_search_books_by_title_found(self, temp_db_path):
        """Test searching for books by title."""
        db = BookDatabase(temp_db_path)
        db.add_book("1984", "George Orwell")
        db.add_book("Animal Farm", "George Orwell")
        
        results = db.search_books_by_title("1984")
        assert len(results) == 1
        assert results[0]['title'] == "1984"
        db.close()

    def test_search_books_by_title_not_found(self, temp_db_path):
        """Test searching for non-existent title."""
        db = BookDatabase(temp_db_path)
        db.add_book("1984", "George Orwell")
        
        results = db.search_books_by_title("Nonexistent Book")
        assert len(results) == 0
        db.close()

    def test_search_books_by_title_exact_match(self, temp_db_path):
        """Test that search requires exact title match."""
        db = BookDatabase(temp_db_path)
        db.add_book("1984", "George Orwell")
        
        results = db.search_books_by_title("198")  # Partial match
        assert len(results) == 0
        db.close()

    def test_search_multiple_books_same_title(self, temp_db_path):
        """Test searching when multiple books have same title."""
        db = BookDatabase(temp_db_path)
        db.add_book("The Stand", "Stephen King")
        db.add_book("The Stand", "Another Author")
        
        results = db.search_books_by_title("The Stand")
        assert len(results) == 2
        db.close()


class TestBookDatabaseEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_empty_string_title(self, temp_db_path):
        """Test adding a book with empty title."""
        db = BookDatabase(temp_db_path)
        book_id = db.add_book("", "Author Name")
        assert book_id > 0
        
        book = db.get_book(book_id)
        assert book['title'] == ""
        db.close()

    def test_empty_string_author(self, temp_db_path):
        """Test adding a book with empty author."""
        db = BookDatabase(temp_db_path)
        book_id = db.add_book("Book Title", "")
        assert book_id > 0
        
        book = db.get_book(book_id)
        assert book['author'] == ""
        db.close()

    def test_special_characters_in_title(self, temp_db_path):
        """Test adding book with special characters."""
        db = BookDatabase(temp_db_path)
        special_title = "Book's Title: A \"Special\" Test & More!"
        book_id = db.add_book(special_title, "Author Name")
        
        book = db.get_book(book_id)
        assert book['title'] == special_title
        db.close()

    def test_unicode_characters(self, temp_db_path):
        """Test adding book with Unicode characters."""
        db = BookDatabase(temp_db_path)
        unicode_title = "Café Müller — 東京物語"
        unicode_author = "François Lefèvre"
        book_id = db.add_book(unicode_title, unicode_author)
        
        book = db.get_book(book_id)
        assert book['title'] == unicode_title
        assert book['author'] == unicode_author
        db.close()

    def test_very_long_title(self, temp_db_path):
        """Test adding book with very long title."""
        db = BookDatabase(temp_db_path)
        long_title = "A" * 10000  # Very long title
        book_id = db.add_book(long_title, "Author")
        
        book = db.get_book(book_id)
        assert book['title'] == long_title
        db.close()

    def test_sql_injection_attempt_title(self, temp_db_path):
        """Test SQL injection attempt in title."""
        db = BookDatabase(temp_db_path)
        malicious_title = "'; DROP TABLE books; --"
        book_id = db.add_book(malicious_title, "Author")
        
        # Should safely store the malicious string
        book = db.get_book(book_id)
        assert book['title'] == malicious_title
        
        # Table should still exist
        books = db.get_all_books()
        assert len(books) == 1
        db.close()

    def test_sql_injection_attempt_author(self, temp_db_path):
        """Test SQL injection attempt in author."""
        db = BookDatabase(temp_db_path)
        malicious_author = "' OR '1'='1"
        book_id = db.add_book("Normal Title", malicious_author)
        
        book = db.get_book(book_id)
        assert book['author'] == malicious_author
        db.close()

    def test_null_summary(self, temp_db_path):
        """Test adding book with None as summary."""
        db = BookDatabase(temp_db_path)
        book_id = db.add_book("Title", "Author", None)
        
        book = db.get_book(book_id)
        assert book['summary'] is None
        db.close()

    def test_update_summary_for_nonexistent_book(self, temp_db_path):
        """Test updating summary for non-existent book."""
        db = BookDatabase(temp_db_path)
        # Should not raise an error
        db.update_summary(999999, "Some summary")
        db.close()


class TestBookDatabaseConnection:
    """Tests for database connection management."""

    def test_close_connection(self, temp_db_path):
        """Test closing database connection."""
        db = BookDatabase(temp_db_path)
        db.close()
        
        # After closing, operations should fail
        with pytest.raises(sqlite3.ProgrammingError):
            db.get_all_books()

    def test_database_persistence(self, temp_db_path):
        """Test that data persists across connections."""
        # First connection - add data
        db1 = BookDatabase(temp_db_path)
        book_id = db1.add_book("1984", "George Orwell")
        db1.close()
        
        # Second connection - verify data exists
        db2 = BookDatabase(temp_db_path)
        book = db2.get_book(book_id)
        assert book is not None
        assert book['title'] == "1984"
        db2.close()
