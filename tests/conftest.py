"""
Shared test fixtures for pytest.
"""
import os
import tempfile
import pytest
from unittest.mock import MagicMock, Mock


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def mock_db_connection():
    """Mock database connection for isolated testing."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def mock_genai_model():
    """Mock Google Generative AI model."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is a test summary of the book."
    mock_model.generate_content.return_value = mock_response
    return mock_model


@pytest.fixture
def sample_books():
    """Sample book data for testing."""
    return [
        ("1984", "George Orwell"),
        ("To Kill a Mockingbird", "Harper Lee"),
        ("The Great Gatsby", "F. Scott Fitzgerald"),
    ]


@pytest.fixture
def sample_book_file(tmp_path):
    """Create a temporary book file with sample data."""
    book_file = tmp_path / "test_books.txt"
    content = """# Test books
1984 by George Orwell
To Kill a Mockingbird - Harper Lee
The Great Gatsby
# Another comment
Brave New World by Aldous Huxley
"""
    book_file.write_text(content, encoding='utf-8')
    return str(book_file)


@pytest.fixture
def unicode_book_file(tmp_path):
    """Create a temporary book file with Unicode characters."""
    book_file = tmp_path / "unicode_books.txt"
    content = """Café by François Mauriac
东京物语 by 小津安二郎
Książka - Autor Polski
"""
    book_file.write_text(content, encoding='utf-8')
    return str(book_file)


@pytest.fixture(autouse=True)
def cleanup_env():
    """Clean up environment variables after each test."""
    yield
    # This runs after each test
    if 'GOOGLE_AI_API_KEY' in os.environ:
        original_key = os.environ.get('GOOGLE_AI_API_KEY')
        yield
        if original_key:
            os.environ['GOOGLE_AI_API_KEY'] = original_key
