"""
Script to fill in missing book summaries in the database.
"""
import sqlite3
from ai_service import SummaryGenerator


def fill_summaries():
    """Fill in missing summaries for all books in the database."""
    # Initialize the AI service
    try:
        generator = SummaryGenerator()
    except ValueError as e:
        print(f"Error initializing AI service: {e}")
        return

    # Connect to database
    conn = sqlite3.connect('bookshelf.db')
    cursor = conn.cursor()

    # Get all books without summaries
    cursor.execute("""
        SELECT id, title, author
        FROM books
        WHERE summary IS NULL OR summary = ''
    """)
    books = cursor.fetchall()

    print(f"Found {len(books)} books without summaries.")

    # Generate and update summaries
    for book_id, title, author in books:
        print(f"\nGenerating summary for: {title} by {author}")
        try:
            summary = generator.generate_summary(title, author)
            cursor.execute("""
                UPDATE books
                SET summary = ?
                WHERE id = ?
            """, (summary, book_id))
            conn.commit()
            print(f"✓ Summary added successfully!")
        except Exception as e:
            print(f"✗ Error generating summary: {e}")
            continue

    # Show results
    cursor.execute("SELECT COUNT(*) FROM books WHERE summary IS NOT NULL AND summary != ''")
    count = cursor.fetchone()[0]
    print(f"\n{count} books now have summaries.")

    conn.close()


if __name__ == "__main__":
    fill_summaries()
