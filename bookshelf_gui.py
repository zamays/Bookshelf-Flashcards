"""
GUI application for Bookshelf Flashcards.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog

from database import BookDatabase
from ai_service import SummaryGenerator
from book_parser import parse_book_file


def get_default_font():
    """Get platform-appropriate default font."""
    if sys.platform == 'darwin':
        return 'Helvetica Neue'
    if sys.platform == 'win32':
        return 'Segoe UI'
    return 'Liberation Sans'


class BookshelfGUI:
    """GUI application for managing bookshelf flashcards."""

    def __init__(self, root: tk.Tk, db_path: str = "bookshelf.db"):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Bookshelf Flashcards")
        self.root.geometry("900x700")

        self.db_path = db_path
        self.db = BookDatabase(db_path)
        self.ai_service = None
        self._init_ai_service()

        # Track flashcard mode state
        self.flashcard_books = []
        self.current_flashcard_index = 0
        self.flashcard_revealed = False

        self._create_menu()
        self._create_main_interface()
        self._refresh_book_list()

    def _init_ai_service(self):
        """Initialize AI service if API key is available."""
        try:
            self.ai_service = SummaryGenerator()
        except ValueError:
            # AI service not available, that's okay
            pass

    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Book", command=self._show_add_book_dialog)
        file_menu.add_command(
            label="Add Books from File", command=self._add_books_from_file
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Book List", command=self._show_book_list)
        view_menu.add_command(
            label="Flashcard Mode", command=self._start_flashcard_mode
        )

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Start Tutorial", command=self._start_tutorial)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_interface(self):
        """Create the main interface."""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Book List Tab
        self.list_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.list_frame, text="Book List")
        self._create_book_list_tab()

        # Flashcard Tab
        self.flashcard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.flashcard_frame, text="Flashcard Mode")
        self._create_flashcard_tab()

        # Status bar
        self.status_bar = ttk.Label(
            self.root, text=f"Database: {self.db_path}", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_book_list_tab(self):
        """Create the book list tab."""
        # Toolbar with cleaner spacing
        toolbar = ttk.Frame(self.list_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Add Book", command=self._show_add_book_dialog).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            toolbar, text="Add from File", command=self._add_books_from_file
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=self._refresh_book_list).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="View Details", command=self._view_book_details).pack(
            side=tk.LEFT, padx=2
        )

        # Add tutorial buttons with separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar, text="Start Tutorial", command=self._start_tutorial).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="Clear Example Books", command=self._clear_example_books).pack(
            side=tk.LEFT, padx=2
        )

        # Book list with scrollbar
        list_container = ttk.Frame(self.list_frame)
        list_container.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.book_listbox = tk.Listbox(
            list_container, yscrollcommand=scrollbar.set, font=("Arial", 10)
        )
        self.book_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        self.book_listbox.bind("<Double-Button-1>", lambda e: self._view_book_details())

        scrollbar.config(command=self.book_listbox.yview)

        # Book count label
        self.book_count_label = ttk.Label(self.list_frame, text="Total books: 0")
        self.book_count_label.pack(side=tk.BOTTOM, pady=5)

    def _create_flashcard_tab(self):
        """Create the flashcard tab."""
        # Instructions with better styling
        instructions = ttk.Label(
            self.flashcard_frame,
            text="Review your books in flashcard mode. Click 'Start' to begin.",
            font=("Arial", 10),
        )
        instructions.pack(pady=20)

        # Card display frame
        self.card_frame = ttk.LabelFrame(
            self.flashcard_frame, text="Flashcard", padding=20
        )
        self.card_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Card content
        self.card_title_label = ttk.Label(
            self.card_frame, text="", font=("Arial", 16, "bold"), wraplength=700
        )
        self.card_title_label.pack(pady=10)

        self.card_author_label = ttk.Label(
            self.card_frame, text="", font=("Arial", 12), wraplength=700
        )
        self.card_author_label.pack(pady=5)

        self.card_summary_text = scrolledtext.ScrolledText(
            self.card_frame,
            wrap=tk.WORD,
            height=12,
            font=("Arial", 10),
            state="disabled",
        )
        self.card_summary_text.pack(fill="both", expand=True, pady=10)

        # Navigation buttons
        nav_frame = ttk.Frame(self.flashcard_frame)
        nav_frame.pack(side=tk.BOTTOM, pady=10)

        self.prev_button = ttk.Button(
            nav_frame, text="◀ Previous", command=self._prev_flashcard, state="disabled"
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.reveal_button = ttk.Button(
            nav_frame,
            text="Reveal Summary",
            command=self._reveal_summary,
            state="disabled",
        )
        self.reveal_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(
            nav_frame, text="Next ▶", command=self._next_flashcard, state="disabled"
        )
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.start_button = ttk.Button(
            nav_frame, text="Start Flashcards", command=self._start_flashcard_mode
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Progress label
        self.progress_label = ttk.Label(self.flashcard_frame, text="")
        self.progress_label.pack(side=tk.BOTTOM, pady=5)

    def _show_add_book_dialog(self):
        """Show dialog to add a new book."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Book")
        dialog.geometry("450x220")
        dialog.transient(self.root)
        dialog.grab_set()

        # Title
        ttk.Label(dialog, text="Book Title:").grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        title_entry = ttk.Entry(dialog, width=40)
        title_entry.grid(row=0, column=1, padx=10, pady=10)
        title_entry.focus()

        # Author
        ttk.Label(dialog, text="Author:").grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        author_entry = ttk.Entry(dialog, width=40)
        author_entry.grid(row=1, column=1, padx=10, pady=10)

        # Status label
        status_label = ttk.Label(
            dialog, text="", foreground="#0078D4", font=(get_default_font(), 9)
        )
        status_label.grid(row=2, column=0, columnspan=2, pady=5)

        def add_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()

            if not title:
                messagebox.showwarning(
                    "Missing Information", "Please enter a book title."
                )
                return
            if not author:
                messagebox.showwarning(
                    "Missing Information", "Please enter an author name."
                )
                return

            # Check if book already exists before adding
            existing = self.db.search_books_by_title(title)
            is_duplicate = any(book["author"] == author for book in existing)

            if is_duplicate:
                messagebox.showinfo(
                    "Duplicate Book", "This book already exists in your bookshelf."
                )
                dialog.destroy()
                self._refresh_book_list()
                return

            status_label.config(text="Adding book...")
            dialog.update()

            book_id = self.db.add_book(title, author)

            # Generate summary if AI service is available
            if self.ai_service:
                status_label.config(text="Generating summary...")
                dialog.update()
                try:
                    summary = self.ai_service.generate_summary(title, author)
                    self.db.update_summary(book_id, summary)
                    status_label.config(text="Book added with summary!")
                except Exception as e:
                    status_label.config(
                        text=f"Book added (summary generation failed: {str(e)})"
                    )
            else:
                status_label.config(text="Book added (no AI summary available)")

            self._refresh_book_list()
            messagebox.showinfo("Success", f"Added '{title}' by {author}")
            dialog.destroy()

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Add Book", command=add_book).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def _add_books_from_file(self):
        """Add books from a file."""
        file_path = filedialog.askopenfilename(
            title="Select Book File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )

        if not file_path:
            return

        try:
            books = parse_book_file(file_path)

            if not books:
                messagebox.showinfo(
                    "No Books Found", "No books found in the selected file."
                )
                return

            # Create progress dialog
            progress_dialog = tk.Toplevel(self.root)
            progress_dialog.title("Adding Books")
            progress_dialog.geometry("400x150")
            progress_dialog.transient(self.root)
            progress_dialog.grab_set()

            status_label = ttk.Label(
                progress_dialog, text=f"Found {len(books)} book(s) in file..."
            )
            status_label.pack(pady=10)

            progress_bar = ttk.Progressbar(
                progress_dialog, length=300, mode="determinate"
            )
            progress_bar.pack(pady=10)
            progress_bar["maximum"] = len(books)

            detail_label = ttk.Label(progress_dialog, text="")
            detail_label.pack(pady=5)

            added_count = 0
            skipped_count = 0

            for idx, (title, author) in enumerate(books):
                progress_bar["value"] = idx
                detail_label.config(text=f"Processing: {title}")
                progress_dialog.update()

                if not author:
                    # Prompt for author
                    author = simpledialog.askstring(
                        "Author Required",
                        f"Enter author for '{title}':",
                        parent=progress_dialog,
                    )
                    if not author:
                        skipped_count += 1
                        continue

                # Check for duplicates before adding
                existing = self.db.search_books_by_title(title)
                if any(book["author"] == author for book in existing):
                    skipped_count += 1
                    continue

                book_id = self.db.add_book(title, author)
                added_count += 1

                # Generate summary if AI service is available
                if self.ai_service:
                    try:
                        summary = self.ai_service.generate_summary(title, author)
                        self.db.update_summary(book_id, summary)
                    except Exception:
                        pass  # Continue even if summary generation fails

            progress_bar["value"] = len(books)
            progress_dialog.destroy()

            self._refresh_book_list()

            message = f"Added {added_count} book(s)."
            if skipped_count > 0:
                message += (
                    f"\nSkipped {skipped_count} book(s) (duplicates or no author)."
                )

            messagebox.showinfo("Books Added", message)

        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {str(e)}")

    def _refresh_book_list(self):
        """Refresh the book list."""
        self.book_listbox.delete(0, tk.END)
        books = self.db.get_all_books()

        for book in books:
            display_text = f"{book['title']} - {book['author']}"
            if not book["summary"]:
                display_text += " (no summary)"
            self.book_listbox.insert(tk.END, display_text)

        self.book_count_label.config(text=f"Total books: {len(books)}")

        # Store books for reference
        self.books = books

    def _view_book_details(self):
        """View details of selected book."""
        selection = self.book_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a book to view details.")
            return

        idx = selection[0]
        book = self.books[idx]

        # Create details dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Book Details")
        dialog.geometry("550x450")
        dialog.transient(self.root)

        # Book info
        info_frame = ttk.Frame(dialog)
        info_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(info_frame, text="Title:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=2
        )
        ttk.Label(info_frame, text=book["title"], font=("Arial", 10)).grid(
            row=0, column=1, sticky="w", pady=2, padx=10
        )

        ttk.Label(info_frame, text="Author:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=2
        )
        ttk.Label(info_frame, text=book["author"], font=("Arial", 10)).grid(
            row=1, column=1, sticky="w", pady=2, padx=10
        )

        ttk.Label(info_frame, text="Added:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=2
        )
        ttk.Label(info_frame, text=book["created_at"], font=("Arial", 10)).grid(
            row=2, column=1, sticky="w", pady=2, padx=10
        )

        # Summary
        summary_frame = ttk.LabelFrame(dialog, text="Summary", padding=10)
        summary_frame.pack(fill="both", expand=True, padx=20, pady=10)

        summary_text = scrolledtext.ScrolledText(
            summary_frame, wrap=tk.WORD, height=15, font=("Arial", 10)
        )
        summary_text.pack(fill="both", expand=True)

        if book["summary"]:
            summary_text.insert("1.0", book["summary"])
        else:
            summary_text.insert("1.0", "No summary available.\n\n")
            if self.ai_service:
                summary_text.insert("end", "Click 'Generate Summary' to create one.")

        summary_text.config(state="disabled")

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        if not book["summary"] and self.ai_service:

            def generate_summary():
                try:
                    summary_text.config(state="normal")
                    summary_text.delete("1.0", tk.END)
                    summary_text.insert("1.0", "Generating summary...")
                    summary_text.config(state="disabled")
                    dialog.update()

                    summary = self.ai_service.generate_summary(
                        book["title"], book["author"]
                    )
                    self.db.update_summary(book["id"], summary)

                    summary_text.config(state="normal")
                    summary_text.delete("1.0", tk.END)
                    summary_text.insert("1.0", summary)
                    summary_text.config(state="disabled")

                    self._refresh_book_list()
                    messagebox.showinfo("Success", "Summary generated successfully!")
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Failed to generate summary: {str(e)}"
                    )

            ttk.Button(
                button_frame, text="Generate Summary", command=generate_summary
            ).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def _start_flashcard_mode(self):
        """Start flashcard mode."""
        self.flashcard_books = self.db.get_all_books()

        if not self.flashcard_books:
            messagebox.showinfo(
                "No Books",
                "No books in your bookshelf yet. Add some books to get started!",
            )
            return

        self.current_flashcard_index = 0
        self.flashcard_revealed = False

        # Switch to flashcard tab
        self.notebook.select(self.flashcard_frame)

        # Enable buttons
        self.start_button.config(state="disabled")
        self.reveal_button.config(state="normal")
        self.next_button.config(state="normal")
        self.prev_button.config(state="normal")

        self._display_current_flashcard()

    def _display_current_flashcard(self):
        """Display the current flashcard."""
        if not self.flashcard_books:
            return

        book = self.flashcard_books[self.current_flashcard_index]

        # Update title and author
        self.card_title_label.config(text=book["title"])
        self.card_author_label.config(text=f"by {book['author']}")

        # Clear summary
        self.card_summary_text.config(state="normal")
        self.card_summary_text.delete("1.0", tk.END)
        self.card_summary_text.config(state="disabled")

        # Update progress
        self.progress_label.config(
            text=f"Card {self.current_flashcard_index + 1} of {len(self.flashcard_books)}"
        )

        # Reset revealed state
        self.flashcard_revealed = False
        self.reveal_button.config(text="Reveal Summary")

        # Update button states
        self.prev_button.config(
            state="normal" if self.current_flashcard_index > 0 else "disabled"
        )
        self.next_button.config(
            state="normal"
            if self.current_flashcard_index < len(self.flashcard_books) - 1
            else "disabled"
        )

    def _reveal_summary(self):
        """Reveal or hide the summary."""
        if not self.flashcard_books:
            return

        book = self.flashcard_books[self.current_flashcard_index]

        if not self.flashcard_revealed:
            # Show summary
            self.card_summary_text.config(state="normal")
            self.card_summary_text.delete("1.0", tk.END)

            if book["summary"]:
                self.card_summary_text.insert("1.0", book["summary"])
            else:
                self.card_summary_text.insert(
                    "1.0", "No summary available for this book."
                )

            self.card_summary_text.config(state="disabled")
            self.flashcard_revealed = True
            self.reveal_button.config(text="Hide Summary")
        else:
            # Hide summary
            self.card_summary_text.config(state="normal")
            self.card_summary_text.delete("1.0", tk.END)
            self.card_summary_text.config(state="disabled")
            self.flashcard_revealed = False
            self.reveal_button.config(text="Reveal Summary")

    def _next_flashcard(self):
        """Move to next flashcard."""
        if self.current_flashcard_index < len(self.flashcard_books) - 1:
            self.current_flashcard_index += 1
            self._display_current_flashcard()

    def _prev_flashcard(self):
        """Move to previous flashcard."""
        if self.current_flashcard_index > 0:
            self.current_flashcard_index -= 1
            self._display_current_flashcard()

    def _start_tutorial(self):
        """Start the interactive tutorial with example books."""
        # Check if example_books.txt exists
        example_file = os.path.join(os.path.dirname(__file__), "example_books.txt")

        if not os.path.exists(example_file):
            messagebox.showerror(
                "Tutorial Error",
                "Could not find example_books.txt file.\n\n"
                "The tutorial requires this file to demonstrate the application features."
            )
            return

        # Show welcome dialog
        welcome_msg = (
            "Welcome to Bookshelf Flashcards Tutorial!\n\n"
            "This tutorial will help you learn how to use the application by:\n\n"
            "1. Loading example books from example_books.txt\n"
            "2. Showing you how to view and manage books\n"
            "3. Demonstrating the flashcard mode\n"
            "4. Allowing you to add your own books\n\n"
            "The example books will be added to your bookshelf.\n"
            "When you're done experimenting, you can click\n"
            "'Clear Example Books' to remove them.\n\n"
            "Would you like to start the tutorial?"
        )

        if not messagebox.askyesno("Start Tutorial", welcome_msg):
            return

        # Load example books
        try:
            books = parse_book_file(example_file)

            if not books:
                messagebox.showerror(
                    "Tutorial Error",
                    "No books found in example_books.txt."
                )
                return

            # Add example books to database
            added_count = 0
            for title, author in books:
                if not author:
                    continue  # Skip books without authors in tutorial

                # Check for duplicates
                existing = self.db.search_books_by_title(title)
                if any(book["author"] == author for book in existing):
                    continue

                self.db.add_book(title, author)
                added_count += 1

            self._refresh_book_list()

            # Show tutorial instructions
            tutorial_msg = (
                f"Tutorial Started! Added {added_count} example books.\n\n"
                "Here's what you can do now:\n\n"
                "📚 Book List Tab (current):\n"
                "  • View all books in the list below\n"
                "  • Double-click a book to view details\n"
                "  • Click 'Add Book' to add your own books\n"
                "  • Click 'View Details' to see summaries\n\n"
                "🎴 Flashcard Mode Tab:\n"
                "  • Switch to this tab to review books\n"
                "  • Click 'Start Flashcards' to begin\n"
                "  • Use Previous/Next to navigate\n"
                "  • Click 'Reveal Summary' to see the summary\n\n"
                "🧹 When you're done:\n"
                "  • Click 'Clear Example Books' to remove them\n\n"
                "Try it out and explore the features!"
            )

            messagebox.showinfo("Tutorial Instructions", tutorial_msg)

        except Exception as e:
            messagebox.showerror(
                "Tutorial Error",
                f"Error loading example books: {str(e)}"
            )

    def _clear_example_books(self):
        """Clear example books from the database."""
        example_file = os.path.join(os.path.dirname(__file__), "example_books.txt")

        if not os.path.exists(example_file):
            messagebox.showwarning(
                "Clear Example Books",
                "Could not find example_books.txt to identify example books."
            )
            return

        try:
            # Parse example books file to know which books to remove
            books = parse_book_file(example_file)

            if not books:
                messagebox.showinfo(
                    "Clear Example Books",
                    "No example books found to clear."
                )
                return

            # Ask for confirmation
            confirm_msg = (
                "This will remove books from example_books.txt that are\n"
                "currently in your bookshelf.\n\n"
                "Are you sure you want to clear these example books?"
            )

            if not messagebox.askyesno("Confirm Clear", confirm_msg):
                return

            # Remove example books from database
            removed_count = 0
            for title, author in books:
                if not author:
                    continue

                # Find and remove the book
                existing = self.db.search_books_by_title(title)
                for book in existing:
                    if book["author"] == author:
                        cursor = self.db.conn.cursor()
                        cursor.execute("DELETE FROM books WHERE id = ?", (book["id"],))
                        self.db.conn.commit()
                        removed_count += 1

            self._refresh_book_list()

            messagebox.showinfo(
                "Example Books Cleared",
                f"Removed {removed_count} example book(s) from your bookshelf.\n\n"
                "You can now start adding your own books!"
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error clearing example books: {str(e)}"
            )

    def _show_about(self):
        """Show about dialog."""
        about_text = """Bookshelf Flashcards
Version 1.0

A helpful tool to refresh one's memory of the books
that they have read on their bookshelf.

© 2024 Bookshelf Flashcards"""

        messagebox.showinfo("About Bookshelf Flashcards", about_text)

    def _show_book_list(self):
        """Switch to book list tab."""
        self.notebook.select(self.list_frame)

    def close(self):
        """Close the application."""
        self.db.close()


def main():
    """Main entry point for the GUI application."""
    # pylint: disable=import-outside-toplevel
    import argparse

    parser = argparse.ArgumentParser(
        description="Bookshelf Flashcards - GUI Application"
    )
    parser.add_argument(
        "--db",
        default="bookshelf.db",
        help="Database file path (default: bookshelf.db)",
    )

    args = parser.parse_args()

    root = tk.Tk()
    app = BookshelfGUI(root, db_path=args.db)

    # Handle window close
    root.protocol("WM_DELETE_WINDOW", lambda: (app.close(), root.destroy()))

    root.mainloop()


if __name__ == "__main__":
    main()
