"""
AI service module for generating book summaries using OpenAI API.
"""
import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv


class SummaryGenerator:
    """Generate book summaries using OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the summary generator.
        
        Args:
            api_key: OpenAI API key (if not provided, loads from environment)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
                "or create a .env file with your API key."
            )
        self.client = OpenAI(api_key=self.api_key)
    
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
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate and concise book summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
