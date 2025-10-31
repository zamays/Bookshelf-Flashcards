# Quick Start Guide

Get up and running with Bookshelf-Flashcards in under 2 minutes!

## Prerequisites

- Python 3.7 or later
- pip (Python package installer)

## One-Command Setup

```bash
./setup.sh
```

This script will:
1. Check your Python installation
2. Install all required dependencies
3. Create a `.env` configuration file
4. Optionally save your OpenAI API key

## Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Create configuration file
cp .env.example .env

# 3. (Optional) Edit .env and add your OpenAI API key
nano .env  # or use your favorite editor
```

## Try It Out

Add the example books and start exploring:

```bash
# Add example books (no API key needed!)
python3 bookshelf.py add-file example_books.txt

# View your bookshelf
python3 bookshelf.py list

# Start flashcard mode
python3 bookshelf.py flashcard
```

## About the OpenAI API Key

**Good news:** The app works without an API key! 

- **With API key:** Books get automatic AI-generated summaries
- **Without API key:** You can still add and organize books (just no summaries)

To get an API key:
1. Visit https://platform.openai.com/api-keys
2. Create an account and generate a key
3. Add it to your `.env` file

## Common Commands

```bash
# View all available commands
python3 bookshelf.py --help

# Add a single book interactively
python3 bookshelf.py add

# Add multiple books from a file
python3 bookshelf.py add-file mybooks.txt

# List all your books
python3 bookshelf.py list

# Review books in flashcard mode
python3 bookshelf.py flashcard
```

## Next Steps

- Read the full [README.md](README.md) for detailed features
- Create your own book list file (see `example_books.txt` for format)
- Start adding books from your bookshelf!

## Troubleshooting

**"ModuleNotFoundError: No module named 'openai'"**
- Run: `pip3 install -r requirements.txt`

**"Warning: OpenAI API key not found"**
- This is just a warning - the app will still work!
- To remove it, add your API key to the `.env` file

**Python version issues**
- Make sure you have Python 3.7 or later: `python3 --version`
