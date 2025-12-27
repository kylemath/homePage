#!/bin/bash
# Test script to run all homepage update scripts locally
# This mimics what the GitHub Actions workflow does

set -e  # Exit on any error

echo "=================================================="
echo "Testing Homepage Update Scripts Locally"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "publications_env" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv publications_env
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source publications_env/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install requests beautifulsoup4 lxml -q
pip install scholarly || echo "⚠️  scholarly installation failed (this is okay)"

echo ""
echo "=================================================="
echo "Environment Setup Complete"
echo "=================================================="
echo ""

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  WARNING: GITHUB_TOKEN not set"
    echo "   You may hit rate limits without it."
    echo "   To set it: export GITHUB_TOKEN=your_token_here"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ GITHUB_TOKEN is set"
fi

echo ""

# Create backup
echo "💾 Creating backup of index.html..."
cp index.html index.html.test-backup
cp catalogue_data.json catalogue_data.json.test-backup 2>/dev/null || true

echo ""
echo "=================================================="
echo "Test 1: Update Projects List"
echo "=================================================="
echo ""
python update_projects.py
echo "✅ Projects update completed"

echo ""
echo "=================================================="
echo "Test 2: Update Contributor Projects"
echo "=================================================="
echo ""
python update_contributor_projects.py
echo "✅ Contributor projects update completed"

echo ""
echo "=================================================="
echo "Test 3: Update Publications (Basic)"
echo "=================================================="
echo "Note: This can take 2-4 minutes..."
echo ""
timeout 240 python update_publications.py || {
    echo "⚠️  Publications update timed out or failed"
    echo "   Restoring backup..."
    cp index.html.test-backup index.html
}

# Count publications
PUB_COUNT=$(grep -c '<li><a href.*target="_blank">' index.html || echo "0")
echo ""
echo "📊 Publications found: $PUB_COUNT"

if [ "$PUB_COUNT" -lt 50 ]; then
    echo "⚠️  Too few publications, this might indicate an issue"
fi

echo ""
echo "=================================================="
echo "Test Results Summary"
echo "=================================================="
echo ""
echo "Files modified:"
git diff --name-only

echo ""
echo "Detailed changes:"
echo ""
echo "--- Changes to index.html ---"
git diff index.html | head -50

echo ""
echo "--- Changes to catalogue_data.json ---"
git diff catalogue_data.json | head -50

echo ""
echo "=================================================="
echo "What to do next:"
echo "=================================================="
echo ""
echo "1. Review the changes above"
echo "2. Test by opening index.html in a browser:"
echo "   open index.html"
echo ""
echo "3. If changes look good, you can:"
echo "   - Keep them: rm index.html.test-backup catalogue_data.json.test-backup"
echo "   - Discard them: mv index.html.test-backup index.html && mv catalogue_data.json.test-backup catalogue_data.json"
echo ""
echo "4. Deactivate virtual environment when done:"
echo "   deactivate"
echo ""

