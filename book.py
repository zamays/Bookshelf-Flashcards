"""Book model for the Bookshelf Flashcards application."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Book:
    """Represents a book in the library."""
    
    title: str
    author: str
    is_read: bool = False
    notes: Optional[str] = None
    
    def to_dict(self):
        """Convert book to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create book from dictionary."""
        return cls(**data)
    
    def mark_as_read(self):
        """Mark this book as read."""
        self.is_read = True
    
    def mark_as_unread(self):
        """Mark this book as unread."""
        self.is_read = False
