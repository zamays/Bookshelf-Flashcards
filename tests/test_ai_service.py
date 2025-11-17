"""
Unit tests for ai_service.py module.
"""
import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from ai_service import SummaryGenerator


class TestSummaryGeneratorInit:
    """Tests for SummaryGenerator initialization."""

    def test_init_with_api_key(self):
        """Test initialization with API key provided."""
        with patch('ai_service.genai.configure') as mock_configure, \
             patch('ai_service.genai.GenerativeModel') as mock_model:
            
            generator = SummaryGenerator(api_key="test_api_key_12345")
            
            assert generator.api_key == "test_api_key_12345"
            mock_configure.assert_called_once_with(api_key="test_api_key_12345")
            mock_model.assert_called_once_with('models/gemini-2.5-flash')

    def test_init_with_env_variable(self):
        """Test initialization with API key from environment."""
        with patch('ai_service.genai.configure') as mock_configure, \
             patch('ai_service.genai.GenerativeModel') as mock_model, \
             patch.dict(os.environ, {'GOOGLE_AI_API_KEY': 'env_api_key_67890'}):
            
            generator = SummaryGenerator()
            
            assert generator.api_key == "env_api_key_67890"
            mock_configure.assert_called_once_with(api_key="env_api_key_67890")

    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with patch.dict(os.environ, {}, clear=True), \
             patch('ai_service.load_dotenv'):
            
            with pytest.raises(ValueError) as exc_info:
                SummaryGenerator()
            
            assert "Google AI Studio API key not found" in str(exc_info.value)

    def test_init_with_placeholder_api_key_raises_error(self):
        """Test that initialization with placeholder API key raises ValueError."""
        with patch.dict(os.environ, {'GOOGLE_AI_API_KEY': 'your_api_key_here'}), \
             patch('ai_service.load_dotenv'):
            
            with pytest.raises(ValueError) as exc_info:
                SummaryGenerator()
            
            assert "Google AI Studio API key not found" in str(exc_info.value)

    def test_init_loads_dotenv(self):
        """Test that initialization loads environment from .env file."""
        with patch('ai_service.load_dotenv') as mock_load_dotenv, \
             patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_AI_API_KEY': 'test_key'}):
            
            SummaryGenerator()
            mock_load_dotenv.assert_called_once()


class TestSummaryGeneratorGenerateSummary:
    """Tests for generate_summary method."""

    def test_generate_summary_success(self):
        """Test successful summary generation."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            # Setup mock
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "This is a test summary of 1984."
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            summary = generator.generate_summary("1984", "George Orwell")
            
            assert summary == "This is a test summary of 1984."
            mock_model.generate_content.assert_called_once()

    def test_generate_summary_with_correct_prompt(self):
        """Test that generate_summary creates correct prompt."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Test summary"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            generator.generate_summary("The Great Gatsby", "F. Scott Fitzgerald")
            
            # Check that the prompt includes title and author
            call_args = mock_model.generate_content.call_args[0][0]
            assert "The Great Gatsby" in call_args
            assert "F. Scott Fitzgerald" in call_args
            assert "summary" in call_args.lower()

    def test_generate_summary_strips_whitespace(self):
        """Test that summary is stripped of leading/trailing whitespace."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "  \n  Test summary with whitespace  \n  "
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            summary = generator.generate_summary("Title", "Author")
            
            assert summary == "Test summary with whitespace"

    def test_generate_summary_empty_response(self):
        """Test handling of empty response from API."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = ""
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            
            with pytest.raises(ValueError) as exc_info:
                generator.generate_summary("Title", "Author")
            
            assert "No content generated" in str(exc_info.value)

    def test_generate_summary_none_response(self):
        """Test handling of None response from API."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_model.generate_content.return_value = None
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            
            with pytest.raises(ValueError) as exc_info:
                generator.generate_summary("Title", "Author")
            
            assert "No content generated" in str(exc_info.value)


class TestSummaryGeneratorErrorHandling:
    """Tests for error handling in SummaryGenerator."""

    def test_api_exception_raises_value_error(self):
        """Test that API exceptions are wrapped in ValueError."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("API Error")
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            
            with pytest.raises(ValueError) as exc_info:
                generator.generate_summary("Title", "Author")
            
            assert "Error generating summary" in str(exc_info.value)
            assert "API Error" in str(exc_info.value)

    def test_network_error_handling(self):
        """Test handling of network errors."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = ConnectionError("Network error")
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            
            with pytest.raises(ValueError) as exc_info:
                generator.generate_summary("Title", "Author")
            
            assert "Error generating summary" in str(exc_info.value)

    def test_timeout_error_handling(self):
        """Test handling of timeout errors."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = TimeoutError("Request timeout")
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            
            with pytest.raises(ValueError) as exc_info:
                generator.generate_summary("Title", "Author")
            
            assert "Error generating summary" in str(exc_info.value)


class TestSummaryGeneratorEdgeCases:
    """Tests for edge cases in SummaryGenerator."""

    def test_special_characters_in_title(self):
        """Test generating summary for book with special characters."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Test summary"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            summary = generator.generate_summary("Book's \"Title\": Part & More!", "Author")
            
            assert summary == "Test summary"
            mock_model.generate_content.assert_called_once()

    def test_unicode_characters_in_title(self):
        """Test generating summary for book with Unicode characters."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Test summary"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            summary = generator.generate_summary("Café Müller — 東京物語", "François Lefèvre")
            
            assert summary == "Test summary"

    def test_empty_title(self):
        """Test generating summary with empty title."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Test summary"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            summary = generator.generate_summary("", "Author")
            
            # Should still work, just with empty title in prompt
            assert summary == "Test summary"

    def test_empty_author(self):
        """Test generating summary with empty author."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Test summary"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            summary = generator.generate_summary("Title", "")
            
            # Should still work, just with empty author in prompt
            assert summary == "Test summary"

    def test_very_long_title(self):
        """Test generating summary for book with very long title."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Test summary"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            long_title = "A" * 1000
            summary = generator.generate_summary(long_title, "Author")
            
            assert summary == "Test summary"


class TestSummaryGeneratorGracefulDegradation:
    """Tests for graceful degradation when API is unavailable."""

    def test_graceful_degradation_api_unavailable(self):
        """Test that meaningful error is raised when API is unavailable."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("API temporarily unavailable")
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            
            with pytest.raises(ValueError) as exc_info:
                generator.generate_summary("Title", "Author")
            
            error_message = str(exc_info.value)
            assert "Error generating summary" in error_message
            assert "API temporarily unavailable" in error_message

    def test_invalid_api_key_during_generation(self):
        """Test handling of invalid API key during generation."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("Invalid API key")
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="invalid_key")
            
            with pytest.raises(ValueError) as exc_info:
                generator.generate_summary("Title", "Author")
            
            assert "Error generating summary" in str(exc_info.value)

    def test_rate_limit_error(self):
        """Test handling of rate limit errors."""
        with patch('ai_service.genai.configure'), \
             patch('ai_service.genai.GenerativeModel') as mock_model_class:
            
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("Rate limit exceeded")
            mock_model_class.return_value = mock_model
            
            generator = SummaryGenerator(api_key="test_key")
            
            with pytest.raises(ValueError) as exc_info:
                generator.generate_summary("Title", "Author")
            
            assert "Error generating summary" in str(exc_info.value)
            assert "Rate limit exceeded" in str(exc_info.value)
