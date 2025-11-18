#!/usr/bin/env python3
"""
Web application for Bookshelf Flashcards.
Flask-based web interface for hosting on Render.com.
"""
import os
import time
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError as WTFValidationError
from werkzeug.utils import secure_filename
from database import BookDatabase
from ai_service import SummaryGenerator
from book_parser import parse_book_file
from config import get_config
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
from auth import create_user, authenticate_user, validate_email, validate_password

# Set up logging for security monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configuration
config = get_config()

# Validate configuration and warn about security issues
try:
    config.validate()
except Exception as e:
    logger.error(f"Configuration validation failed: {e}")
    if config.is_production:
        raise

app = Flask(__name__)
# Use SECRET_KEY from config
app.secret_key = config.get_secret_key()

# Configure session security
app.config['SESSION_COOKIE_SECURE'] = config.is_production  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 604800  # 7 days

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    # Content Security Policy - restrict resource loading
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable browser XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Strict Transport Security (HSTS) - only in production with HTTPS
    if config.is_production and request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response


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
    ai_service = SummaryGenerator(config=config)
except ValueError as e:
    # AI service not available, that's okay
    logger.info("AI service not initialized: API key not configured")
except Exception as e:
    # Log error but don't expose details
    logger.error("Failed to initialize AI service")
    pass


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return db.get_user_by_id(int(user_id))


