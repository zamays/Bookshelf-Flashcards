"""
Unit tests for CSV parsing in book_parser.py module.
"""
import os
import pytest
from book_parser import parse_book_file, parse_csv_file


class TestCSVParserBasic:
    """Tests for basic CSV parsing functionality."""

    def test_parse_csv_with_title_and_author(self, tmp_path):
        """Test parsing CSV with standard Title and Author headers."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author\n"
            "1984,George Orwell\n"
            "To Kill a Mockingbird,Harper Lee\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 2
        assert books[0] == ("1984", "George Orwell")
        assert books[1] == ("To Kill a Mockingbird", "Harper Lee")

    def test_parse_csv_with_title_only(self, tmp_path):
        """Test parsing CSV with only Title column."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title\n"
            "1984\n"
            "The Great Gatsby\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 2
        assert books[0] == ("1984", None)
        assert books[1] == ("The Great Gatsby", None)

    def test_parse_csv_extra_columns(self, tmp_path):
        """Test parsing CSV with extra columns that are ignored."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author,Year,Genre\n"
            "1984,George Orwell,1949,Dystopian\n"
            "Brave New World,Aldous Huxley,1932,Science Fiction\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 2
        assert books[0] == ("1984", "George Orwell")
        assert books[1] == ("Brave New World", "Aldous Huxley")


class TestCSVParserSynonyms:
    """Tests for synonym support in CSV headers."""

    def test_parse_csv_title_synonym_name(self, tmp_path):
        """Test parsing CSV with 'Name' as title column."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Name,Author\n"
            "1984,George Orwell\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "George Orwell")

    def test_parse_csv_title_synonym_book(self, tmp_path):
        """Test parsing CSV with 'Book' as title column."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Book,Writer\n"
            "The Great Gatsby,F. Scott Fitzgerald\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("The Great Gatsby", "F. Scott Fitzgerald")

    def test_parse_csv_author_synonym_writer(self, tmp_path):
        """Test parsing CSV with 'Writer' as author column."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Writer\n"
            "1984,George Orwell\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "George Orwell")

    def test_parse_csv_author_synonym_by(self, tmp_path):
        """Test parsing CSV with 'By' as author column."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Book,By\n"
            "Dune,Frank Herbert\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("Dune", "Frank Herbert")

    def test_parse_csv_case_insensitive_headers(self, tmp_path):
        """Test that header matching is case-insensitive."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "TITLE,AUTHOR\n"
            "1984,George Orwell\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "George Orwell")

    def test_parse_csv_mixed_case_headers(self, tmp_path):
        """Test parsing with mixed case headers."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "TiTLe,AuThOr\n"
            "1984,George Orwell\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "George Orwell")

    def test_parse_csv_book_title_synonym(self, tmp_path):
        """Test parsing CSV with 'Book Title' as column name."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Book Title,Author Name\n"
            "1984,George Orwell\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "George Orwell")


