#!/usr/bin/env python3
"""
Web application for Bookshelf Flashcards.
Flask-based web interface for hosting on Render.com.
"""
import os
import time
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from database import BookDatabase
from ai_service import SummaryGenerator
from book_parser import parse_book_file
from validation import (
    validate_all_book_data,
    validate_book_id,
    validate_filename,
    validate_file_size,
    validate_file_content,
    validate_file_path,
    sanitize_html,
    ValidationError
)

# Set up logging for security monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Use SECRET_KEY from environment or a static fallback for development
# In production, always set SECRET_KEY environment variable
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Add custom Jinja2 filter for HTML sanitization (though Jinja2 auto-escapes by default)
@app.template_filter('sanitize')
def sanitize_filter(text):
    """Custom Jinja2 filter for explicit HTML sanitization."""
    return sanitize_html(text)

# Configuration
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'txt'}
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'bookshelf.db')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize services
db = BookDatabase(DATABASE_PATH)
ai_service = None

try:
    ai_service = SummaryGenerator()
except ValueError:
    # AI service not available, that's okay
    pass

# Rate limiting for AI summary generation (track last request time per session)
# In production, use Redis or similar for distributed rate limiting
ai_rate_limit = {}
AI_RATE_LIMIT_SECONDS = 5  # Minimum seconds between AI requests per session


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page showing list of books."""
    books = db.get_all_books()
    return render_template('index.html', books=books, ai_available=ai_service is not None)


def check_ai_rate_limit(session_id: str) -> bool:
    """
    Check if AI rate limit allows request.
    
    Args:
        session_id: Session identifier for rate limiting
        
    Returns:
        True if request is allowed, False if rate limited
    """
    current_time = time.time()
    last_request = ai_rate_limit.get(session_id, 0)
    
    if current_time - last_request < AI_RATE_LIMIT_SECONDS:
        return False
    
    ai_rate_limit[session_id] = current_time
    return True


@app.route('/add', methods=['GET', 'POST'])
def add_book():
    """Add a single book with input validation."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        
        # Validate inputs
        try:
            validated_title, validated_author, _ = validate_all_book_data(title, author, None)
        except ValidationError as e:
            logger.warning(f"Validation error in add_book: {e}")
            flash(f'Validation error: {str(e)}', 'error')
            return redirect(url_for('add_book'))
        
        # Add book to database (validation happens in db.add_book too)
        try:
            book_id = db.add_book(validated_title, validated_author)
        except ValidationError as e:
            logger.error(f"Database validation error in add_book: {e}")
            flash(f'Error adding book: {str(e)}', 'error')
            return redirect(url_for('add_book'))
        
        if book_id == -1:
            flash('Book already exists in database.', 'warning')
            return redirect(url_for('index'))
        
        # Generate summary if AI service is available and rate limit allows
        if ai_service:
            # Use client IP as session identifier for rate limiting
            session_id = request.remote_addr or 'unknown'
            
            if not check_ai_rate_limit(session_id):
                flash(f'Successfully added "{validated_title}" by {validated_author}. Rate limit reached for AI summaries - please wait.', 'warning')
                return redirect(url_for('index'))
            
            try:
                summary = ai_service.generate_summary(validated_title, validated_author)
                db.update_summary(book_id, summary)
                flash(f'Successfully added "{validated_title}" by {validated_author} with AI-generated summary.', 'success')
            except Exception as e:
                logger.error(f"AI summary generation failed: {e}")
                flash(f'Book added, but failed to generate summary: {str(e)}', 'warning')
        else:
            flash(f'Successfully added "{validated_title}" by {validated_author} (no AI summary available).', 'success')
        
        return redirect(url_for('index'))
    
    return render_template('add_book.html')


