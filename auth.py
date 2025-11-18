"""
Authentication logic for user management.
"""
import re
import logging
from typing import Optional
from models import User
from validation import ValidationError

logger = logging.getLogger(__name__)

# Email validation regex (basic)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def validate_email(email: str) -> str:
    """
    Validate and normalize email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        Validated email address
        
    Raises:
        ValidationError: If email is invalid
    """
    if not isinstance(email, str):
        raise ValidationError("Email must be a string")
    
    email = email.strip().lower()
    
    if not email:
        raise ValidationError("Email cannot be empty")
    
    if len(email) > 254:  # RFC 5321
        raise ValidationError("Email address is too long")
    
    if not EMAIL_REGEX.match(email):
        raise ValidationError("Invalid email format")
    
    return email


def validate_password(password: str) -> str:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Validated password
        
    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if not isinstance(password, str):
        raise ValidationError("Password must be a string")
    
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    if len(password) > 128:
        raise ValidationError("Password is too long (max 128 characters)")
    
    # Check for at least one lowercase, one uppercase, and one digit
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")
    
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit")
    
    return password


def create_user(db, email: str, password: str) -> Optional[int]:
    """
    Create a new user account.
    
    Args:
        db: Database connection
        email: User's email address
        password: User's password
        
    Returns:
        User ID if successful, None if user already exists
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate inputs
    validated_email = validate_email(email)
    validated_password = validate_password(password)
    
    # Check if user already exists
    existing_user = db.get_user_by_email(validated_email)
    if existing_user:
        return None
    
    # Hash password and create user
    password_hash = User.hash_password(validated_password)
    user_id = db.create_user(validated_email, password_hash)
    
    logger.info(f"New user registered: {validated_email}")
    return user_id


def authenticate_user(db, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password.
    
    Args:
        db: Database connection
        email: User's email address
        password: User's password
        
    Returns:
        User object if authentication successful, None otherwise
    """
    try:
        validated_email = validate_email(email)
    except ValidationError:
        return None
    
    user = db.get_user_by_email(validated_email)
    if not user:
        return None
    
    if not user.check_password(password):
        return None
    
    logger.info(f"User authenticated: {validated_email}")
    return user