# Form classes
class LoginForm(FlaskForm):
    """Login form."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """Registration form."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

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
    user_id = current_user.id if current_user.is_authenticated else None
    books = db.get_all_books(user_id=user_id)
    return render_template('index.html', books=books, ai_available=ai_service is not None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate_user(db, form.email.data, form.password.data)
        if user:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            flash('Login successful!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user_id = create_user(db, form.email.data, form.password.data)
            if user_id:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('An account with this email already exists.', 'error')
        except ValidationError as e:
            flash(f'Registration failed: {str(e)}', 'error')
        except Exception as e:
            logger.error(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


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
@login_required
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
            book_id = db.add_book(validated_title, validated_author, user_id=current_user.id)
        except ValidationError as e:
            logger.error(f"Database validation error in add_book: {e}")
            flash(f'Error adding book: {str(e)}', 'error')
            return redirect(url_for('add_book'))
        
        if book_id == -1:
            flash('Book already exists in database.', 'warning')
            return redirect(url_for('index'))
        
        # Book added without summary - user can generate it later
        flash(f'Successfully added "{validated_title}" by {validated_author}. Generate summaries from the main page.', 'success')
        
        return redirect(url_for('index'))
    
    return render_template('add_book.html')


@app.route('/add-from-file', methods=['GET', 'POST'])
@login_required
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
                        book_id = db.add_book(validated_title, validated_author, user_id=current_user.id)
                        if book_id != -1:
                            added_count += 1
                            # Summaries can be generated later by the user
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
@login_required
def view_book(book_id):
    """View details of a specific book with validation."""
    # Validate book_id
    try:
        validated_id = validate_book_id(book_id)
        user_id = current_user.id if current_user.is_authenticated else None
        book = db.get_book(validated_id, user_id=user_id)
    except ValidationError as e:
        logger.warning(f"Invalid book_id in view_book: {book_id} - {e}")
        flash('Invalid book ID.', 'error')
        return redirect(url_for('index'))
    
    if not book:
        flash('Book not found or access denied.', 'error')
        return redirect(url_for('index'))
    
    return render_template('book_detail.html', book=book, ai_available=ai_service is not None)


@app.route('/generate-summaries', methods=['GET', 'POST'])
@login_required
def generate_summaries():
    """Generate summaries for selected books."""
    if request.method == 'POST':
        if not ai_service:
            flash('AI service not available. Please configure API key.', 'error')
            return redirect(url_for('generate_summaries'))
        
        # Get selected book IDs
        selected_ids = request.form.getlist('book_ids')
        if not selected_ids:
            flash('No books selected. Please select at least one book.', 'warning')
            return redirect(url_for('generate_summaries'))
        
        # Validate and convert IDs
        try:
            validated_ids = [validate_book_id(int(book_id)) for book_id in selected_ids]
        except (ValueError, ValidationError) as e:
            logger.warning(f"Invalid book IDs in generate_summaries: {selected_ids} - {e}")
            flash('Invalid book selection.', 'error')
            return redirect(url_for('generate_summaries'))
        
        # Rate limiting
        session_id = request.remote_addr or 'unknown'
        
        success_count = 0
        skipped_count = 0
        error_count = 0
        
        for book_id in validated_ids:
            book = db.get_book(book_id, user_id=current_user.id)
            if not book:
                error_count += 1
                continue
            
            # Skip if already has summary
            if book.get('summary'):
                skipped_count += 1
                continue
            
            # Check rate limit
            if not check_ai_rate_limit(session_id):
                flash(f'Rate limit reached. Generated {success_count} summaries. Please wait before generating more.', 'warning')
                break
            
            try:
                summary = ai_service.generate_summary(book['title'], book['author'])
                db.update_summary(book_id, summary, user_id=current_user.id)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to generate summary for book {book_id}: {e}")
                error_count += 1
        
        # Build feedback message
        messages = []
        if success_count > 0:
            messages.append(f'Successfully generated {success_count} summary/summaries')
        if skipped_count > 0:
            messages.append(f'skipped {skipped_count} (already had summaries)')
        if error_count > 0:
            messages.append(f'{error_count} failed')
        
        if success_count > 0:
            flash('. '.join(messages).capitalize() + '.', 'success')
        elif skipped_count > 0:
            flash('. '.join(messages).capitalize() + '.', 'info')
        else:
            flash('Failed to generate summaries. Please try again.', 'error')
        
        return redirect(url_for('index'))
    
    # GET request - show form
    books = db.get_all_books(user_id=current_user.id)
    # Filter to books without summaries
    books_without_summaries = [book for book in books if not book.get('summary')]
    
    return render_template('generate_summaries.html', 
                         books=books_without_summaries, 
                         ai_available=ai_service is not None)


@app.route('/book/<int:book_id>/edit-summary', methods=['GET', 'POST'])
@login_required
def edit_summary(book_id):
    """Edit summary for a specific book."""
    try:
        validated_id = validate_book_id(book_id)
        book = db.get_book(validated_id, user_id=current_user.id)
    except ValidationError as e:
        logger.warning(f"Invalid book_id in edit_summary: {book_id} - {e}")
        flash('Invalid book ID.', 'error')
        return redirect(url_for('index'))
    
    if not book:
        flash('Book not found or access denied.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'save':
            # Save edited summary
            new_summary = request.form.get('summary', '').strip()
            
            try:
                from validation import validate_summary
                validated_summary = validate_summary(new_summary) if new_summary else None
                db.update_summary(validated_id, validated_summary, user_id=current_user.id)
                flash(f'Summary updated for "{book["title"]}".', 'success')
            except ValidationError as e:
                logger.warning(f"Invalid summary in edit_summary: {e}")
                flash(f'Invalid summary: {str(e)}', 'error')
                return redirect(url_for('edit_summary', book_id=validated_id))
            
            return redirect(url_for('view_book', book_id=validated_id))
        
        elif action == 'regenerate':
            # Regenerate summary with AI
            if not ai_service:
                flash('AI service not available. Please configure API key.', 'error')
                return redirect(url_for('edit_summary', book_id=validated_id))
            
            # Rate limiting
            session_id = request.remote_addr or 'unknown'
            if not check_ai_rate_limit(session_id):
                flash('Rate limit reached. Please wait before regenerating.', 'warning')
                return redirect(url_for('edit_summary', book_id=validated_id))
            
            try:
                summary = ai_service.generate_summary(book['title'], book['author'])
                db.update_summary(validated_id, summary, user_id=current_user.id)
                flash(f'Summary regenerated for "{book["title"]}".', 'success')
            except Exception as e:
                logger.error(f"Failed to regenerate summary: {e}")
                flash(f'Failed to regenerate summary: {str(e)}', 'error')
            
            return redirect(url_for('view_book', book_id=validated_id))
    
    return render_template('edit_summary.html', book=book, ai_available=ai_service is not None)


@app.route('/flashcards')
@login_required
def flashcards():
    """Flashcard mode."""
    books = db.get_all_books(user_id=current_user.id)
    if not books:
        flash('No books available for flashcard mode. Add some books first!', 'info')
        return redirect(url_for('index'))
    
    return render_template('flashcards.html', books=books)


@app.route('/api/books')
@login_required
def api_books():
    """API endpoint to get all books."""
    books = db.get_all_books(user_id=current_user.id)
    return jsonify(books)


@app.route('/api/book/<int:book_id>')
@login_required
def api_book(book_id):
    """API endpoint to get a specific book with validation."""
    # Validate book_id
    try:
        validated_id = validate_book_id(book_id)
        book = db.get_book(validated_id, user_id=current_user.id)
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
