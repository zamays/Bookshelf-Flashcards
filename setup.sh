#!/bin/bash
# Setup script for Bookshelf-Flashcards

set -euo pipefail  # Exit on error, undefined variables, and pipe failures

echo "=========================================="
echo "Bookshelf-Flashcards Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.7 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Check pip3 availability
echo "Checking pip3..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed."
    echo "Please install pip3 (Python package manager)."
    exit 1
fi
echo "✓ Found pip3"
echo ""

# Install dependencies
echo "Installing dependencies..."
if pip3 install -r requirements.txt; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Setup .env file
echo "Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file from .env.example"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Google AI Studio API key"
    echo "   The application can run without it, but won't generate summaries."
    echo ""
    
    # Check if running in interactive mode
    if [ -t 0 ]; then
        read -p "Do you have a Google AI Studio API key to add now? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter your Google AI Studio API key: " api_key
            if [ -n "$api_key" ]; then
                # Write the API key to the newly created .env file
                # This is safe because we just created it from .env.example above
                printf "# Google AI Studio API Key for generating book summaries\nGOOGLE_AI_API_KEY=%s\n" "$api_key" > .env
                echo "✓ API key saved to .env"
            fi
        else
            echo "You can add it later by editing the .env file"
        fi
    else
        echo "Non-interactive mode detected. You can add your API key later by editing the .env file"
    fi
else
    echo "✓ .env file already exists"
fi
echo ""

# Test the installation
echo "Testing installation..."
if python3 bookshelf.py --help > /dev/null 2>&1; then
    echo "✓ Application is ready to use!"
else
    echo "❌ There was a problem with the installation"
    exit 1
fi
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Quick Start:"
echo "  1. Add books from the example file:"
echo "     python3 bookshelf.py add-file example_books.txt"
echo ""
echo "  2. View your bookshelf:"
echo "     python3 bookshelf.py list"
echo ""
echo "  3. Start flashcard mode:"
echo "     python3 bookshelf.py flashcard"
echo ""
echo "For more information, see README.md"
echo ""
