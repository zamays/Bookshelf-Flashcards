"""
Book parser module for reading book titles from files.
"""
import csv
from typing import List, Tuple, Optional


def _is_csv_file(file_path: str) -> bool:
    """Check if file is a CSV based on extension."""
    return file_path.lower().endswith('.csv')


def _normalize_header(header: str) -> str:
    """Normalize header name for comparison."""
    return header.lower().strip()


def _find_column_index(headers: List[str], synonyms: List[str]) -> Optional[int]:
    """
    Find column index by checking header against synonyms.

    Args:
        headers: List of column headers from CSV
        synonyms: List of acceptable header names (already lowercase)

    Returns:
        Column index or None if not found
    """
    normalized_headers = [_normalize_header(h) for h in headers]
    for synonym in synonyms:
        if synonym in normalized_headers:
            return normalized_headers.index(synonym)
    return None


def parse_csv_file(file_path: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parse a CSV file containing book titles and optional authors.

    Recognizes columns with these headers (case-insensitive):
    - Title synonyms: title, name, book, book title, book name
    - Author synonyms: author, writer, by, author name, written by

    Args:
        file_path: Path to the CSV file

    Returns:
        List of tuples (title, author or None)

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
        UnicodeDecodeError: If the file encoding is invalid
        ValueError: If CSV has no title column
    """
    title_synonyms = ['title', 'name', 'book', 'book title', 'book name']
    author_synonyms = ['author', 'writer', 'by', 'author name', 'written by']

    books = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        # Read header row
        try:
            headers = next(reader)
        except StopIteration:
            # Empty file
            return books

        # Find title and author columns
        title_idx = _find_column_index(headers, title_synonyms)
        author_idx = _find_column_index(headers, author_synonyms)

        if title_idx is None:
            raise ValueError("CSV file must have a column with title information "
                           "(acceptable headers: title, name, book, etc.)")

        # Read data rows
        for row in reader:
            if not row or len(row) <= title_idx:
                continue

            title = row[title_idx].strip()
            if not title:
                continue

            author = None
            if author_idx is not None and len(row) > author_idx:
                author = row[author_idx].strip()
                if not author:
                    author = None

            books.append((title, author))

    return books


def parse_book_file(file_path: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parse a file containing book titles and optional authors.

    Supports both text files and CSV files:

    Text file formats:
    - "Title by Author"
    - "Title - Author"
    - "Title" (author will be None)

    CSV file format:
    - Must have header row
    - Title column: title, name, book, book title, book name (case-insensitive)
    - Author column (optional): author, writer, by, author name, written by (case-insensitive)

    Args:
        file_path: Path to the file containing book titles

    Returns:
        List of tuples (title, author or None)

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
        UnicodeDecodeError: If the file encoding is invalid
        ValueError: If CSV file has no title column
    """
    if _is_csv_file(file_path):
        return parse_csv_file(file_path)

    books = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            # Try to parse "Title by Author" format
            if ' by ' in line:
                parts = line.split(' by ', 1)
                title = parts[0].strip()
                author = parts[1].strip()
                books.append((title, author))
            # Try to parse "Title - Author" format
            elif ' - ' in line:
                parts = line.split(' - ', 1)
                title = parts[0].strip()
                author = parts[1].strip()
                books.append((title, author))
            else:
                # No author specified
                books.append((line.strip(), None))

    return books
