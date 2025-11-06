# Bookshelf-Flashcards
A helpful tool to refresh one's memory of the books that they have read on their bookshelf. Too often do people read a book and never think about it again. By keeping the stories in recent memory, their messages become more useful.

**Available in GUI, CLI, and Web versions!** Choose the interface that works best for you.

## 🌐 Web Version (NEW!)

**Host your bookshelf online and access it from anywhere!**

The web version is perfect for:
- Accessing your bookshelf from any device
- Sharing with friends or colleagues
- Cloud hosting on Render.com or similar platforms

### Deploy to Render.com

1. Fork this repository to your GitHub account
2. Sign up for a free account at [Render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` configuration
6. (Optional) Add your `GOOGLE_AI_API_KEY` environment variable for AI summaries
7. Click "Create Web Service"

Your bookshelf will be live at `https://your-service-name.onrender.com`

### Run Web Version Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the web server
python3 web_app.py

# 3. Open your browser to http://localhost:5000
```

Or use gunicorn for production-like environment:
```bash
gunicorn --bind 0.0.0.0:5000 web_app:app
```

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
python3 main.py
# OR
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

# 3. Try it out with example books
python3 main.py --mode cli add-file example_books.txt
python3 main.py --mode cli list
# OR using make:
# make run-example
# OR manually:
# python3 bookshelf.py add-file example_books.txt
# python3 bookshelf.py list
```

💡 **No Google AI Studio API key?** No problem! The app works without it - you just won't get AI-generated summaries.

📖 See [QUICKSTART.md](QUICKSTART.md) for more details and troubleshooting.

### Make Commands

For convenience, use `make` commands:
- `make help` - Show all available commands
- `make setup` - Run the setup script
- `make run` - Launch the application (GUI by default, using main.py)
- `make gui` - Launch the GUI application
- `make run-example` - Add example books and display them (CLI)
- `make list` - List all books (CLI)
- `make clean` - Remove database and cache files

## Features

- 🌐 **Web Interface**: Modern, responsive web UI accessible from any device
- 🖥️ **GUI & CLI Interfaces**: Choose between a full-featured GUI, web app, or lightweight CLI
- 📚 **Import from File**: Add multiple books at once from a text file
- 🤖 **AI-Powered Summaries**: Automatically generates book summaries using Google AI Studio
- 🗃️ **SQLite Database**: Stores books and summaries locally
- 💭 **Flashcard Mode**: Interactive interface to refresh your memory (available in all versions)
- ➕ **Easy Addition**: Add books interactively or from a file
- 🔍 **Author Disambiguation**: Prompts for author when titles match
- ☁️ **Cloud Ready**: Deploy to Render.com or any hosting platform

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
# Edit .env and add your Google AI Studio API key (optional)
```

**Note:** The application works without a Google AI Studio API key, but won't generate book summaries.

## Usage

### Unified Entry Point (main.py)

The easiest way to start the application is through `main.py`:

```bash
# Launch GUI (default)
python3 main.py

# Launch CLI
python3 main.py --mode cli list
python3 main.py --mode cli add-file books.txt
python3 main.py --mode cli flashcard
```

You can also use the individual entry points directly:

### GUI Application

Launch the GUI with:

```bash
python3 bookshelf_gui.py
# OR
make gui
# OR
python3 main.py --mode gui
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
# OR
python3 main.py --mode cli add-file books.txt
```

**File format options:**
- `Title by Author`
- `Title - Author`
- `Title` (will prompt for author)

#### Add a Single Book

```bash
python3 bookshelf.py add
# OR
python3 main.py --mode cli add
```

#### List All Books

```bash
python3 bookshelf.py list
# OR
python3 main.py --mode cli list
```

#### Flashcard Mode

Review your books in an interactive flashcard session:

```bash
python3 bookshelf.py flashcard
# OR
python3 main.py --mode cli flashcard
```

This mode will display each book's title and author, then reveal the summary when you press Enter. Perfect for refreshing your memory!

**CLI Database Path:**
```bash
python3 bookshelf.py --db /path/to/database.db list
```

## Which Version Should I Use?

- **Use the Web Version** if you want to access your bookshelf from anywhere, share it with others, or prefer a modern web interface
- **Use the GUI** if you prefer a desktop application with mouse-driven navigation, or if you want to see multiple books at once
- **Use the CLI** if you prefer command-line tools, want to script operations, or need a lightweight option

All versions share the same database format, so you can use them interchangeably!

## Example

**Using main.py (Recommended):**
```bash
# Launch the GUI (default)
python3 main.py

# Or use CLI mode
python3 main.py --mode cli add-file example_books.txt
python3 main.py --mode cli list
python3 main.py --mode cli flashcard
```

**GUI Example:**
```bash
# Launch the GUI
python3 bookshelf_gui.py
# OR
python3 main.py --mode gui

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

The application requires a Google AI Studio API key for generating summaries. Set it in a `.env` file:

```
GOOGLE_AI_API_KEY=your_api_key_here
```

**The application will run without an API key** - you can add and organize books, but summaries won't be generated automatically.

## Project Structure

- `main.py` - Unified entry point for both GUI and CLI
- `web_app.py` - Flask web application for hosting online
- `bookshelf_gui.py` - GUI application (tkinter)
- `bookshelf.py` - CLI application (lite version)
- `database.py` - Database operations (SQLite)
- `ai_service.py` - Google AI Studio integration for summaries
- `book_parser.py` - Parse book files
- `templates/` - HTML templates for web version
- `example_books.txt` - Example book list
- `requirements.txt` - Python dependencies
- `render.yaml` - Render.com deployment configuration

## Requirements

- Python 3.7+
- `python3-tk` package (for GUI) - usually pre-installed, or install with:
  - Ubuntu/Debian: `sudo apt-get install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - macOS: Usually included with Python installation
  - Windows: Usually included with Python installation
- OpenAI API key (optional, for summary generation)

**Note:** The CLI version works without `python3-tk`. Only the GUI requires it.
- Google AI Studio API key (for summary generation)

## License

See LICENSE file for details.
