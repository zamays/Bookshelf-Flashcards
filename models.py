"""
Database models for user authentication.
"""
import bcrypt
from flask_login import UserMixin
from typing import Optional


class User(UserMixin):
    """User model for authentication."""
    
    def __init__(self, user_id: int, email: str, password_hash: str, 
                 created_at: str, verified: bool = False):
        """
        Initialize a User object.
        
        Args:
            user_id: User's database ID
            email: User's email address
            password_hash: Hashed password
            created_at: Timestamp when user was created
            verified: Whether email is verified
        """
        self.id = user_id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.verified = verified
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password as string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """
        Check if provided password matches the user's password.
        
        Args:
            password: Plain text password to check
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def get_id(self) -> str:
        """
        Return user ID as string for Flask-Login.
        
        Returns:
            User ID as string
        """
        return str(self.id)
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User {self.email}>"
