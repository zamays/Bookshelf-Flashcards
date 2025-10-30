"""Tests for the BookLibrary class."""
import unittest
import os
import tempfile
from pathlib import Path
from library import BookLibrary
from book import Book


class TestBookLibrary(unittest.TestCase):
    """Test cases for the BookLibrary class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.library = BookLibrary(data_file=self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_add_book(self):
        """Test adding a book to the library."""
        book = self.library.add_book("Test Book", "Test Author")
        self.assertEqual(len(self.library.books), 1)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertFalse(book.is_read)
    
    def test_add_book_as_read(self):
        """Test adding a book marked as read."""
        book = self.library.add_book("Test Book", "Test Author", is_read=True)
        self.assertTrue(book.is_read)
    
    def test_add_book_with_notes(self):
        """Test adding a book with notes."""
        book = self.library.add_book("Test Book", "Test Author", notes="Great read!")
        self.assertEqual(book.notes, "Great read!")
    
    def test_get_books_all(self):
        """Test getting all books including unread."""
        self.library.add_book("Book 1", "Author 1", is_read=True)
        self.library.add_book("Book 2", "Author 2", is_read=False)
        self.library.add_book("Book 3", "Author 3", is_read=True)
        
        books = self.library.get_books(include_unread=True)
        self.assertEqual(len(books), 3)
    
    def test_get_books_read_only(self):
        """Test getting only read books."""
        self.library.add_book("Book 1", "Author 1", is_read=True)
        self.library.add_book("Book 2", "Author 2", is_read=False)
        self.library.add_book("Book 3", "Author 3", is_read=True)
        
        books = self.library.get_books(include_unread=False)
        self.assertEqual(len(books), 2)
        self.assertTrue(all(book.is_read for book in books))
    
    def test_find_book(self):
        """Test finding a book by title."""
        self.library.add_book("Test Book", "Test Author")
        book = self.library.find_book("Test Book")
        self.assertIsNotNone(book)
        self.assertEqual(book.title, "Test Book")
    
    def test_find_book_case_insensitive(self):
        """Test finding a book with case-insensitive search."""
        self.library.add_book("Test Book", "Test Author")
        book = self.library.find_book("test book")
        self.assertIsNotNone(book)
        self.assertEqual(book.title, "Test Book")
    
    def test_find_book_not_found(self):
        """Test finding a non-existent book."""
        book = self.library.find_book("Non-existent Book")
        self.assertIsNone(book)
    
    def test_mark_book_as_read(self):
        """Test marking a book as read."""
        self.library.add_book("Test Book", "Test Author", is_read=False)
        result = self.library.mark_book_as_read("Test Book")
        self.assertTrue(result)
        book = self.library.find_book("Test Book")
        self.assertTrue(book.is_read)
    
    def test_mark_book_as_read_not_found(self):
        """Test marking a non-existent book as read."""
        result = self.library.mark_book_as_read("Non-existent Book")
        self.assertFalse(result)
    
    def test_mark_book_as_unread(self):
        """Test marking a book as unread."""
        self.library.add_book("Test Book", "Test Author", is_read=True)
        result = self.library.mark_book_as_unread("Test Book")
        self.assertTrue(result)
        book = self.library.find_book("Test Book")
        self.assertFalse(book.is_read)
    
    def test_mark_book_as_unread_not_found(self):
        """Test marking a non-existent book as unread."""
        result = self.library.mark_book_as_unread("Non-existent Book")
        self.assertFalse(result)
    
    def test_save_and_load(self):
        """Test saving and loading the library."""
        self.library.add_book("Book 1", "Author 1", is_read=True)
        self.library.add_book("Book 2", "Author 2", is_read=False)
        
        # Create a new library instance with the same data file
        new_library = BookLibrary(data_file=self.temp_file.name)
        
        self.assertEqual(len(new_library.books), 2)
        book1 = new_library.find_book("Book 1")
        book2 = new_library.find_book("Book 2")
        
        self.assertIsNotNone(book1)
        self.assertIsNotNone(book2)
        self.assertTrue(book1.is_read)
        self.assertFalse(book2.is_read)


if __name__ == "__main__":
    unittest.main()
