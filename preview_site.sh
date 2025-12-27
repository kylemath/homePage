#!/bin/bash
# Preview your homepage locally with a web server
# This allows the catalogue cards to load properly

echo "🚀 Starting local web server..."
echo ""
echo "   Your site will be available at:"
echo "   👉 http://localhost:8000"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""
echo "=================================================="
echo ""

# Try Python 3 first (most common)
if command -v python3 &> /dev/null; then
    python3 -m http.server 8000
# Try Python 2 as fallback
elif command -v python &> /dev/null; then
    python -m SimpleHTTPServer 8000
# Try PHP as alternative
elif command -v php &> /dev/null; then
    php -S localhost:8000
else
    echo "❌ Error: No suitable web server found."
    echo ""
    echo "Please install Python or PHP to preview your site locally."
    echo ""
    echo "On macOS (using Homebrew):"
    echo "  brew install python3"
    echo ""
    exit 1
fi

