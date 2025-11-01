# GUI Screenshots and Visual Guide

Since the GUI is built with tkinter and runs in a graphical environment, here's what users will see when they run the application:

## Main Window

When launching `python3 bookshelf_gui.py`, users see:

### Window Title Bar
- **Title**: "Bookshelf Flashcards"
- **Size**: 900x700 pixels (resizable)
- **Standard window controls**: Minimize, Maximize, Close

### Menu Bar
Located at the top with three menus:

1. **File Menu**
   - Add Book
   - Add Books from File
   - (separator line)
   - Exit

2. **View Menu**
   - Book List
   - Flashcard Mode

3. **Help Menu**
   - About

### Tab Interface
Two tabs are visible below the menu bar:

#### Tab 1: "Book List" (default)
- **Toolbar** with 4 buttons in a row:
  - [Add Book]
  - [Add from File]
  - [Refresh]
  - [View Details]

- **Book List Area**:
  - Scrollable listbox showing all books
  - Each entry displays: "Title - Author"
  - Books without summaries show: "Title - Author (no summary)"
  - Vertical scrollbar on the right
  - Double-click any book to view details

- **Footer**:
  - Text showing: "Total books: X"

#### Tab 2: "Flashcard Mode"
- **Instructions** at top:
  - "Review your books in flashcard mode. Click 'Start' to begin."

- **Flashcard Display Box** (large bordered area):
  - Book title in large, bold font (16pt)
  - Author name in medium font (12pt) with "by" prefix
  - Scrollable text area for summary (12 lines tall)

- **Navigation Buttons** (centered at bottom):
  - [◀ Previous]
  - [Reveal Summary] (or [Hide Summary] when revealed)
  - [Next ▶]
  - [Start Flashcards]

- **Progress Label**:
  - Shows: "Card X of Y"

### Status Bar
At the very bottom of the window:
- Displays: "Database: bookshelf.db" (or custom path)
- Sunken border style
- Left-aligned text

## Dialog Windows

### Add Book Dialog (300x250px)
- **Title**: "Add New Book"
- **Fields**:
  - Label: "Book Title:" | Input box (40 chars wide)
  - Label: "Author:" | Input box (40 chars wide)
- **Status Label**: Shows progress messages in blue
- **Buttons**: [Add Book] [Cancel]

### Book Details Dialog (600x500px)
- **Title**: "Book Details"
- **Information Section**:
  - Title: [Bold] Book Title
  - Author: [Bold] Author Name
  - Added: [Bold] Timestamp
- **Summary Section** (bordered box):
  - Large scrollable text area
  - Shows full summary or "No summary available"
- **Buttons**: [Generate Summary] (if no summary) [Close]

### Add from File Dialog
Standard file browser dialog:
- Filter: "Text Files (*.txt)" and "All Files (*.*)"
- Title: "Select Book File"

### Progress Dialog (400x150px)
Appears when adding multiple books:
- **Status Label**: "Found X book(s) in file..."
- **Progress Bar**: Visual progress indicator
- **Detail Label**: "Processing: [current book title]"
- Closes automatically when complete

### Message Boxes
Standard tkinter message boxes:
- **Success**: "Added 'Title' by Author"
- **Warning**: "Please enter a book title" / "Please enter an author name"
- **Info**: "This book already exists in your bookshelf"
- **About**: Application info with version number

## Color Scheme
The GUI uses system default colors for a native look:
- **Background**: System default (typically light gray or white)
- **Text**: System default (typically black)
- **Buttons**: System default (platform-specific)
- **Highlights**: System selection color (typically blue)
- **Status Messages**: Blue for informational text

## User Interactions

### Adding a Book
1. Click "Add Book" → Dialog opens
2. Type title → Type author → Click "Add Book"
3. Status updates: "Adding book..." → "Generating summary..." → "Book added!"
4. Success message box appears
5. Book list refreshes automatically

### Viewing Book Details
1. Select a book from the list
2. Double-click OR click "View Details"
3. Details window opens with full information
4. If no summary, "Generate Summary" button is available

### Using Flashcard Mode
1. Switch to "Flashcard Mode" tab
2. Click "Start Flashcards"
3. See title and author
4. Click "Reveal Summary" to show the summary
5. Click "Next ▶" to move forward
6. Click "◀ Previous" to go back
7. Progress shows "Card X of Y"

### Importing from File
1. Click "Add from File"
2. File browser opens
3. Select a .txt file
4. Progress dialog shows with bar and status
5. Prompts for author if needed
6. Completion message shows: "Added X book(s). Skipped Y book(s)."

## Platform-Specific Appearance

### Windows
- Standard Windows look with window decorations
- Tahoma or Segoe UI font
- Windows-style buttons and scrollbars

### macOS
- macOS Aqua theme
- San Francisco or Helvetica font
- macOS-style buttons and scrollbars

### Linux
- Depends on desktop environment (GNOME, KDE, etc.)
- System font (typically DejaVu Sans or Ubuntu)
- GTK or Qt-style widgets

## Keyboard Navigation
- **Tab**: Move between controls
- **Enter**: Activate focused button
- **Arrow Keys**: Navigate in list and flashcards
- **Ctrl+Q**: Quit (on some platforms)
- **Alt+F**: Open File menu
- **Alt+V**: Open View menu
- **Alt+H**: Open Help menu

## Responsive Behavior
- Window can be resized
- List boxes expand to fill available space
- Scrollbars appear automatically when content exceeds visible area
- Minimum window size prevents controls from overlapping
- Text wraps in summary areas (700px wrap length)

## Comparison with CLI
The GUI provides the same functionality as the CLI but with:
- Visual feedback and progress bars
- Mouse-driven navigation
- Multiple books visible at once
- Easy access to all features through menus and buttons
- No need to remember command syntax
