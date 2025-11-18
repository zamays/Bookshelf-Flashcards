"""
Unit tests for validation.py module.
"""
import os
import pytest
import tempfile
from pathlib import Path
from validation import (
    ValidationError,
    validate_title,
    validate_author,
    validate_summary,
    validate_book_id,
    validate_file_path,
    validate_filename,
    validate_file_size,
    validate_file_content,
    sanitize_html,
    validate_all_book_data,
    MAX_TITLE_LENGTH,
    MAX_AUTHOR_LENGTH,
    MAX_SUMMARY_LENGTH,
    MAX_FILE_SIZE,
)


class TestValidateTitle:
    """Tests for title validation."""
    
    def test_valid_title(self):
        """Test that a valid title passes validation."""
        title = "The Great Gatsby"
        result = validate_title(title)
        assert result == "The Great Gatsby"
    
    def test_title_with_unicode(self):
        """Test title with Unicode characters."""
        title = "Café Müller — 東京物語"
        result = validate_title(title)
        assert result == title
    
    def test_title_with_punctuation(self):
        """Test title with various punctuation."""
        title = "Book's Title: A \"Special\" Test & More!"
        result = validate_title(title)
        assert result == title
    
    def test_title_strips_whitespace(self):
        """Test that title whitespace is stripped."""
        title = "  The Great Gatsby  "
        result = validate_title(title)
        assert result == "The Great Gatsby"
    
    def test_empty_title_raises_error(self):
        """Test that empty title raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_title("")
    
    def test_whitespace_only_title_raises_error(self):
        """Test that whitespace-only title raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_title("   ")
    
    def test_title_exceeds_max_length(self):
        """Test that too-long title raises error."""
        long_title = "A" * (MAX_TITLE_LENGTH + 1)
        with pytest.raises(ValidationError, match="cannot exceed"):
            validate_title(long_title)
    
    def test_title_at_max_length(self):
        """Test title at exactly max length."""
        title = "A" * MAX_TITLE_LENGTH
        result = validate_title(title)
        assert len(result) == MAX_TITLE_LENGTH
    
    def test_title_with_script_tag_raises_error(self):
        """Test XSS prevention - script tag."""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_title("Title<script>alert('xss')</script>")
    
    def test_title_with_javascript_protocol_raises_error(self):
        """Test XSS prevention - javascript protocol."""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_title("javascript:alert('xss')")
    
    def test_title_with_onerror_raises_error(self):
        """Test XSS prevention - onerror attribute."""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_title("Title onerror=alert(1)")
    
    def test_title_with_iframe_raises_error(self):
        """Test XSS prevention - iframe tag."""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_title("<iframe src='evil.com'>")
    
    def test_title_with_null_byte_raises_error(self):
        """Test that null byte raises error."""
        with pytest.raises(ValidationError, match="control characters"):
            validate_title("Title\x00Bad")
    
    def test_title_with_newline_raises_error(self):
        """Test that newline raises error."""
        with pytest.raises(ValidationError, match="control characters"):
            validate_title("Title\nBad")
    
    def test_title_not_string_raises_error(self):
        """Test that non-string title raises error."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_title(123)
    
    def test_title_none_raises_error(self):
        """Test that None title raises error."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_title(None)


class TestValidateAuthor:
    """Tests for author validation."""
    
    def test_valid_author(self):
        """Test that a valid author passes validation."""
        author = "F. Scott Fitzgerald"
        result = validate_author(author)
        assert result == "F. Scott Fitzgerald"
    
    def test_author_with_unicode(self):
        """Test author with Unicode characters."""
        author = "François Lefèvre"
        result = validate_author(author)
        assert result == author
    
    def test_author_strips_whitespace(self):
        """Test that author whitespace is stripped."""
        author = "  George Orwell  "
        result = validate_author(author)
        assert result == "George Orwell"
    
    def test_empty_author_raises_error(self):
        """Test that empty author raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_author("")
    
    def test_author_exceeds_max_length(self):
        """Test that too-long author raises error."""
        long_author = "A" * (MAX_AUTHOR_LENGTH + 1)
        with pytest.raises(ValidationError, match="cannot exceed"):
            validate_author(long_author)
    
    def test_author_at_max_length(self):
        """Test author at exactly max length."""
        author = "A" * MAX_AUTHOR_LENGTH
        result = validate_author(author)
        assert len(result) == MAX_AUTHOR_LENGTH
    
    def test_author_with_script_tag_raises_error(self):
        """Test XSS prevention - script tag."""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_author("<script>alert('xss')</script>")
    
    def test_author_with_null_byte_raises_error(self):
        """Test that null byte raises error."""
        with pytest.raises(ValidationError, match="control characters"):
            validate_author("Author\x00Bad")
    
    def test_author_not_string_raises_error(self):
        """Test that non-string author raises error."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_author(123)


