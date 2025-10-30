"""Tests for the Book model."""
import unittest
from book import Book


class TestBook(unittest.TestCase):
    """Test cases for the Book class."""
    
    def test_book_creation(self):
        """Test creating a new book."""
        book = Book(title="Test Book", author="Test Author")
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertFalse(book.is_read)
        self.assertIsNone(book.notes)
    
    def test_book_with_read_status(self):
        """Test creating a book with read status."""
        book = Book(title="Test Book", author="Test Author", is_read=True)
        self.assertTrue(book.is_read)
    
    def test_book_with_notes(self):
        """Test creating a book with notes."""
        book = Book(title="Test Book", author="Test Author", notes="Great book!")
        self.assertEqual(book.notes, "Great book!")
    
    def test_mark_as_read(self):
        """Test marking a book as read."""
        book = Book(title="Test Book", author="Test Author")
        self.assertFalse(book.is_read)
        book.mark_as_read()
        self.assertTrue(book.is_read)
    
    def test_mark_as_unread(self):
        """Test marking a book as unread."""
        book = Book(title="Test Book", author="Test Author", is_read=True)
        self.assertTrue(book.is_read)
        book.mark_as_unread()
        self.assertFalse(book.is_read)
    
    def test_to_dict(self):
        """Test converting book to dictionary."""
        book = Book(title="Test Book", author="Test Author", is_read=True, notes="Notes")
        book_dict = book.to_dict()
        self.assertEqual(book_dict["title"], "Test Book")
        self.assertEqual(book_dict["author"], "Test Author")
        self.assertTrue(book_dict["is_read"])
        self.assertEqual(book_dict["notes"], "Notes")
    
    def test_from_dict(self):
        """Test creating book from dictionary."""
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "is_read": True,
            "notes": "Notes"
        }
        book = Book.from_dict(data)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertTrue(book.is_read)
        self.assertEqual(book.notes, "Notes")


if __name__ == "__main__":
    unittest.main()
