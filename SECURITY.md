# Security Measures

This document describes the security measures implemented in the Bookshelf Flashcards application to prevent injection attacks, data corruption, and secure API key management.

## Table of Contents
1. [API Key and Secrets Management](#api-key-and-secrets-management)
2. [Input Validation](#input-validation)
3. [Security Headers](#security-headers)
4. [Rate Limiting](#rate-limiting)
5. [Security Logging](#security-logging)
6. [Database Constraints](#database-constraints)
7. [Testing](#testing)
8. [Security Best Practices](#security-best-practices)

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

## API Key and Secrets Management

### Overview
The application uses a centralized configuration system (`config.py`) for secure API key and secrets management with the following features:

- **Multiple Secret Providers**: Environment variables, file-based secrets (Docker/Kubernetes), and cloud secret managers (AWS/GCP)
- **API Key Validation**: Format checking and validation before use
- **Key Rotation Support**: Automatic support when using file or cloud-based providers
- **Production Warnings**: Automatic detection of insecure configurations in production
- **Never Logged**: API keys are never exposed in logs or error messages

### Secret Providers

#### 1. Environment Variables (Default)
The simplest method, suitable for development and simple deployments:

```bash
export GOOGLE_AI_API_KEY="your_api_key_here"
export SECRET_KEY="your_secret_key_here"
```

Or use a `.env` file:
```bash
# Copy example and edit
cp .env.example .env
# Edit .env with your values
```

**Security**: Environment variables are read at startup. Never commit `.env` files to version control.

#### 2. File-Based Secrets (Docker/Kubernetes)
For container orchestration platforms that mount secrets as files:

```bash
# Docker Swarm example
docker secret create google_ai_api_key ./google_api_key.txt

# Kubernetes example
kubectl create secret generic app-secrets \
  --from-literal=GOOGLE_AI_API_KEY="your_key_here"
```

**Configuration**:
```bash
# Set the secrets directory (default: /run/secrets)
SECRETS_DIR=/run/secrets
```

**Security**: Secrets are read from files at `/run/secrets/{SECRET_NAME}`. This is the standard location for Docker Swarm and Kubernetes secrets.

#### 3. AWS Secrets Manager
For AWS deployments using Secrets Manager:

**Prerequisites**:
```bash
pip install boto3
```

**Configuration**:
```bash
CLOUD_SECRET_PROVIDER=aws
AWS_REGION=us-east-1  # Set your region
```

**Create Secret**:
```bash
aws secretsmanager create-secret \
  --name GOOGLE_AI_API_KEY \
  --secret-string "your_api_key_here"
```

**Security**: Uses IAM roles for authentication. Never hardcode AWS credentials.

#### 4. Google Cloud Secret Manager
For GCP deployments using Secret Manager:

**Prerequisites**:
```bash
pip install google-cloud-secret-manager
```

**Configuration**:
```bash
CLOUD_SECRET_PROVIDER=gcp
GCP_PROJECT_ID=your-project-id
```

**Create Secret**:
```bash
echo -n "your_api_key_here" | \
  gcloud secrets create GOOGLE_AI_API_KEY --data-file=-
```

**Security**: Uses Application Default Credentials. Configure service account with minimal permissions.

### API Key Format Validation

API keys are validated before use:

- **Google AI API Key**: Must be at least 20 alphanumeric characters
- **Placeholder Detection**: Rejects common placeholder values like "your_api_key_here"
- **Production Enforcement**: Invalid keys cause errors in production but warnings in development

### Key Rotation

**Automatic Rotation Support**:
- File-based and cloud providers support key rotation automatically
- Application reads the latest value on each request (with caching for performance)
- No application restart required for key rotation

**Best Practices**:
1. Rotate keys regularly (recommended: every 90 days)
2. Use cloud provider features for automatic rotation
3. Monitor key usage and set expiration alerts
4. Have a rollback plan if rotation causes issues

**Example - AWS Secrets Manager Rotation**:
```bash
# Enable automatic rotation
aws secretsmanager rotate-secret \
  --secret-id GOOGLE_AI_API_KEY \
  --rotation-lambda-arn arn:aws:lambda:region:account:function:SecretsManagerRotation
```

### Production Security Warnings

The application automatically detects production environments and validates configuration:

**Detected Production Indicators**:
- `ENVIRONMENT=production`
- `FLASK_ENV=production`
- Running on Render.com, Heroku, AWS, or Google Cloud Run

**Automatic Checks**:
- ✅ Verifies SECRET_KEY is not a default value
- ✅ Checks SECRET_KEY length (minimum 32 characters recommended)
- ✅ Validates API key format
- ✅ Recommends HTTPS enforcement

**Example Output**:
```
WARNING: SECRET_KEY is too short. Use at least 32 characters.
INFO: Consider setting FORCE_HTTPS=true for production.
```

**Critical Failures**:
If using default SECRET_KEY in production, the application will refuse to start:
```
CRITICAL: Using default SECRET_KEY in production! Set SECRET_KEY environment variable.
```

### Security Headers

The application automatically adds security headers to all HTTP responses:

- **Content-Security-Policy**: Restricts resource loading to prevent XSS
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-XSS-Protection**: Enables browser XSS filters
- **Strict-Transport-Security (HSTS)**: Forces HTTPS (production only)

**Configuration**:
The CSP header can be customized in `web_app.py` if needed for your deployment.

### Never Logging API Keys

**Protection Mechanisms**:
1. API keys are never included in error messages
2. Error messages are sanitized to remove any accidental key exposure
3. Generic error messages in production (detailed errors only in development)
4. Configuration validation errors don't expose key values

**Example - Safe Error Handling**:
```python
try:
    summary = ai_service.generate_summary(title, author)
except Exception as e:
    # Error logged without exposing API key
    logger.error("AI summary generation failed")
    # User sees: "Failed to generate summary"
    # NOT: "API key 'AIza...' is invalid"
```

### Generating Secure Keys

**SECRET_KEY** (Flask session security):
```bash
# Python method (recommended)
python3 -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL method
openssl rand -hex 32

# Result example (use your own!):
# 8f7a3c2d9e1b4f6a8c3d5e7f9a2b4c6d8e1f3a5c7d9e2f4a6c8d1e3f5a7c9e2f
```

**API Keys**:
- Google AI Studio: Get from https://makersuite.google.com/app/apikey
- Never generate fake API keys or use placeholder values in production

## Security Best Practices

### For Developers
1. **Always validate inputs** before processing
2. **Never trust user input** - validate at multiple layers
3. **Use parameterized queries** for all database operations
4. **Enable logging** for security monitoring
5. **Keep dependencies updated** to patch security vulnerabilities
6. **Use HTTPS** in production to prevent man-in-the-middle attacks
7. **Set strong SECRET_KEY** in production environment
8. **Never commit secrets** to version control
9. **Use secret providers** for production deployments
10. **Rotate keys regularly** (recommended: every 90 days)

### For Deployment
1. Set `SECRET_KEY` environment variable to a strong random value (32+ characters)
2. Configure proper HTTPS certificates and set `FORCE_HTTPS=true`
3. Use production WSGI server (e.g., Gunicorn)
4. Set up log aggregation and monitoring
5. Implement rate limiting at load balancer/CDN level
6. Regular security audits and dependency updates
7. Consider implementing CSRF protection for sensitive operations
8. Use secret management service (AWS Secrets Manager, GCP Secret Manager, etc.)
9. Configure least-privilege IAM roles for secret access
10. Enable secret rotation where supported
11. Monitor for security warnings in application logs
12. Set `ENVIRONMENT=production` to enable production security checks

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
