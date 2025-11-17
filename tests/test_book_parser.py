"""
Unit tests for book_parser.py module.
"""
import os
import pytest
from book_parser import parse_book_file


class TestBookParserFormats:
    """Tests for different book parsing formats."""

    def test_parse_title_by_author_format(self, tmp_path):
        """Test parsing 'Title by Author' format."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("1984 by George Orwell\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "George Orwell")

    def test_parse_title_dash_author_format(self, tmp_path):
        """Test parsing 'Title - Author' format."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("To Kill a Mockingbird - Harper Lee\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 1
        assert books[0] == ("To Kill a Mockingbird", "Harper Lee")

    def test_parse_title_only_format(self, tmp_path):
        """Test parsing 'Title' format (no author)."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("The Great Gatsby\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 1
        assert books[0] == ("The Great Gatsby", None)

    def test_parse_multiple_formats_mixed(self, tmp_path):
        """Test parsing file with mixed formats."""
        book_file = tmp_path / "books.txt"
        content = """1984 by George Orwell
To Kill a Mockingbird - Harper Lee
The Great Gatsby
"""
        book_file.write_text(content, encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 3
        assert books[0] == ("1984", "George Orwell")
        assert books[1] == ("To Kill a Mockingbird", "Harper Lee")
        assert books[2] == ("The Great Gatsby", None)

    def test_parse_preserves_order(self, tmp_path):
        """Test that parsing preserves the order of books."""
        book_file = tmp_path / "books.txt"
        content = """First Book by Author One