class TestValidateSummary:
    """Tests for summary validation."""
    
    def test_valid_summary(self):
        """Test that a valid summary passes validation."""
        summary = "A great book about literature and society."
        result = validate_summary(summary)
        assert result == summary
    
    def test_summary_none(self):
        """Test that None summary is allowed."""
        result = validate_summary(None)
        assert result is None
    
    def test_empty_summary_returns_none(self):
        """Test that empty summary returns None."""
        result = validate_summary("")
        assert result is None
    
    def test_whitespace_only_summary_returns_none(self):
        """Test that whitespace-only summary returns None."""
        result = validate_summary("   ")
        assert result is None
    
    def test_summary_strips_whitespace(self):
        """Test that summary whitespace is stripped."""
        summary = "  A summary  "
        result = validate_summary(summary)
        assert result == "A summary"
    
    def test_summary_exceeds_max_length(self):
        """Test that too-long summary raises error."""
        long_summary = "A" * (MAX_SUMMARY_LENGTH + 1)
        with pytest.raises(ValidationError, match="cannot exceed"):
            validate_summary(long_summary)
    
    def test_summary_at_max_length(self):
        """Test summary at exactly max length."""
        summary = "A" * MAX_SUMMARY_LENGTH
        result = validate_summary(summary)
        assert len(result) == MAX_SUMMARY_LENGTH
    
    def test_summary_with_script_tag_raises_error(self):
        """Test XSS prevention - script tag."""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_summary("Summary<script>alert('xss')</script>")
    
    def test_summary_with_null_byte_raises_error(self):
        """Test that null byte raises error."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_summary("Summary\x00Bad")
    
    def test_summary_with_newlines_allowed(self):
        """Test that newlines are allowed in summaries."""
        summary = "Line 1\nLine 2\nLine 3"
        result = validate_summary(summary)
        assert result == summary
    
    def test_summary_not_string_raises_error(self):
        """Test that non-string summary raises error."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_summary(123)


class TestValidateBookId:
    """Tests for book ID validation."""
    
    def test_valid_book_id(self):
        """Test that a valid book ID passes validation."""
        result = validate_book_id(1)
        assert result == 1
    
    def test_book_id_string_converted(self):
        """Test that string book ID is converted."""
        result = validate_book_id("42")
        assert result == 42
        assert isinstance(result, int)
    
    def test_book_id_zero_raises_error(self):
        """Test that zero book ID raises error."""
        with pytest.raises(ValidationError, match="positive"):
            validate_book_id(0)
    
    def test_book_id_negative_raises_error(self):
        """Test that negative book ID raises error."""
        with pytest.raises(ValidationError, match="positive"):
            validate_book_id(-1)
    
    def test_book_id_too_large_raises_error(self):
        """Test that too-large book ID raises error."""
        with pytest.raises(ValidationError, match="too large"):
            validate_book_id(2147483648)
    
    def test_book_id_invalid_string_raises_error(self):
        """Test that invalid string raises error."""
        with pytest.raises(ValidationError, match="valid integer"):
            validate_book_id("not_a_number")
    
    def test_book_id_none_raises_error(self):
        """Test that None raises error."""
        with pytest.raises(ValidationError, match="valid integer"):
            validate_book_id(None)
    
    def test_book_id_float_converted(self):
        """Test that float is converted to int."""
        result = validate_book_id(42.7)
        assert result == 42


