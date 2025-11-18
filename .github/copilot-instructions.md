# GitHub Copilot Instructions for Bookshelf-Flashcards

## Project Overview

Bookshelf-Flashcards is a Python application that helps users refresh their memory of books they've read through a flashcard system. The application is available in three interfaces:

- **Web Application**: Flask-based web interface (production-ready, deployable to Render.com)
- **GUI Application**: Tkinter-based desktop interface
- **CLI Application**: Command-line interface for lightweight usage

### Key Features
- Import books from text files or add them individually
- AI-powered book summaries using Google AI Studio API
- SQLite database for persistent storage
- Flashcard mode for reviewing books
- Comprehensive input validation and security measures

## Project Structure

### Core Modules
- `main.py` - Unified entry point for GUI and CLI modes
- `web_app.py` - Flask web application
- `bookshelf_gui.py` - Tkinter GUI application
- `bookshelf.py` - CLI application
- `database.py` - SQLite database operations with validation
- `ai_service.py` - Google AI Studio integration for generating summaries
- `book_parser.py` - Parse book files in multiple formats
- `validation.py` - Comprehensive input validation and security
- `config.py` - Centralized configuration and secrets management

### Supporting Files
- `templates/` - Jinja2 templates for web interface
- `tests/` - Comprehensive test suite (295 tests, >90% coverage)
- `example_books.txt` - Example book list for testing

## Development Standards

### Python Version
- **Target**: Python 3.9+ (supports 3.9, 3.10, 3.11, 3.12)
- **Compatibility**: Use features compatible with Python 3.9

### Code Style
- **Line length**: Maximum 100 characters
- **Docstrings**: Required for all public functions and classes
- **Type hints**: Encouraged but not strictly enforced (mypy checks are informational)
- **Naming conventions**: Follow PEP 8 (snake_case for functions/variables, PascalCase for classes)

### Linting and Type Checking
- **Pylint**: Must pass with score ≥8.0 (configuration in `.pylintrc`)
- **Mypy**: Run for type checking but failures don't block CI (configuration in `mypy.ini`)
- **Bandit**: Security scanning runs but doesn't block CI

### Testing Requirements
- **Framework**: pytest with pytest-cov and pytest-mock
- **Coverage**: Minimum 75% required, aim for >90% on core modules
- **Configuration**: See `pytest.ini` for settings
- **Test files**: Located in `tests/` directory, named `test_*.py`
- **Run tests**: `pytest -v` or `pytest --cov=. --cov-report=term-missing`

### Current Test Coverage
- `database.py`: 100% ✅
- `book_parser.py`: 100% ✅
- `ai_service.py`: 77%
- Overall core modules: >90%

## Building and Running

### Setup
```bash
./setup.sh          # Automated setup (installs dependencies, creates .env)
# OR
pip3 install -r requirements.txt
```

### Running the Application
```bash
python3 main.py                              # Launch GUI (default)
python3 main.py --mode gui                   # Launch GUI explicitly
python3 main.py --mode cli list              # CLI mode
python3 web_app.py                           # Web version (dev server)
gunicorn --bind 0.0.0.0:5000 web_app:app    # Web version (production)
```

### Make Commands
```bash
make help         # Show all commands
make setup        # Run setup script
make run          # Launch GUI
make gui          # Launch GUI
make run-example  # Add example books (CLI)
make list         # List books (CLI)
make clean        # Remove database and cache files
```

### Testing
```bash
pytest -v                                    # Run all tests
pytest tests/test_database.py               # Run specific test file
pytest --cov=. --cov-report=term-missing    # Run with coverage report
```

## Security Guidelines

### Input Validation
**CRITICAL**: All user inputs MUST be validated using the `validation.py` module before processing or storage.

#### Required Validators
- `validate_title()` - Book titles (max 500 chars, XSS prevention)
- `validate_author()` - Author names (max 200 chars, XSS prevention)
- `validate_summary()` - Summaries (max 10,000 chars, optional)
- `validate_book_id()` - Database IDs (positive integers only)
- `validate_file_path()` - File paths (path traversal prevention)
- `validate_file_upload()` - File uploads (size, extension, content validation)

#### Example Usage
```python
from validation import validate_title, validate_author, ValidationError

try:
    title = validate_title(user_input_title)
    author = validate_author(user_input_author)
    db.add_book(title, author)
except ValidationError as e:
    # Handle validation error
    print(f"Validation failed: {e}")
```

### XSS Prevention
- All database inputs are validated to block dangerous patterns
- HTML templates use Jinja2 auto-escaping
- Custom `sanitize_html()` filter available: `{{ variable | sanitize }}`
- Never use `safe` filter on user input

### SQL Injection Prevention
- ALWAYS use parameterized queries: `cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))`
- NEVER concatenate user input into SQL strings
- Database layer includes CHECK constraints as defense-in-depth

### Path Traversal Prevention
- Validate all file paths with `validate_file_path()`
- Use `werkzeug.secure_filename()` for file uploads
- Restrict file uploads to `.txt` extension only
- Maximum file size: 16 MB

### API Keys and Secrets
- Use `config.py` for all configuration and secret management
- Support environment variables, file-based secrets, AWS Secrets Manager, GCP Secret Manager
- API keys are NEVER logged or exposed in error messages
- Validate API keys before use with `is_valid_api_key()`
- In production, SECRET_KEY must be strong (32+ characters)

## Database Guidelines

### Schema
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

