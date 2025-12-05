#!/bin/bash
# Helper script to set up GITHUB_TOKEN for private repo automation

echo "=========================================="
echo "GitHub Token Setup for Private Repos"
echo "=========================================="
echo ""

# Check if token is already set in current session
if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ GITHUB_TOKEN is already set in current session"
    echo "   Token: ${GITHUB_TOKEN:0:8}..."
    echo ""
else
    echo "❌ GITHUB_TOKEN is not set in current session"
    echo ""
fi

# Check shell config files
SHELL_NAME=$(basename "$SHELL")
case "$SHELL_NAME" in
    zsh)
        CONFIG_FILE="$HOME/.zshrc"
        ;;
    bash)
        if [ -f "$HOME/.bash_profile" ]; then
            CONFIG_FILE="$HOME/.bash_profile"
        else
            CONFIG_FILE="$HOME/.bashrc"
        fi
        ;;
    *)
        CONFIG_FILE="$HOME/.profile"
        ;;
esac

echo "Detected shell: $SHELL_NAME"
echo "Config file: $CONFIG_FILE"
echo ""

# Check if token is in config file
if [ -f "$CONFIG_FILE" ] && grep -q "GITHUB_TOKEN" "$CONFIG_FILE"; then
    echo "✅ GITHUB_TOKEN found in $CONFIG_FILE"
    echo ""
    echo "If the token isn't working, you may need to:"
    echo "  1. Open a new terminal, OR"
    echo "  2. Run: source $CONFIG_FILE"
else
    echo "❌ GITHUB_TOKEN not found in $CONFIG_FILE"
    echo ""
    echo "To set up your GitHub token:"
    echo ""
    echo "1. Create a Personal Access Token:"
    echo "   → Go to: https://github.com/settings/tokens"
    echo "   → Click 'Generate new token (classic)'"
    echo "   → Select scope: 'repo' (full control of private repositories)"
    echo "   → Copy the generated token"
    echo ""
    echo "2. Add to your shell config:"
    echo "   → Run: echo 'export GITHUB_TOKEN=\"your_token_here\"' >> $CONFIG_FILE"
    echo "   → Then: source $CONFIG_FILE"
    echo ""
    echo "3. Or set temporarily (just for this session):"
    echo "   → Run: export GITHUB_TOKEN='your_token_here'"
    echo ""
fi

echo "=========================================="
echo "Testing Access"
echo "=========================================="
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  Cannot test - GITHUB_TOKEN not set"
    echo ""
    echo "After setting up, test with:"
    echo "  python check_private_repos.py"
else
    echo "Testing GitHub API access..."
    RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/user)
    
    if echo "$RESPONSE" | grep -q '"login"'; then
        LOGIN=$(echo "$RESPONSE" | grep '"login"' | head -1 | cut -d'"' -f4)
        echo "✅ Token is valid! Authenticated as: $LOGIN"
        echo ""
        echo "Now run the diagnostic:"
        echo "  python check_private_repos.py"
    else
        echo "❌ Token test failed"
        echo "   Response: $RESPONSE"
        echo ""
        echo "The token may be invalid or expired."
        echo "Create a new token at: https://github.com/settings/tokens"
    fi
fi

echo ""
echo "=========================================="