@app.route('/add-from-file', methods=['GET', 'POST'])
def add_from_file():
    """Add books from a file with comprehensive validation."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded.', 'error')
            return redirect(url_for('add_from_file'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('add_from_file'))
        
        # Validate filename
        try:
            validated_filename = validate_filename(file.filename)
        except ValidationError as e:
            logger.warning(f"Invalid filename uploaded: {file.filename} - {e}")
            flash(f'Invalid filename: {str(e)}', 'error')
            return redirect(url_for('add_from_file'))
        
        if file and allowed_file(file.filename):
            # Read and validate file content before saving
            try:
                file_content = file.read()
                
                # Validate file size
                validate_file_size(len(file_content))
                
                # Validate file content
                validate_file_content(file_content)
                
            except ValidationError as e:
                logger.warning(f"Invalid file content: {e}")
                flash(f'Invalid file: {str(e)}', 'error')
                return redirect(url_for('add_from_file'))
            
            # Save to secure location
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Validate file path (prevent path traversal)
            try:
                validated_filepath = validate_file_path(filepath, base_dir=app.config['UPLOAD_FOLDER'])
            except ValidationError as e:
                logger.error(f"Path traversal attempt: {filepath} - {e}")
                flash('Invalid file path.', 'error')
                return redirect(url_for('add_from_file'))
            
            # Write validated content to file
            with open(validated_filepath, 'wb') as f:
                f.write(file_content)
            
            try:
                books = parse_book_file(validated_filepath)
                
                if not books:
                    flash('No books found in file.', 'warning')
                    return redirect(url_for('index'))
                
                added_count = 0
                validation_errors = 0
                
                # Rate limiting for file uploads
                session_id = request.remote_addr or 'unknown'
                
                for title, author in books:
                    if not author:
                        # Skip books without authors for now
                        continue
                    
                    # Validate each book's data
                    try:
                        validated_title, validated_author, _ = validate_all_book_data(title, author, None)
                    except ValidationError as e:
                        logger.warning(f"Skipping invalid book from file: {title} - {e}")
                        validation_errors += 1
                        continue
                    
                    try:
                        book_id = db.add_book(validated_title, validated_author)
                        if book_id != -1:
                            added_count += 1
                            # Generate summary if AI service is available and rate limit allows
                            if ai_service and check_ai_rate_limit(session_id):
                                try:
                                    summary = ai_service.generate_summary(validated_title, validated_author)
                                    db.update_summary(book_id, summary)
                                except Exception as e:
                                    logger.warning(f"Summary generation failed for {validated_title}: {e}")
                                    pass  # Continue even if summary generation fails
                    except ValidationError as e:
                        logger.warning(f"Failed to add book from file: {validated_title} - {e}")
                        validation_errors += 1
                        continue
                
                if validation_errors > 0:
                    flash(f'Successfully added {added_count} book(s) from file. Skipped {validation_errors} invalid entries.', 'warning')
                else:
                    flash(f'Successfully added {added_count} book(s) from file.', 'success')
                
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                flash(f'Error processing file: {str(e)}', 'error')
            finally:
                # Clean up uploaded file
                if os.path.exists(validated_filepath):
                    os.remove(validated_filepath)
            
            return redirect(url_for('index'))
        else:
            flash('Invalid file type. Only .txt files are allowed.', 'error')
            return redirect(url_for('add_from_file'))
    
    return render_template('add_from_file.html')


@app.route('/book/<int:book_id>')
def view_book(book_id):
    """View details of a specific book with validation."""
    # Validate book_id
    try:
        validated_id = validate_book_id(book_id)
        book = db.get_book(validated_id)
    except ValidationError as e:
        logger.warning(f"Invalid book_id in view_book: {book_id} - {e}")
        flash('Invalid book ID.', 'error')
        return redirect(url_for('index'))
    
    if not book:
        flash('Book not found.', 'error')
        return redirect(url_for('index'))
    
    return render_template('book_detail.html', book=book, ai_available=ai_service is not None)


@app.route('/flashcards')
def flashcards():
    """Flashcard mode."""
    books = db.get_all_books()
    if not books:
        flash('No books available for flashcard mode. Add some books first!', 'info')
        return redirect(url_for('index'))
    
    return render_template('flashcards.html', books=books)


@app.route('/api/books')
def api_books():
    """API endpoint to get all books."""
    books = db.get_all_books()
    return jsonify(books)


@app.route('/api/book/<int:book_id>')
def api_book(book_id):
    """API endpoint to get a specific book with validation."""
    # Validate book_id
    try:
        validated_id = validate_book_id(book_id)
        book = db.get_book(validated_id)
    except ValidationError as e:
        logger.warning(f"Invalid book_id in api_book: {book_id} - {e}")
        return jsonify({'error': 'Invalid book ID'}), 400
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book)


@app.route('/health')
def health():
    """Health check endpoint for Render.com."""
    return jsonify({'status': 'healthy', 'ai_service': ai_service is not None})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
