"""
AI service module for generating book summaries using Google AI Studio API.
"""
import sys
from typing import Optional

# Fix for Python 3.9: Add packages_distributions from importlib_metadata to importlib.metadata
if sys.version_info < (3, 10):
    import importlib.metadata
    try:
        import importlib_metadata
        if not hasattr(importlib.metadata, 'packages_distributions'):
            importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
    except ImportError:
        pass  # importlib_metadata not available, will fail later if needed

import google.generativeai as genai
from config import get_config, Config


class SummaryGenerator:
    """Generate book summaries using Google AI Studio API."""
    def __init__(self, api_key: Optional[str] = None, config: Optional[Config] = None):
        """
        Initialize the summary generator.

        Args:
            api_key: Google AI Studio API key (if not provided, loads from config)
            config: Configuration instance (if not provided, uses global config)
        """
        self.config = config or get_config()
        
        # Get API key from parameter or config
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self.config.get_google_ai_api_key()
        
        if not self.api_key:
            raise ValueError(
                "Google AI Studio API key not found. Please set "
                "GOOGLE_AI_API_KEY environment variable or create "
                "a .env file with your API key."
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    def generate_summary(self, title: str, author: str) -> str:
        """
        Generate a summary for a book.

        Args:
            title: Book title
            author: Book author

        Returns:
            Book summary
        """
        prompt = (
            f'Please provide a concise but comprehensive summary of the book '
            f'"{title}" by {author}. '
            f'Include the main themes, key plot points (if fiction), and the '
            f'overall message or takeaways. '
            f'Keep it to about 200-300 words so it can serve as a memory refresher.'
        )
        try:
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                raise ValueError("No content generated from the AI model")
            return response.text.strip()
        except Exception as e:
            # Never expose API keys in error messages
            error_msg = str(e)
            # Sanitize error message to remove any potential API key exposure
            if self.api_key and self.api_key in error_msg:
                error_msg = error_msg.replace(self.api_key, '[REDACTED]')
            raise ValueError(f"Error generating summary: {error_msg}") from e
