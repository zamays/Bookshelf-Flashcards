"""
Book parser module for reading book titles from files.
"""
from typing import List, Tuple


def parse_book_file(file_path: str) -> List[Tuple[str, str]]:
    """
    Parse a file containing book titles and optional authors.
    
    Expected formats:
    - "Title by Author"
    - "Title - Author"
    - "Title" (author will be None)
    
    Args:
        file_path: Path to the file containing book titles
        
    Returns:
        List of tuples (title, author or None)
    """
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
