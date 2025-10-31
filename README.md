# Bookshelf-Flashcards
A helpful tool to refresh one's memory of the books that they have read on their bookshelf. Too often do people read a book and never think about it again. By keeping the stories in recent memory, their messages become more useful.

## Features

- 📚 **Import from File**: Add multiple books at once from a text file
- 🤖 **AI-Powered Summaries**: Automatically generates book summaries using OpenAI
- 🗃️ **SQLite Database**: Stores books and summaries locally
- 💭 **Flashcard Mode**: Interactive interface to refresh your memory
- ➕ **Easy Addition**: Add books interactively or from a file
- 🔍 **Author Disambiguation**: Prompts for author when titles match

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zamays/Bookshelf-Flashcards.git
cd Bookshelf-Flashcards
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

### Add Books from a File

Create a text file with book titles (see `example_books.txt` for format):

```bash
python bookshelf.py add-file books.txt
```

**File format options:**
- `Title by Author`
- `Title - Author`
- `Title` (will prompt for author)

### Add a Single Book

```bash
python bookshelf.py add
```

### List All Books

```bash
python bookshelf.py list
```

### Flashcard Mode

Review your books in an interactive flashcard session:

```bash
python bookshelf.py flashcard
```

This mode will display each book's title and author, then reveal the summary when you press Enter. Perfect for refreshing your memory!

## Example

```bash
# Add books from the example file
python bookshelf.py add-file example_books.txt

# View your bookshelf
python bookshelf.py list

# Start flashcard review
python bookshelf.py flashcard
```

## Configuration

### Database Location

By default, books are stored in `bookshelf.db` in the current directory. You can specify a different location:

```bash
python bookshelf.py --db /path/to/your/database.db list
```

### API Key

The application requires an OpenAI API key for generating summaries. Set it in a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

## Project Structure

- `bookshelf.py` - Main CLI application
- `database.py` - Database operations (SQLite)
- `ai_service.py` - OpenAI integration for summaries
- `book_parser.py` - Parse book files
- `example_books.txt` - Example book list
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.7+
- OpenAI API key (for summary generation)

## License

See LICENSE file for details.
