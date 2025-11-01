# Bookshelf-Flashcards
A helpful tool to refresh one's memory of the books that they have read on their bookshelf. Too often do people read a book and never think about it again. By keeping the stories in recent memory, their messages become more useful.

**Available in both GUI and CLI versions!** Choose the interface that works best for you.

## 🚀 Quick Start

**Get started in under 2 minutes!**

### GUI Version (Recommended)

```bash
# 1. Clone and navigate to the repository
git clone https://github.com/zamays/Bookshelf-Flashcards.git
cd Bookshelf-Flashcards

# 2. Run the automated setup
./setup.sh

# 3. Launch the GUI
make gui
# OR manually:
# python3 bookshelf_gui.py
```

### CLI Version (Lite)

```bash
# 1. Clone and navigate to the repository
git clone https://github.com/zamays/Bookshelf-Flashcards.git
cd Bookshelf-Flashcards

# 2. Run the automated setup
./setup.sh

# 3. Try it out with example books (using make)
make run-example
# OR manually:
# python3 bookshelf.py add-file example_books.txt
# python3 bookshelf.py list
```

💡 **No OpenAI API key?** No problem! The app works without it - you just won't get AI-generated summaries.

📖 See [QUICKSTART.md](QUICKSTART.md) for more details and troubleshooting.

### Make Commands

For convenience, use `make` commands:
- `make help` - Show all available commands
- `make setup` - Run the setup script
- `make gui` - Launch the GUI application
- `make run-example` - Add example books and display them (CLI)
- `make list` - List all books (CLI)
- `make clean` - Remove database and cache files

## Features

- 🖥️ **GUI & CLI Interfaces**: Choose between a full-featured GUI or lightweight CLI
- 📚 **Import from File**: Add multiple books at once from a text file
- 🤖 **AI-Powered Summaries**: Automatically generates book summaries using OpenAI
- 🗃️ **SQLite Database**: Stores books and summaries locally
- 💭 **Flashcard Mode**: Interactive interface to refresh your memory
- ➕ **Easy Addition**: Add books interactively or from a file
- 🔍 **Author Disambiguation**: Prompts for author when titles match

## Installation

### Automated Setup (Recommended)

```bash
git clone https://github.com/zamays/Bookshelf-Flashcards.git
cd Bookshelf-Flashcards
./setup.sh
```

The setup script will install dependencies and configure the application for you.

### Manual Setup

If you prefer to set up manually:

1. Clone the repository:
```bash
git clone https://github.com/zamays/Bookshelf-Flashcards.git
cd Bookshelf-Flashcards
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Set up your configuration (optional):
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (optional)
```

**Note:** The application works without an OpenAI API key, but won't generate book summaries.

## Usage

### GUI Application

Launch the GUI with:

```bash
python3 bookshelf_gui.py
# OR
make gui
```

**GUI Features:**
- **Book List Tab**: View all your books in a list, add new books, and view detailed information
- **Flashcard Mode Tab**: Review books with an interactive flashcard interface
- **Menu Bar**: Quick access to all features
- **Add Single Book**: File → Add Book
- **Add from File**: File → Add Books from File (supports .txt files)
- **View Details**: Double-click any book or select and click "View Details"
- **Flashcard Navigation**: Previous/Next buttons and Reveal/Hide summary toggle

You can specify a custom database path:
```bash
python3 bookshelf_gui.py --db /path/to/database.db
```

### CLI Application (Lite Version)

The CLI provides a lightweight command-line interface with all core functionality.

#### Add Books from a File

Create a text file with book titles (see `example_books.txt` for format):

```bash
python3 bookshelf.py add-file books.txt
```

**File format options:**
- `Title by Author`
- `Title - Author`
- `Title` (will prompt for author)

#### Add a Single Book

```bash
python3 bookshelf.py add
```

#### List All Books

```bash
python3 bookshelf.py list
```

#### Flashcard Mode

Review your books in an interactive flashcard session:

```bash
python3 bookshelf.py flashcard
```

This mode will display each book's title and author, then reveal the summary when you press Enter. Perfect for refreshing your memory!

**CLI Database Path:**
```bash
python3 bookshelf.py --db /path/to/database.db list
```

## Which Version Should I Use?

- **Use the GUI** if you prefer a visual interface with mouse-driven navigation, or if you want to see multiple books at once
- **Use the CLI** if you prefer command-line tools, want to script operations, or need a lightweight option

Both versions share the same database, so you can use them interchangeably!

## Example

**GUI Example:**
```bash
# Launch the GUI
python3 bookshelf_gui.py

# Then use the GUI to:
# 1. Click "Add from File" and select example_books.txt
# 2. View your books in the Book List tab
# 3. Switch to Flashcard Mode tab to review
```

**CLI Example:**
```bash
# Add books from the example file
python3 bookshelf.py add-file example_books.txt

# View your bookshelf
python3 bookshelf.py list

# Start flashcard review
python3 bookshelf.py flashcard
```

## Configuration

### Database Location

By default, books are stored in `bookshelf.db` in the current directory. You can specify a different location in both GUI and CLI:

**GUI:**
```bash
python3 bookshelf_gui.py --db /path/to/your/database.db
```

**CLI:**
```bash
python3 bookshelf.py --db /path/to/your/database.db list
```

### API Key

The application requires an OpenAI API key for generating summaries. Set it in a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

**The application will run without an API key** - you can add and organize books, but summaries won't be generated automatically.

## Project Structure

- `bookshelf_gui.py` - GUI application (tkinter)
- `bookshelf.py` - CLI application (lite version)
- `database.py` - Database operations (SQLite)
- `ai_service.py` - OpenAI integration for summaries
- `book_parser.py` - Parse book files
- `example_books.txt` - Example book list
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.7+
- `python3-tk` package (for GUI) - usually pre-installed, or install with:
  - Ubuntu/Debian: `sudo apt-get install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - macOS: Usually included with Python installation
  - Windows: Usually included with Python installation
- OpenAI API key (optional, for summary generation)

**Note:** The CLI version works without `python3-tk`. Only the GUI requires it.

## License

See LICENSE file for details.
