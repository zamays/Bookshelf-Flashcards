# Bookshelf-Flashcards
A helpful tool to refresh one's memory of the books that they have read on their bookshelf. Too often do people read a book and never think about it again. By keeping the stories in recent memory, their messages become more useful.

## Features
- Add books to your library with title, author, and optional notes
- Mark books as read or unread
- View all books or filter to show only read books
- Persistent storage using JSON

## Installation
This application requires Python 3.7 or higher.

```bash
# Clone the repository
git clone https://github.com/zamays/Bookshelf-Flashcards.git
cd Bookshelf-Flashcards
```

## Usage

### Add a book to your library
```bash
# Add an unread book
python cli.py add "The Great Gatsby" "F. Scott Fitzgerald"

# Add a book that you've already read
python cli.py add "1984" "George Orwell" --read

# Add a book with notes
python cli.py add "To Kill a Mockingbird" "Harper Lee" --read --notes "A powerful story about justice"
```

### List books
```bash
# List all books (including unread)
python cli.py list

# List only books you've read
python cli.py list --read-only
```

### Mark books as read/unread
```bash
# Mark a book as read
python cli.py mark-read "The Great Gatsby"

# Mark a book as unread
python cli.py mark-unread "The Great Gatsby"
```

### Find a specific book
```bash
python cli.py find "1984"
```

### Get help
```bash
python cli.py help
```

## Running Tests
```bash
# Run all tests
python -m unittest discover -s . -p "test_*.py"

# Run specific test file
python -m unittest test_book.py
python -m unittest test_library.py
```

## Data Storage
Books are stored in a `library.json` file in the current directory. This file is created automatically when you add your first book.
