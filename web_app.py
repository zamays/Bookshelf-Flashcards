#!/usr/bin/env python3
"""
Web application for Bookshelf Flashcards.
Flask-based web interface for hosting on Render.com.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from database import BookDatabase
from ai_service import SummaryGenerator
from book_parser import parse_book_file

app = Flask(__name__)
# Use SECRET_KEY from environment or a static fallback for development
# In production, always set SECRET_KEY environment variable
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

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


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page showing list of books."""
    books = db.get_all_books()
    return render_template('index.html', books=books, ai_available=ai_service is not None)


@app.route('/add', methods=['GET', 'POST'])
def add_book():
    """Add a single book."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        
        if not title or not author:
            flash('Both title and author are required.', 'error')
            return redirect(url_for('add_book'))
        
        # Add book to database
        book_id = db.add_book(title, author)
        
        if book_id == -1:
            flash('Book already exists in database.', 'warning')
            return redirect(url_for('index'))
        
        # Generate summary if AI service is available
        if ai_service:
            try:
                summary = ai_service.generate_summary(title, author)
                db.update_summary(book_id, summary)
                flash(f'Successfully added "{title}" by {author} with AI-generated summary.', 'success')
            except Exception as e:
                flash(f'Book added, but failed to generate summary: {str(e)}', 'warning')
        else:
            flash(f'Successfully added "{title}" by {author} (no AI summary available).', 'success')
        
        return redirect(url_for('index'))
    
    return render_template('add_book.html')


@app.route('/add-from-file', methods=['GET', 'POST'])
def add_from_file():
    """Add books from a file."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                books = parse_book_file(filepath)
                
                if not books:
                    flash('No books found in file.', 'warning')
                    return redirect(url_for('index'))
                
                added_count = 0
                for title, author in books:
                    if not author:
                        # Skip books without authors for now
                        continue
                    
                    book_id = db.add_book(title, author)
                    if book_id != -1:
                        added_count += 1
                        # Generate summary if AI service is available
                        if ai_service:
                            try:
                                summary = ai_service.generate_summary(title, author)
                                db.update_summary(book_id, summary)
                            except Exception:
                                pass  # Continue even if summary generation fails
                
                flash(f'Successfully added {added_count} book(s) from file.', 'success')
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
            finally:
                # Clean up uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            return redirect(url_for('index'))
        else:
            flash('Invalid file type. Only .txt files are allowed.', 'error')
            return redirect(request.url)
    
    return render_template('add_from_file.html')


@app.route('/book/<int:book_id>')
def view_book(book_id):
    """View details of a specific book."""
    book = db.get_book(book_id)
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
    """API endpoint to get a specific book."""
    book = db.get_book(book_id)
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