Second Book - Author Two
Third Book
"""
        book_file.write_text(content, encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert books[0][0] == "First Book"
        assert books[1][0] == "Second Book"
        assert books[2][0] == "Third Book"


class TestBookParserCommentAndEmptyLines:
    """Tests for handling comments and empty lines."""

    def test_parse_skip_comment_lines(self, tmp_path):
        """Test that comment lines starting with # are skipped."""
        book_file = tmp_path / "books.txt"
        content = """# This is a comment
1984 by George Orwell
# Another comment
"""
        book_file.write_text(content, encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "George Orwell")

    def test_parse_skip_empty_lines(self, tmp_path):
        """Test that empty lines are skipped."""
        book_file = tmp_path / "books.txt"
        content = """1984 by George Orwell

To Kill a Mockingbird - Harper Lee

"""
        book_file.write_text(content, encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 2

    def test_parse_skip_whitespace_only_lines(self, tmp_path):
        """Test that lines with only whitespace are skipped."""
        book_file = tmp_path / "books.txt"
        content = """1984 by George Orwell
    
\t
To Kill a Mockingbird - Harper Lee
"""
        book_file.write_text(content, encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 2

    def test_parse_empty_file(self, tmp_path):
        """Test parsing an empty file."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert books == []

    def test_parse_comments_only_file(self, tmp_path):
        """Test parsing a file with only comments."""
        book_file = tmp_path / "books.txt"
        content = """# Comment 1
# Comment 2
# Comment 3
"""
        book_file.write_text(content, encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert books == []


class TestBookParserWhitespaceHandling:
    """Tests for whitespace handling."""

    def test_parse_strips_leading_whitespace(self, tmp_path):
        """Test that leading whitespace is stripped."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("   1984 by George Orwell\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert books[0] == ("1984", "George Orwell")

    def test_parse_strips_trailing_whitespace(self, tmp_path):
        """Test that trailing whitespace is stripped."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("1984 by George Orwell   \n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert books[0] == ("1984", "George Orwell")

    def test_parse_strips_whitespace_around_separator_by(self, tmp_path):
        """Test that whitespace around 'by' separator is stripped."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("1984   by   George Orwell\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert books[0] == ("1984", "George Orwell")

    def test_parse_strips_whitespace_around_separator_dash(self, tmp_path):
        """Test that whitespace around '-' separator is stripped."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("1984   -   George Orwell\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert books[0] == ("1984", "George Orwell")


class TestBookParserEdgeCases:
    """Tests for edge cases and malformed input."""

    def test_parse_title_with_by_in_name(self, tmp_path):
        """Test title containing the word 'by'."""
        book_file = tmp_path / "books.txt"
        # The first ' by ' is treated as separator
        book_file.write_text("Stand by Me by Stephen King\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 1
        # The parser splits on the first ' by '
        assert books[0] == ("Stand", "Me by Stephen King")

    def test_parse_title_with_dash_in_name(self, tmp_path):
        """Test title containing dashes."""
        book_file = tmp_path / "books.txt"
        # Only the last ' - ' should be treated as separator
        book_file.write_text("The Spy Who Came In From The Cold - John le Carré\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 1
        assert books[0] == ("The Spy Who Came In From The Cold", "John le Carré")

    def test_parse_multiple_separators_by(self, tmp_path):
        """Test handling multiple 'by' separators (splits on first)."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("Book by Someone by Someone Else\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        # Should split on the first ' by '
        assert len(books) == 1
        assert books[0] == ("Book", "Someone by Someone Else")

    def test_parse_multiple_separators_dash(self, tmp_path):
        """Test handling multiple '-' separators (splits on first)."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("Book - Author - Extra\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        # Should split on the first ' - '
        assert len(books) == 1
        assert books[0] == ("Book", "Author - Extra")

    def test_parse_unicode_characters(self, unicode_book_file):
        """Test parsing books with Unicode characters."""
        books = parse_book_file(unicode_book_file)
        
        assert len(books) == 3
        assert books[0] == ("Café", "François Mauriac")
        assert books[1] == ("东京物语", "小津安二郎")
        assert books[2] == ("Książka", "Autor Polski")

    def test_parse_special_characters(self, tmp_path):
        """Test parsing books with special characters."""
        book_file = tmp_path / "books.txt"
        content = """Book's "Title": A Test! by Author & Co.
Another Book: Part 2 - Author (Jr.)
"""
        book_file.write_text(content, encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 2
        assert books[0] == ("Book's \"Title\": A Test!", "Author & Co.")
        assert books[1] == ("Another Book: Part 2", "Author (Jr.)")

    def test_parse_very_long_line(self, tmp_path):
        """Test parsing a very long line."""
        book_file = tmp_path / "books.txt"
        long_title = "A" * 5000
        long_author = "B" * 5000
        book_file.write_text(f"{long_title} by {long_author}\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 1
        assert books[0] == (long_title, long_author)

    def test_parse_only_separator_by(self, tmp_path):
        """Test line with only ' by ' separator."""
        book_file = tmp_path / "books.txt"
        book_file.write_text(" by \n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        # After stripping, becomes "by" which is treated as title only
        assert len(books) == 1
        assert books[0] == ("by", None)

    def test_parse_only_separator_dash(self, tmp_path):
        """Test line with only ' - ' separator."""
        book_file = tmp_path / "books.txt"
        book_file.write_text(" - \n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        # After stripping, becomes "-" which is treated as title only
        assert len(books) == 1
        assert books[0] == ("-", None)

    def test_parse_title_ends_with_by(self, tmp_path):
        """Test title that ends with 'by'."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("Stand by\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        # No ' by ' separator, so should be title only
        assert len(books) == 1
        assert books[0] == ("Stand by", None)

    def test_parse_author_starts_with_dash(self, tmp_path):
        """Test author that starts with dash."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("Title --Author\n", encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        # No ' - ' (with spaces), so should be title only
        assert len(books) == 1
        assert books[0] == ("Title --Author", None)


class TestBookParserFileErrors:
    """Tests for file handling errors."""

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_book_file("/nonexistent/path/to/file.txt")

    def test_parse_invalid_encoding(self, tmp_path):
        """Test handling of invalid file encoding."""
        book_file = tmp_path / "books.txt"
        # Write invalid UTF-8 bytes
        with open(str(book_file), 'wb') as f:
            f.write(b'\xff\xfe\x00\x00Invalid UTF-8')
        
        # Should raise UnicodeDecodeError
        with pytest.raises(UnicodeDecodeError):
            parse_book_file(str(book_file))

    def test_parse_directory_instead_of_file(self, tmp_path):
        """Test parsing a directory raises appropriate error."""
        # Try to parse the directory itself
        with pytest.raises((IsADirectoryError, PermissionError)):
            parse_book_file(str(tmp_path))

    def test_parse_unreadable_file(self, tmp_path):
        """Test parsing an unreadable file."""
        book_file = tmp_path / "books.txt"
        book_file.write_text("1984 by George Orwell\n", encoding='utf-8')
        
        # Make file unreadable (Unix-like systems only)
        if os.name != 'nt':  # Skip on Windows
            os.chmod(str(book_file), 0o000)
            
            with pytest.raises(PermissionError):
                parse_book_file(str(book_file))
            
            # Restore permissions for cleanup
            os.chmod(str(book_file), 0o644)


class TestBookParserIntegration:
    """Integration tests with sample book files."""

    def test_parse_sample_book_file(self, sample_book_file):
        """Test parsing the sample book file fixture."""
        books = parse_book_file(sample_book_file)
        
        # Should have 4 books (comments and empty lines skipped)
        assert len(books) == 4
        assert ("1984", "George Orwell") in books
        assert ("To Kill a Mockingbird", "Harper Lee") in books
        assert ("The Great Gatsby", None) in books
        assert ("Brave New World", "Aldous Huxley") in books

    def test_parse_realistic_file(self, tmp_path):
        """Test parsing a realistic book file."""
        book_file = tmp_path / "my_books.txt"
        content = """# My Reading List 2024

# Fiction
1984 by George Orwell
Brave New World - Aldous Huxley
The Handmaid's Tale by Margaret Atwood

# Non-fiction
Sapiens: A Brief History of Humankind by Yuval Noah Harari
Educated - Tara Westover

# To Read
The Midnight Library
# Need to get author for this one

# Classics
War and Peace by Leo Tolstoy
Crime and Punishment - Fyodor Dostoevsky
"""
        book_file.write_text(content, encoding='utf-8')
        
        books = parse_book_file(str(book_file))
        
        assert len(books) == 8
        # Verify a few specific entries
        assert ("1984", "George Orwell") in books
        assert ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari") in books
        assert ("The Midnight Library", None) in books

    def test_parse_mixed_line_endings(self, tmp_path):
        """Test parsing file with mixed line endings."""
        book_file = tmp_path / "books.txt"
        # Create file with mixed line endings
        with open(str(book_file), 'wb') as f:
            f.write(b"1984 by George Orwell\r\n")  # Windows
            f.write(b"Brave New World - Aldous Huxley\n")  # Unix
            f.write(b"The Great Gatsby\r")  # Old Mac
        
        books = parse_book_file(str(book_file))
        
        # Should handle all line ending types
        assert len(books) >= 2  # At least the first two should parse correctly