class TestCSVParserEdgeCases:
    """Tests for edge cases in CSV parsing."""

    def test_parse_csv_empty_file(self, tmp_path):
        """Test parsing an empty CSV file."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text("", encoding='utf-8')
        
        books = parse_csv_file(str(csv_file))
        
        assert books == []

    def test_parse_csv_header_only(self, tmp_path):
        """Test parsing CSV with only headers."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text("Title,Author\n", encoding='utf-8')
        
        books = parse_csv_file(str(csv_file))
        
        assert books == []

    def test_parse_csv_empty_rows(self, tmp_path):
        """Test parsing CSV with empty rows."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author\n"
            "1984,George Orwell\n"
            "\n"
            "The Great Gatsby,F. Scott Fitzgerald\n"
            ",\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 2
        assert books[0] == ("1984", "George Orwell")
        assert books[1] == ("The Great Gatsby", "F. Scott Fitzgerald")

    def test_parse_csv_empty_title(self, tmp_path):
        """Test that rows with empty titles are skipped."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author\n"
            ",George Orwell\n"
            "1984,Harper Lee\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "Harper Lee")

    def test_parse_csv_empty_author(self, tmp_path):
        """Test that empty author fields result in None."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author\n"
            "1984,\n"
            "The Great Gatsby,F. Scott Fitzgerald\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 2
        assert books[0] == ("1984", None)
        assert books[1] == ("The Great Gatsby", "F. Scott Fitzgerald")

    def test_parse_csv_whitespace_handling(self, tmp_path):
        """Test that whitespace is stripped from values."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author\n"
            "  1984  ,  George Orwell  \n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "George Orwell")

    def test_parse_csv_quoted_values(self, tmp_path):
        """Test parsing CSV with quoted values containing commas."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            'Title,Author\n'
            '"The Spy Who Came In from the Cold",John le Carré\n'
            '"Book, The: A Story","Author, Name"\n',
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 2
        assert books[0] == ("The Spy Who Came In from the Cold", "John le Carré")
        assert books[1] == ("Book, The: A Story", "Author, Name")

    def test_parse_csv_unicode_characters(self, tmp_path):
        """Test parsing CSV with Unicode characters."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author\n"
            "Café,François Mauriac\n"
            "东京物语,小津安二郎\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 2
        assert books[0] == ("Café", "François Mauriac")
        assert books[1] == ("东京物语", "小津安二郎")

    def test_parse_csv_special_characters(self, tmp_path):
        """Test parsing CSV with special characters."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author\n"
            "Book's \"Title\": A Test!,Author & Co.\n",
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("Book's \"Title\": A Test!", "Author & Co.")

    def test_parse_csv_no_title_column_raises_error(self, tmp_path):
        """Test that CSV without title column raises ValueError."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Author,Year\n"
            "George Orwell,1949\n",
            encoding='utf-8'
        )
        
        with pytest.raises(ValueError, match="title information"):
            parse_csv_file(str(csv_file))

    def test_parse_csv_incomplete_rows(self, tmp_path):
        """Test parsing CSV with incomplete rows."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author,Year\n"
            "1984,George Orwell,1949\n"
            "The Great Gatsby\n"  # Missing author and year
            "Brave New World,Aldous Huxley\n",  # Missing year
            encoding='utf-8'
        )
        
        books = parse_csv_file(str(csv_file))
        
        assert len(books) == 3
        assert books[0] == ("1984", "George Orwell")
        assert books[1] == ("The Great Gatsby", None)
        assert books[2] == ("Brave New World", "Aldous Huxley")


class TestCSVParserIntegration:
    """Integration tests for CSV parsing through parse_book_file."""

    def test_parse_book_file_detects_csv(self, tmp_path):
        """Test that parse_book_file detects and parses CSV files."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author\n"
            "1984,George Orwell\n"
            "The Great Gatsby,F. Scott Fitzgerald\n",
            encoding='utf-8'
        )
        
        books = parse_book_file(str(csv_file))
        
        assert len(books) == 2
        assert books[0] == ("1984", "George Orwell")
        assert books[1] == ("The Great Gatsby", "F. Scott Fitzgerald")

    def test_parse_book_file_csv_case_insensitive(self, tmp_path):
        """Test that CSV detection is case-insensitive."""
        csv_file = tmp_path / "books.CSV"
        csv_file.write_text(
            "Title,Author\n"
            "1984,George Orwell\n",
            encoding='utf-8'
        )
        
        books = parse_book_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "George Orwell")

    def test_parse_book_file_still_handles_txt(self, tmp_path):
        """Test that text file parsing still works."""
        txt_file = tmp_path / "books.txt"
        txt_file.write_text(
            "1984 by George Orwell\n"
            "The Great Gatsby - F. Scott Fitzgerald\n",
            encoding='utf-8'
        )
        
        books = parse_book_file(str(txt_file))
        
        assert len(books) == 2
        assert books[0] == ("1984", "George Orwell")
        assert books[1] == ("The Great Gatsby", "F. Scott Fitzgerald")

    def test_parse_realistic_csv_file(self, tmp_path):
        """Test parsing a realistic CSV file with various synonyms."""
        csv_file = tmp_path / "my_books.csv"
        csv_file.write_text(
            "Book Title,Author Name,Year,Rating\n"
            "1984,George Orwell,1949,5\n"
            "Brave New World,Aldous Huxley,1932,4\n"
            "The Handmaid's Tale,Margaret Atwood,1985,5\n",
            encoding='utf-8'
        )
        
        books = parse_book_file(str(csv_file))
        
        assert len(books) == 3
        assert ("1984", "George Orwell") in books
        assert ("Brave New World", "Aldous Huxley") in books
        assert ("The Handmaid's Tale", "Margaret Atwood") in books

    def test_parse_csv_with_different_delimiter_still_uses_comma(self, tmp_path):
        """Test that we use standard comma delimiter."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text(
            "Title,Author\n"
            "1984,George Orwell\n",
            encoding='utf-8'
        )
        
        books = parse_book_file(str(csv_file))
        
        assert len(books) == 1
        assert books[0] == ("1984", "George Orwell")


class TestCSVParserFileErrors:
    """Tests for file handling errors in CSV parsing."""

    def test_parse_csv_nonexistent_file(self):
        """Test parsing a nonexistent CSV file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_csv_file("/nonexistent/path/to/file.csv")

    def test_parse_csv_invalid_encoding(self, tmp_path):
        """Test handling of invalid file encoding in CSV."""
        csv_file = tmp_path / "books.csv"
        # Write invalid UTF-8 bytes
        with open(str(csv_file), 'wb') as f:
            f.write(b'\xff\xfe\x00\x00Invalid UTF-8')
        
        # Should raise UnicodeDecodeError
        with pytest.raises(UnicodeDecodeError):
            parse_csv_file(str(csv_file))

    def test_parse_csv_directory_instead_of_file(self, tmp_path):
        """Test parsing a directory raises appropriate error."""
        with pytest.raises((IsADirectoryError, PermissionError)):
            parse_csv_file(str(tmp_path))

    def test_parse_csv_unreadable_file(self, tmp_path):
        """Test parsing an unreadable CSV file."""
        csv_file = tmp_path / "books.csv"
        csv_file.write_text("Title,Author\n1984,George Orwell\n", encoding='utf-8')
        
        # Make file unreadable (Unix-like systems only)
        if os.name != 'nt':  # Skip on Windows
            os.chmod(str(csv_file), 0o000)
            
            with pytest.raises(PermissionError):
                parse_csv_file(str(csv_file))
            
            # Restore permissions for cleanup
            os.chmod(str(csv_file), 0o644)
