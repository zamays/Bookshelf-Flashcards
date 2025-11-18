# Security Measures

This document describes the security measures implemented in the Bookshelf Flashcards application to prevent injection attacks and data corruption.

## Input Validation

### Overview
All user inputs are validated using the `validation.py` module before being processed or stored. Validation is enforced at multiple layers:

1. **Application Layer** - web_app.py, bookshelf_gui.py
2. **Database Layer** - database.py with schema constraints
3. **Template Layer** - Jinja2 auto-escaping for HTML output

### Validators

#### 1. Book Title Validation
- **Maximum length**: 500 characters
- **Required**: Cannot be empty
- **XSS Prevention**: Blocks patterns like `<script>`, `javascript:`, `onerror=`, `onclick=`, `<iframe>`, `eval(`
- **Control characters**: Rejects null bytes, newlines, carriage returns, tabs
- **Whitespace**: Automatically stripped from beginning and end

#### 2. Author Name Validation
- **Maximum length**: 200 characters
- **Required**: Cannot be empty
- **XSS Prevention**: Same protections as title
- **Control characters**: Same restrictions as title
- **Unicode support**: Full Unicode character support for international names

#### 3. Summary Validation
- **Maximum length**: 10,000 characters
- **Optional**: Can be null or empty
- **XSS Prevention**: Same protections as title
- **Control characters**: Null bytes rejected, newlines allowed
- **Whitespace**: Empty strings converted to None

#### 4. Database ID Validation
- **Type**: Integer only
- **Range**: 1 to 2,147,483,647 (32-bit signed integer max)
- **Conversion**: Automatic conversion from string to int
- **Prevention**: Blocks negative values, zero, and overflow attempts

#### 5. File Path Validation
- **Path traversal prevention**: Resolves to absolute path and checks against base directory
- **Control characters**: Rejects null bytes
- **Base directory constraint**: When specified, ensures path stays within allowed directory
- **Normalization**: Converts relative paths to absolute, resolves symlinks

#### 6. File Upload Validation
- **Filename validation**:
  - Maximum 255 characters
  - Must have extension
  - Only `.txt` extension allowed
  - No path separators (`/`, `\`)
  - No hidden files (starting with `.`)
- **File size validation**:
  - Maximum: 16 MB
  - Minimum: > 0 bytes (no empty files)
- **File content validation**:
  - Must be valid UTF-8
  - No null bytes (binary content)
  - Limited control characters (< 10% of content)

### XSS Prevention

All text outputs in HTML templates are automatically escaped by Jinja2. Additionally:

- Custom `sanitize_html()` function available for explicit sanitization
- Registered as Jinja2 filter: `{{ variable | sanitize }}`
- Escapes: `<`, `>`, `&`, `"`, `'`
- Prevents: Script injection, event handlers, iframe embedding

### SQL Injection Prevention

The application uses **parameterized queries** exclusively:
```python
cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
```

Combined with input validation, this provides defense-in-depth against SQL injection.

### Path Traversal Prevention

File uploads are protected against path traversal attacks:

1. Filenames validated to reject path separators
2. `werkzeug.secure_filename()` used to sanitize filenames
3. `validate_file_path()` ensures resolved path is within upload directory
4. Base directory constraint prevents `../` attacks

Example attack prevented:
```python
# Attempt: "../../../../etc/passwd"
# Result: ValidationError - path is outside allowed directory
```

## Rate Limiting

### AI Summary Generation
- **Rate limit**: 5 seconds minimum between requests per IP address
- **Scope**: Both manual additions and file uploads
- **Implementation**: In-memory tracking (use Redis in production for distributed systems)
- **Bypass prevention**: Rate limit applied before AI service call

## Security Logging

All validation failures are logged with details for security monitoring:

```python
logger.warning(f"Title validation failed: length {len(title)} exceeds maximum {MAX_TITLE_LENGTH}")
```

### Logged Events
- Input validation failures (with reason)
- XSS attack attempts (dangerous patterns detected)
- Path traversal attempts
- File upload validation failures
- Invalid database ID access attempts
- AI service errors

### Log Levels
- **WARNING**: Validation failures, user errors
- **ERROR**: System errors, unexpected failures
- **INFO**: Normal operations (web app startup, etc.)

## Database Constraints

The database schema includes CHECK constraints for defense-in-depth:

```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(title) <= 500),
    author TEXT NOT NULL CHECK(length(author) <= 200),
    summary TEXT CHECK(summary IS NULL OR length(summary) <= 10000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(title, author)
)
```

These constraints provide a last line of defense if validation is somehow bypassed.

## Testing

The security implementation includes comprehensive test coverage:

- **89 validation tests** in `tests/test_validation.py`
- **29 database tests** including validation integration
- **218 total tests** across the application
- **Edge case testing**: Empty inputs, oversized inputs, special characters, Unicode, XSS attempts, SQL injection attempts, path traversal attempts

### Example Test Cases
```python
def test_title_with_script_tag_raises_error():
    """Test XSS prevention - script tag."""
    with pytest.raises(ValidationError, match="dangerous"):
        validate_title("Title<script>alert('xss')</script>")

def test_file_path_traversal_with_base_dir():
    """Test path traversal prevention with base directory."""
    with pytest.raises(ValidationError, match="outside"):
        validate_file_path("../etc/passwd", base_dir=tmpdir)
```

## Security Best Practices

### For Developers
1. **Always validate inputs** before processing
2. **Never trust user input** - validate at multiple layers
3. **Use parameterized queries** for all database operations
4. **Enable logging** for security monitoring
5. **Keep dependencies updated** to patch security vulnerabilities
6. **Use HTTPS** in production to prevent man-in-the-middle attacks
7. **Set strong SECRET_KEY** in production environment

### For Deployment
1. Set `SECRET_KEY` environment variable to a strong random value
2. Configure proper HTTPS certificates
3. Use production WSGI server (e.g., Gunicorn)
4. Set up log aggregation and monitoring
5. Implement rate limiting at load balancer/CDN level
6. Regular security audits and dependency updates
7. Consider implementing CSRF protection for sensitive operations

## Known Limitations

1. **Rate limiting**: In-memory implementation - use Redis/Memcached for distributed deployments
2. **Session tracking**: Uses IP address - may have issues with proxies/NAT
3. **File upload cleanup**: Relies on finally block - ensure proper error handling in production
4. **No CAPTCHA**: Consider adding for public-facing deployments
5. **No email verification**: For user accounts if implemented in future

## Compliance

This implementation addresses common web security concerns:

- **OWASP Top 10**: XSS, Injection, Path Traversal
- **CWE**: CWE-79 (XSS), CWE-89 (SQL Injection), CWE-22 (Path Traversal)
- **Data Validation**: Input sanitization and output encoding

## Security Updates

- **Version 1.0** (2024): Initial security implementation
  - Input validation module
  - XSS prevention
  - Path traversal prevention
  - Rate limiting
  - Security logging

## Contact

For security issues or vulnerability reports, please contact the repository maintainers.
