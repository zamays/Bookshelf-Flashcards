"""
AI service module for generating book summaries using Google AI Studio API.
"""
import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv


class SummaryGenerator:
    """Generate book summaries using Google AI Studio API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the summary generator.
        
        Args:
            api_key: Google AI Studio API key (if not provided, loads from environment)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError(
                "Google AI Studio API key not found. Please set GOOGLE_AI_API_KEY environment variable "
                "or create a .env file with your API key."
            )
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_summary(self, title: str, author: str) -> str:
        """
        Generate a summary for a book.
        
        Args:
            title: Book title
            author: Book author
            
        Returns:
            Book summary
        """
        prompt = f"""Please provide a concise but comprehensive summary of the book "{title}" by {author}. 
Include the main themes, key plot points (if fiction), and the overall message or takeaways. 
Keep it to about 200-300 words so it can serve as a memory refresher."""
        
        try:
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                raise Exception("No content generated from the AI model")
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
