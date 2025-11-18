"""
Input validation module to prevent injection attacks and data corruption.

This module provides validators for all user inputs including:
- Book titles, authors, and summaries
- File paths and uploads
- Database IDs
- HTML output sanitization
"""

import os
import re
import html
from typing import Optional, Tuple
from pathlib import Path
import logging

# Set up logging for security monitoring
logger = logging.getLogger(__name__)

# Length limits
MAX_TITLE_LENGTH = 500
MAX_AUTHOR_LENGTH = 200
MAX_SUMMARY_LENGTH = 10000
MAX_FILENAME_LENGTH = 255

# File upload constraints
ALLOWED_EXTENSIONS = {'txt'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Allowed characters patterns
# Allow letters (including Unicode), numbers, common punctuation, and whitespace
TITLE_PATTERN = re.compile(r'^[\w\s\.,;:!?\'\"\-–—()&\[\]{}*+/\\@#$%€£¥©®™]+$', re.UNICODE)
AUTHOR_PATTERN = re.compile(r'^[\w\s\.,\'\-]+$', re.UNICODE)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_title(title: str) -> str:
    """
    Validate and sanitize a book title.
    
    Args:
        title: The book title to validate
        
    Returns:
        Sanitized title string
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(title, str):
        logger.warning(f"Title validation failed: not a string (type: {type(title).__name__})")
        raise ValidationError("Title must be a string")
    
    # Strip whitespace
    title = title.strip()
    
    # Check if empty
    if not title:
        logger.warning("Title validation failed: empty string")
        raise ValidationError("Title cannot be empty")
    
    # Check length
    if len(title) > MAX_TITLE_LENGTH:
        logger.warning(f"Title validation failed: length {len(title)} exceeds maximum {MAX_TITLE_LENGTH}")
        raise ValidationError(f"Title cannot exceed {MAX_TITLE_LENGTH} characters")
    
    # Check for allowed characters (relaxed pattern)
    # We allow most Unicode characters for international book titles
    # but prevent control characters and potential XSS patterns
    if '\x00' in title or '\r' in title or '\n' in title or '\t' in title:
        logger.warning("Title validation failed: contains control characters")
        raise ValidationError("Title contains invalid control characters")
    
    # Check for potential XSS patterns (basic check)
    dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=', '<iframe', 'eval(']
    title_lower = title.lower()
    for pattern in dangerous_patterns:
        if pattern in title_lower:
            logger.warning(f"Title validation failed: contains dangerous pattern '{pattern}'")
            raise ValidationError("Title contains potentially dangerous content")
    
    return title


def validate_author(author: str) -> str:
    """
    Validate and sanitize an author name.
    
    Args:
        author: The author name to validate
        
    Returns:
        Sanitized author string
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(author, str):
        logger.warning(f"Author validation failed: not a string (type: {type(author).__name__})")
        raise ValidationError("Author must be a string")
    
    # Strip whitespace
    author = author.strip()
    
    # Check if empty
    if not author:
        logger.warning("Author validation failed: empty string")
        raise ValidationError("Author cannot be empty")
    
    # Check length
    if len(author) > MAX_AUTHOR_LENGTH:
        logger.warning(f"Author validation failed: length {len(author)} exceeds maximum {MAX_AUTHOR_LENGTH}")
        raise ValidationError(f"Author name cannot exceed {MAX_AUTHOR_LENGTH} characters")
    
    # Check for control characters
    if '\x00' in author or '\r' in author or '\n' in author or '\t' in author:
        logger.warning("Author validation failed: contains control characters")
        raise ValidationError("Author name contains invalid control characters")
    
    # Check for potential XSS patterns
    dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=', '<iframe', 'eval(']
    author_lower = author.lower()
    for pattern in dangerous_patterns:
        if pattern in author_lower:
            logger.warning(f"Author validation failed: contains dangerous pattern '{pattern}'")
            raise ValidationError("Author name contains potentially dangerous content")
    
    return author


def validate_summary(summary: Optional[str]) -> Optional[str]:
    """
    Validate and sanitize a book summary.
    
    Args:
        summary: The book summary to validate (can be None)
        
    Returns:
        Sanitized summary string or None
        
    Raises:
        ValidationError: If validation fails
    """
    if summary is None:
        return None
    
    if not isinstance(summary, str):
        logger.warning(f"Summary validation failed: not a string (type: {type(summary).__name__})")
        raise ValidationError("Summary must be a string or None")
    
    # Strip whitespace
    summary = summary.strip()
    
    # Empty summaries are allowed (return None)
    if not summary:
        return None
    
    # Check length
    if len(summary) > MAX_SUMMARY_LENGTH:
        logger.warning(f"Summary validation failed: length {len(summary)} exceeds maximum {MAX_SUMMARY_LENGTH}")
        raise ValidationError(f"Summary cannot exceed {MAX_SUMMARY_LENGTH} characters")
    
    # Check for null bytes
    if '\x00' in summary:
        logger.warning("Summary validation failed: contains null bytes")
        raise ValidationError("Summary contains invalid characters")
    
    # Check for potential XSS patterns
    dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=', '<iframe', 'eval(']
    summary_lower = summary.lower()
    for pattern in dangerous_patterns:
        if pattern in summary_lower:
            logger.warning(f"Summary validation failed: contains dangerous pattern '{pattern}'")
            raise ValidationError("Summary contains potentially dangerous content")
    
    return summary


def validate_book_id(book_id: any) -> int:
    """
    Validate a database book ID.
    
    Args:
        book_id: The book ID to validate
        
    Returns:
        Validated integer book ID
        
    Raises:
        ValidationError: If validation fails
    """
    # Try to convert to integer
    try:
        book_id = int(book_id)
    except (ValueError, TypeError):
        logger.warning(f"Book ID validation failed: cannot convert '{book_id}' to integer")
        raise ValidationError("Book ID must be a valid integer")
    
    # Check range (must be positive)
    if book_id <= 0:
        logger.warning(f"Book ID validation failed: invalid value {book_id}")
        raise ValidationError("Book ID must be a positive integer")
    
    # Check reasonable upper bound (to prevent memory issues)
    if book_id > 2147483647:  # Max 32-bit signed integer
        logger.warning(f"Book ID validation failed: value {book_id} too large")
        raise ValidationError("Book ID value is too large")
    
    return book_id


def validate_file_path(file_path: str, base_dir: Optional[str] = None) -> str:
    """
    Validate a file path to prevent path traversal attacks.
    
    Args:
        file_path: The file path to validate
        base_dir: Optional base directory to constrain the path within
        
    Returns:
        Sanitized absolute file path
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(file_path, str):
        logger.warning(f"File path validation failed: not a string (type: {type(file_path).__name__})")
        raise ValidationError("File path must be a string")
    
    # Check for null bytes
    if '\x00' in file_path:
        logger.warning("File path validation failed: contains null bytes")
        raise ValidationError("File path contains invalid characters")
    
    # Resolve to absolute path and normalize
    try:
        resolved_path = Path(file_path).resolve()
    except (ValueError, RuntimeError) as e:
        logger.warning(f"File path validation failed: cannot resolve path '{file_path}': {e}")
        raise ValidationError("Invalid file path")
    
    # If base_dir is provided, ensure the path is within it
    if base_dir:
        try:
            base_path = Path(base_dir).resolve()
            # Check if resolved_path is within base_path
            resolved_path.relative_to(base_path)
        except ValueError:
            logger.warning(f"File path validation failed: path '{file_path}' is outside base directory '{base_dir}'")
            raise ValidationError("File path is outside allowed directory")
    
    # Check for suspicious patterns
    path_str = str(resolved_path)
    suspicious_patterns = ['..', '~/', '$HOME']
    original_lower = file_path.lower()
    for pattern in suspicious_patterns:
        if pattern in original_lower and pattern in path_str:
            logger.warning(f"File path validation failed: contains suspicious pattern '{pattern}'")
            raise ValidationError("File path contains suspicious patterns")
    
    return str(resolved_path)


def validate_filename(filename: str) -> str:
    """
    Validate a filename for file uploads.
    
    Args:
        filename: The filename to validate
        
    Returns:
        Sanitized filename
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(filename, str):
        logger.warning(f"Filename validation failed: not a string (type: {type(filename).__name__})")
        raise ValidationError("Filename must be a string")
    
    # Check if empty
    if not filename or not filename.strip():
        logger.warning("Filename validation failed: empty string")
        raise ValidationError("Filename cannot be empty")
    
    filename = filename.strip()
    
    # Check length
    if len(filename) > MAX_FILENAME_LENGTH:
        logger.warning(f"Filename validation failed: length {len(filename)} exceeds maximum {MAX_FILENAME_LENGTH}")
        raise ValidationError(f"Filename cannot exceed {MAX_FILENAME_LENGTH} characters")
    
    # Check for null bytes and path separators
    if '\x00' in filename or '/' in filename or '\\' in filename:
        logger.warning("Filename validation failed: contains invalid characters")
        raise ValidationError("Filename contains invalid characters")
    
    # Check for hidden files (starting with .)
    if filename.startswith('.'):
        logger.warning(f"Filename validation failed: hidden file '{filename}'")
        raise ValidationError("Hidden files are not allowed")
    
    # Validate file extension
    if '.' not in filename:
        logger.warning(f"Filename validation failed: no extension in '{filename}'")
        raise ValidationError("File must have an extension")
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Filename validation failed: extension '{ext}' not in allowed list {ALLOWED_EXTENSIONS}")
        raise ValidationError(f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed")
    
    return filename


def validate_file_size(size: int) -> None:
    """
    Validate file size for uploads.
    
    Args:
        size: File size in bytes
        
    Raises:
        ValidationError: If file is too large
    """
    if not isinstance(size, int):
        logger.warning(f"File size validation failed: not an integer (type: {type(size).__name__})")
        raise ValidationError("File size must be an integer")
    
    if size < 0:
        logger.warning(f"File size validation failed: negative value {size}")
        raise ValidationError("File size cannot be negative")
    
    if size > MAX_FILE_SIZE:
        logger.warning(f"File size validation failed: size {size} exceeds maximum {MAX_FILE_SIZE}")
        raise ValidationError(f"File size cannot exceed {MAX_FILE_SIZE // (1024 * 1024)}MB")
    
    if size == 0:
        logger.warning("File size validation failed: empty file")
        raise ValidationError("File cannot be empty")


def validate_file_content(content: bytes) -> None:
    """
    Validate file content to ensure it's safe text.
    
    Args:
        content: File content as bytes
        
    Raises:
        ValidationError: If content is invalid
    """
    if not isinstance(content, bytes):
        logger.warning(f"File content validation failed: not bytes (type: {type(content).__name__})")
        raise ValidationError("File content must be bytes")
    
    # Check if content can be decoded as UTF-8
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        logger.warning("File content validation failed: not valid UTF-8")
        raise ValidationError("File must be valid UTF-8 text")
    
    # Check for null bytes (indicates binary content)
    if '\x00' in text:
        logger.warning("File content validation failed: contains null bytes (binary content)")
        raise ValidationError("File appears to be binary, not text")
    
    # Check for excessive control characters (may indicate binary or malicious content)
    control_char_count = sum(1 for char in text if ord(char) < 32 and char not in '\n\r\t')
    if len(text) > 0 and control_char_count / len(text) > 0.1:  # More than 10% control chars
        logger.warning("File content validation failed: too many control characters")
        raise ValidationError("File contains too many control characters")


def sanitize_html(text: str) -> str:
    """
    Sanitize text for safe display in HTML (XSS prevention).
    
    Args:
        text: The text to sanitize
        
    Returns:
        HTML-escaped text
    """
    if not isinstance(text, str):
        return str(text)
    
    # Use html.escape to escape HTML special characters
    return html.escape(text, quote=True)


def validate_all_book_data(title: str, author: str, summary: Optional[str] = None) -> Tuple[str, str, Optional[str]]:
    """
    Validate all book data at once.
    
    Args:
        title: Book title
        author: Author name
        summary: Optional book summary
        
    Returns:
        Tuple of (validated_title, validated_author, validated_summary)
        
    Raises:
        ValidationError: If any validation fails
    """
    validated_title = validate_title(title)
    validated_author = validate_author(author)
    validated_summary = validate_summary(summary)
    
    return validated_title, validated_author, validated_summary
