# Bookshelf Flashcards - GUI Guide

## Overview

The Bookshelf Flashcards GUI provides a user-friendly graphical interface for managing your book collection and reviewing summaries in flashcard mode.

## Launching the GUI

```bash
python3 bookshelf_gui.py
# OR
make gui
```

With custom database:
```bash
python3 bookshelf_gui.py --db /path/to/database.db
```

## Main Window Layout

The GUI window consists of:

### Menu Bar
Located at the top of the window:

- **File Menu**
  - Add Book - Opens dialog to add a single book
  - Add Books from File - Import multiple books from a text file
  - Exit - Close the application

- **View Menu**
  - Book List - Switch to book list view
  - Flashcard Mode - Switch to flashcard view

- **Help Menu**
  - About - Display application information

### Tab Interface

The main interface has two tabs:

#### 1. Book List Tab

**Toolbar Buttons:**
- **Add Book** - Add a single book with title and author
- **Add from File** - Import books from a text file
- **Refresh** - Reload the book list from database
- **View Details** - Show full details of selected book

**Book List:**
- Displays all books in a scrollable list
- Format: "Title - Author"
- Books without summaries are marked with "(no summary)"
- Double-click any book to view its details

**Book Count:**
- Shows total number of books at the bottom

#### 2. Flashcard Mode Tab

**Flashcard Display:**
- Large title display
- Author display
- Scrollable summary text area

**Navigation Controls:**
- **◀ Previous** - Go to previous flashcard
- **Reveal Summary** - Toggle showing/hiding the summary
- **Next ▶** - Go to next flashcard
- **Start Flashcards** - Begin flashcard session

**Progress Indicator:**
- Shows current card position (e.g., "Card 3 of 10")

## Usage Guide

### Adding a Single Book

1. Click **File → Add Book** or use the toolbar button in Book List tab
2. Enter the book title
3. Enter the author name
4. Click **Add Book**
5. The application will:
   - Add the book to the database
   - Generate a summary if OpenAI API key is configured
   - Display a success message

### Adding Multiple Books from File

1. Click **File → Add Books from File** or use the toolbar button
2. Select a `.txt` file with book entries
3. The application will process each book and:
   - Show a progress bar
   - Prompt for author if not specified in file
   - Skip duplicate books
   - Display summary of added/skipped books

**File Format:**
```
Title by Author
Title - Author
Title (will prompt for author)
```

### Viewing Book Details

1. In the Book List tab, select a book
2. Click **View Details** button or double-click the book
3. A detail window will show:
   - Book title
   - Author name
   - Date added
   - Full summary (if available)
   - **Generate Summary** button (if no summary exists and API key is configured)

### Using Flashcard Mode

1. Click **View → Flashcard Mode** or select the Flashcard Mode tab
2. Click **Start Flashcards** button
3. For each card:
   - Read the title and author
   - Think about what you remember
   - Click **Reveal Summary** to see the summary
   - Click **Hide Summary** to test yourself again
   - Use **Next ▶** to move to the next card
   - Use **◀ Previous** to go back

4. Navigate through all your books at your own pace

## Status Bar

The bottom of the window shows:
- Current database file path
- Useful for confirming which database is being used

## Tips

- **Keyboard Focus**: Use Tab key to navigate between controls
- **Quick Access**: Double-click books in the list to view details
- **Both Versions**: The GUI and CLI use the same database, so you can switch between them
- **No API Key**: The GUI works without an OpenAI API key - you just won't get automatic summaries
- **Manual Summaries**: You can generate summaries later by viewing book details and clicking "Generate Summary"

## Troubleshooting

### GUI Won't Start

**Error: "No module named 'tkinter'"**

Solution: Install python3-tk package:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Display Issues

If you see "Can't connect to display" errors:
- Make sure you're running in a graphical environment
- On remote systems, ensure X11 forwarding is enabled
- Consider using the CLI version instead

### Books Not Showing

- Click the **Refresh** button
- Check that you're using the correct database file
- Verify books exist with CLI: `python3 bookshelf.py list`

## Comparison: GUI vs CLI

| Feature | GUI | CLI |
|---------|-----|-----|
| Add Single Book | ✓ Dialog form | ✓ Interactive prompts |
| Add from File | ✓ File browser | ✓ Command line |
| List Books | ✓ Scrollable list | ✓ Text output |
| Flashcard Mode | ✓ Visual cards with buttons | ✓ Text-based with Enter key |
| View Details | ✓ Detail window | ✓ Included in list |
| Generate Summary | ✓ On-demand button | ✓ Automatic on add |
| Progress Feedback | ✓ Progress bars | ✓ Text messages |
| Multi-tasking | ✓ Can browse while viewing | ✗ One task at a time |
| Ease of Use | Visual, mouse-driven | Fast, keyboard-driven |
| Requirements | python3-tk package | None (pure Python) |

Both interfaces provide the same core functionality - choose the one that fits your workflow!