### Usage Patterns
- Use `BookDatabase` class for all database operations
- Connection uses `check_same_thread=False` for Flask compatibility
- Use `sqlite3.Row` for row factory (access by column name)
- Handle `sqlite3.IntegrityError` for duplicate books
- Always validate inputs before database operations

## AI Service Integration

### Google AI Studio
- Uses Google Generative AI API (Gemini model)
- API key from environment variable: `GOOGLE_AI_API_KEY`
- Rate limiting: 5 seconds minimum between requests
- Graceful degradation: Application works without API key (no summaries)
- Error handling: Catch and log API errors, provide user-friendly messages

### Summary Generation
```python
from ai_service import SummaryGenerator

try:
    generator = SummaryGenerator(api_key)
    summary = generator.generate_summary(title, author)
except ValueError as e:
    # Handle missing/invalid API key
    summary = None
```

## Common Patterns

### Error Handling
- Use `ValidationError` for validation failures
- Catch `sqlite3.IntegrityError` for duplicate books
- Catch `FileNotFoundError` for missing files
- Provide user-friendly error messages (don't expose internals)
- Log security-related errors for monitoring

### Book File Parsing
Supported formats:
```
Title by Author
Title - Author
Title
```

Comments (lines starting with `#`) and empty lines are ignored.

### Flashcard Mode
- Display books sequentially
- Show title and author initially
- Reveal summary on user action
- Support navigation (next/previous)
- Handle empty bookshelf gracefully

## Adding New Features

### Before Adding Code
1. Check existing tests to understand expected behavior
2. Review validation requirements if handling user input
3. Consider all three interfaces (web, GUI, CLI)
4. Check SECURITY.md for relevant security concerns

### After Adding Code
1. Write tests for new functionality (aim for >90% coverage)
2. Run `pytest -v` to ensure all tests pass
3. Run linting: `pylint --rcfile=.pylintrc your_file.py`
4. Update documentation if adding user-facing features
5. Check security implications if handling user data

### Adding Dependencies
1. Add to `requirements.txt` with version constraints
2. Run security scan if adding external libraries
3. Test on Python 3.9-3.12 for compatibility
4. Document any system-level dependencies (like `python3-tk`)

## Deployment Considerations

### Web Application (Production)
- Use Gunicorn WSGI server, not Flask dev server
- Set `SECRET_KEY` environment variable (32+ characters)
- Configure `GOOGLE_AI_API_KEY` if using AI features
- Enable HTTPS and set `FORCE_HTTPS=true`
- Use production secret provider (AWS/GCP Secrets Manager)
- Configuration auto-detects production environment

### Render.com Deployment
- Configuration in `render.yaml`
- Set environment variables in Render dashboard
- Uses Gunicorn automatically
- See DEPLOYMENT.md for detailed instructions

### Environment Variables
```bash
GOOGLE_AI_API_KEY=<your_api_key>        # Optional, for AI summaries
SECRET_KEY=<strong_random_key>          # Required for web app in production
ENVIRONMENT=production                   # Enables production security checks
FORCE_HTTPS=true                        # Enforces HTTPS redirects
```

## Troubleshooting Common Issues

### GUI Issues
- Missing `python3-tk`: Install system package
  - Ubuntu/Debian: `sudo apt-get install python3-tk`
  - macOS/Windows: Usually included with Python

### Database Issues
- Lock errors: Close other connections to `bookshelf.db`
- Duplicate book: Check `UNIQUE(title, author)` constraint
- Validation errors: Check `validation.py` for length limits

### API Issues
- Missing API key: Application runs but won't generate summaries
- Invalid API key: Check format and test with Google AI Studio
- Rate limiting: Wait 5 seconds between summary requests

## Documentation

### Key Documentation Files
- `README.md` - Main documentation with usage examples
- `QUICKSTART.md` - Quick start guide for new users
- `DEPLOYMENT.md` - Deployment instructions for Render.com
- `SECURITY.md` - Comprehensive security documentation
- `TUTORIAL.md` - User tutorial for getting started
- `GUI_GUIDE.md` - GUI application user guide

### Updating Documentation
- Keep README.md synchronized with code changes
- Update version numbers and feature lists
- Add examples for new features
- Update deployment instructions if configuration changes

## CI/CD

### GitHub Actions Workflows
- `.github/workflows/test.yml` - Runs tests on multiple OS and Python versions
- `.github/workflows/lint.yml` - Code quality checks (pylint, mypy, bandit)

### Pull Request Requirements
- All tests must pass
- Pylint score must be ≥8.0
- Code coverage must be ≥75%
- No critical security issues from Bandit

## Important Notes

### Multi-Interface Support
When modifying core functionality, ensure changes work across all interfaces:
- Web app (Flask/HTML)
- GUI (Tkinter)
- CLI (argparse)

### Thread Safety
- Database uses `check_same_thread=False` for Flask
- Rate limiting uses thread-safe structures
- AI service calls are sequential (not parallelized)

### Backward Compatibility
- Maintain database schema compatibility
- Don't break existing book file formats
- Keep CLI command interface stable

## Getting Help

### Resources
- Repository README: Comprehensive usage documentation
- Test files: Examples of expected behavior
- SECURITY.md: Security implementation details
- Issue tracker: Known issues and feature requests

### When Making Changes
- Read related test files first
- Check existing code for similar patterns
- Follow security guidelines strictly
- Write tests before implementing features
- Run full test suite before committing

---

**Remember**: Security, input validation, and testing are not optional in this project. Every user input must be validated, every feature must be tested, and security best practices must be followed.