class TestValidateFilePath:
    """Tests for file path validation."""
    
    def test_valid_file_path(self):
        """Test that a valid file path passes validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            Path(file_path).touch()
            result = validate_file_path(file_path)
            assert os.path.isabs(result)
    
    def test_file_path_resolved_to_absolute(self):
        """Test that relative path is resolved to absolute."""
        result = validate_file_path("validation.py")
        assert os.path.isabs(result)
    
    def test_file_path_with_null_byte_raises_error(self):
        """Test that null byte raises error."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_file_path("test\x00.txt")
    
    def test_file_path_traversal_with_base_dir(self):
        """Test path traversal prevention with base directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Try to access parent directory
            with pytest.raises(ValidationError, match="outside"):
                validate_file_path("../etc/passwd", base_dir=tmpdir)
    
    def test_file_path_within_base_dir(self):
        """Test that path within base directory is allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            result = validate_file_path(file_path, base_dir=tmpdir)
            assert result.startswith(tmpdir)
    
    def test_file_path_not_string_raises_error(self):
        """Test that non-string path raises error."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_file_path(123)


class TestValidateFilename:
    """Tests for filename validation."""
    
    def test_valid_filename(self):
        """Test that a valid filename passes validation."""
        result = validate_filename("test.txt")
        assert result == "test.txt"
    
    def test_filename_strips_whitespace(self):
        """Test that filename whitespace is stripped."""
        result = validate_filename("  test.txt  ")
        assert result == "test.txt"
    
    def test_empty_filename_raises_error(self):
        """Test that empty filename raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_filename("")
    
    def test_filename_too_long_raises_error(self):
        """Test that too-long filename raises error."""
        long_name = "a" * 300 + ".txt"
        with pytest.raises(ValidationError, match="cannot exceed"):
            validate_filename(long_name)
    
    def test_filename_with_path_separator_raises_error(self):
        """Test that path separator raises error."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_filename("path/to/file.txt")
    
    def test_filename_with_backslash_raises_error(self):
        """Test that backslash raises error."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_filename("path\\to\\file.txt")
    
    def test_filename_with_null_byte_raises_error(self):
        """Test that null byte raises error."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_filename("test\x00.txt")
    
    def test_hidden_filename_raises_error(self):
        """Test that hidden file raises error."""
        with pytest.raises(ValidationError, match="Hidden"):
            validate_filename(".hidden.txt")
    
    def test_filename_without_extension_raises_error(self):
        """Test that filename without extension raises error."""
        with pytest.raises(ValidationError, match="must have an extension"):
            validate_filename("noextension")
    
    def test_filename_with_invalid_extension_raises_error(self):
        """Test that invalid extension raises error."""
        with pytest.raises(ValidationError, match="Only"):
            validate_filename("test.exe")
    
    def test_filename_with_txt_extension(self):
        """Test that .txt extension is allowed."""
        result = validate_filename("test.txt")
        assert result == "test.txt"
    
    def test_filename_with_uppercase_extension(self):
        """Test that uppercase extension is normalized."""
        result = validate_filename("test.TXT")
        assert result == "test.TXT"  # Filename preserved, but extension checked case-insensitive


class TestValidateFileSize:
    """Tests for file size validation."""
    
    def test_valid_file_size(self):
        """Test that a valid file size passes validation."""
        validate_file_size(1024)  # Should not raise
    
    def test_file_size_zero_raises_error(self):
        """Test that zero size raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_file_size(0)
    
    def test_file_size_negative_raises_error(self):
        """Test that negative size raises error."""
        with pytest.raises(ValidationError, match="cannot be negative"):
            validate_file_size(-1)
    
    def test_file_size_too_large_raises_error(self):
        """Test that too-large size raises error."""
        with pytest.raises(ValidationError, match="cannot exceed"):
            validate_file_size(MAX_FILE_SIZE + 1)
    
    def test_file_size_at_max(self):
        """Test that max size is allowed."""
        validate_file_size(MAX_FILE_SIZE)  # Should not raise
    
    def test_file_size_not_int_raises_error(self):
        """Test that non-integer size raises error."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_file_size("1024")


class TestValidateFileContent:
    """Tests for file content validation."""
    
    def test_valid_file_content(self):
        """Test that valid text content passes validation."""
        content = b"This is valid text content.\nWith multiple lines."
        validate_file_content(content)  # Should not raise
    
    def test_file_content_with_unicode(self):
        """Test that Unicode content is valid."""
        content = "Hello 世界 Café".encode('utf-8')
        validate_file_content(content)  # Should not raise
    
    def test_file_content_empty(self):
        """Test that empty content is allowed."""
        content = b""
        validate_file_content(content)  # Should not raise
    
    def test_file_content_not_utf8_raises_error(self):
        """Test that non-UTF-8 content raises error."""
        content = b"\xff\xfe\xfd"  # Invalid UTF-8
        with pytest.raises(ValidationError, match="valid UTF-8"):
            validate_file_content(content)
    
    def test_file_content_with_null_bytes_raises_error(self):
        """Test that null bytes raise error."""
        content = b"Text\x00with\x00nulls"
        with pytest.raises(ValidationError, match="binary"):
            validate_file_content(content)
    
    def test_file_content_excessive_control_chars_raises_error(self):
        """Test that excessive control characters raise error."""
        # Create content with many control characters (but no null bytes)
        content = bytes([1 + (i % 31) for i in range(100)])  # Use control chars 1-31
        with pytest.raises(ValidationError, match="control characters|binary"):
            validate_file_content(content)
    
    def test_file_content_not_bytes_raises_error(self):
        """Test that non-bytes content raises error."""
        with pytest.raises(ValidationError, match="must be bytes"):
            validate_file_content("string not bytes")


class TestSanitizeHtml:
    """Tests for HTML sanitization."""
    
    def test_sanitize_html_basic(self):
        """Test basic HTML escaping."""
        result = sanitize_html("Hello <script>alert('xss')</script>")
        assert "&lt;script&gt;" in result
        assert "<script>" not in result
    
    def test_sanitize_html_quotes(self):
        """Test that quotes are escaped."""
        result = sanitize_html('He said "hello"')
        assert "&quot;" in result
    
    def test_sanitize_html_ampersand(self):
        """Test that ampersand is escaped."""
        result = sanitize_html("Tom & Jerry")
        assert "&amp;" in result
    
    def test_sanitize_html_less_than(self):
        """Test that < is escaped."""
        result = sanitize_html("5 < 10")
        assert "&lt;" in result
    
    def test_sanitize_html_greater_than(self):
        """Test that > is escaped."""
        result = sanitize_html("10 > 5")
        assert "&gt;" in result
    
    def test_sanitize_html_complex_xss(self):
        """Test complex XSS attempt."""
        xss = '<img src=x onerror="alert(1)">'
        result = sanitize_html(xss)
        assert "onerror" not in result or "&quot;" in result
        assert "<img" not in result
    
    def test_sanitize_html_non_string(self):
        """Test that non-string is converted."""
        result = sanitize_html(123)
        assert result == "123"


class TestValidateAllBookData:
    """Tests for validating all book data at once."""
    
    def test_validate_all_valid_data(self):
        """Test that valid data passes validation."""
        title, author, summary = validate_all_book_data(
            "1984",
            "George Orwell",
            "A dystopian novel"
        )
        assert title == "1984"
        assert author == "George Orwell"
        assert summary == "A dystopian novel"
    
    def test_validate_all_with_none_summary(self):
        """Test validation with None summary."""
        title, author, summary = validate_all_book_data(
            "1984",
            "George Orwell",
            None
        )
        assert title == "1984"
        assert author == "George Orwell"
        assert summary is None
    
    def test_validate_all_strips_whitespace(self):
        """Test that all fields have whitespace stripped."""
        title, author, summary = validate_all_book_data(
            "  1984  ",
            "  George Orwell  ",
            "  A dystopian novel  "
        )
        assert title == "1984"
        assert author == "George Orwell"
        assert summary == "A dystopian novel"
    
    def test_validate_all_invalid_title_raises_error(self):
        """Test that invalid title raises error."""
        with pytest.raises(ValidationError):
            validate_all_book_data("", "George Orwell", None)
    
    def test_validate_all_invalid_author_raises_error(self):
        """Test that invalid author raises error."""
        with pytest.raises(ValidationError):
            validate_all_book_data("1984", "", None)
    
    def test_validate_all_invalid_summary_raises_error(self):
        """Test that invalid summary raises error."""
        long_summary = "A" * (MAX_SUMMARY_LENGTH + 1)
        with pytest.raises(ValidationError):
            validate_all_book_data("1984", "George Orwell", long_summary)


class TestValidationLogging:
    """Tests to ensure validation failures are logged."""
    
    def test_validation_error_logged(self, caplog):
        """Test that validation errors are logged."""
        import logging
        caplog.set_level(logging.WARNING)
        
        try:
            validate_title("")
        except ValidationError:
            pass
        
        # Check that something was logged
        assert len(caplog.records) > 0
        assert "validation failed" in caplog.text.lower()
