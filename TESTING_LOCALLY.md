# Testing Homepage Scripts Locally

This guide shows you how to test the automated update scripts that run in GitHub Actions.

## Quick Start

```bash
# Run the full test suite
./test_scripts_locally.sh
```

## Manual Testing (Step by Step)

### 1. Set up environment

```bash
# Activate virtual environment (if it exists)
source publications_env/bin/activate

# Or create a new one if needed
python3 -m venv test_env
source test_env/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install requests beautifulsoup4 lxml scholarly
```

### 2. Set GitHub Token (Optional but Recommended)

Without a token, you'll hit API rate limits quickly.

```bash
# Set for current session
export GITHUB_TOKEN=your_github_token_here

# Or add to ~/.zshrc or ~/.bashrc for persistence
echo 'export GITHUB_TOKEN=your_github_token_here' >> ~/.zshrc
```

Get a token at: https://github.com/settings/tokens

### 3. Test Individual Scripts

#### Test Projects Update

```bash
# Create backup first
cp index.html index.html.backup
cp catalogue_data.json catalogue_data.json.backup

# Run the script
python update_projects.py

# Check what changed
git diff index.html
git diff catalogue_data.json

# Restore if needed
mv index.html.backup index.html
mv catalogue_data.json.backup catalogue_data.json
```

#### Test Contributor Projects Update

```bash
# Create backup
cp index.html index.html.backup

# Run the script
python update_contributor_projects.py

# Check changes
git diff index.html

# Restore if needed
mv index.html.backup index.html
```

#### Test Publications Update

```bash
# Create backup
cp index.html index.html.backup

# Run the script (this takes 2-4 minutes)
python update_publications.py

# Check results
grep -c '<li><a href.*target="_blank">' index.html

# Restore if needed
mv index.html.backup index.html
```

### 4. Preview Changes in Browser

**⚠️ Important:** To see the catalogue cards working, you MUST run a local web server. 
Opening `index.html` directly won't load the catalogues due to browser security restrictions.

```bash
# Start local web server (REQUIRED for catalogues to work)
./preview_site.sh

# Then open in browser: http://localhost:8000
```

**Alternative methods:**

```bash
# Python 3
python3 -m http.server 8000

# PHP
php -S localhost:8000

# Then visit: http://localhost:8000
```

**Quick preview (catalogues won't work):**
```bash
# This will open the file directly - catalogues will be empty!
open index.html
```

### 5. Clean Up

```bash
# Remove backups if everything looks good
rm -f index.html.backup catalogue_data.json.backup

# Deactivate virtual environment
deactivate
```

## What Each Script Does

### `update_projects.py`
- Fetches all your GitHub repositories
- Sorts them by last commit date
- Updates the "Recent Projects" section in `index.html`
- Creates/updates `catalogue_data.json` with project metadata
- Looks for `catalogue.json` in each repo for custom metadata

### `update_contributor_projects.py`
- Finds your forked repositories
- Identifies which ones you've contributed to
- Adds a "Contributor Projects" section in `index.html`
- Shows your contribution status (commits ahead, contributor status)

### `update_publications.py`
- Scrapes your Google Scholar profile
- Fetches all publications with pagination
- Updates the "Recent Publications" section in `index.html`
- Sorts publications by year (newest first)
- Requires at least 50 publications to prevent data loss

### `update_publications_scholarly.py`
- Alternative to basic scraping using the `scholarly` library
- More robust but can be slower
- Used as fallback in GitHub Actions

## Troubleshooting

### Rate Limiting

**Problem:** Getting 403 errors or incomplete results

**Solution:** Set `GITHUB_TOKEN` environment variable

```bash
export GITHUB_TOKEN=your_token_here
```

### Publications Not Updating

**Problem:** Publications count is low or script fails

**Solutions:**
1. Google Scholar may be rate limiting - wait and try again
2. The script requires at least 50 publications
3. Check your internet connection
4. Try the scholarly version: `python update_publications_scholarly.py`

### Changes Not Appearing

**Problem:** Script runs but `index.html` doesn't change

**Solutions:**
1. Check if there are actually any changes: `git diff index.html`
2. Verify the HTML structure matches what the script expects
3. Look for error messages in the script output

### Virtual Environment Issues

**Problem:** Module not found errors

**Solution:** Make sure you're in the virtual environment

```bash
# Check if you're in a virtual environment
which python  # Should show path to venv

# If not, activate it
source publications_env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## GitHub Actions vs Local Testing

The GitHub Actions workflow:
- Runs automatically on schedule (daily for projects, monthly for publications)
- Runs on push to main branch
- Can be triggered manually via workflow_dispatch
- Has built-in retry logic and fallbacks
- Automatically commits and deploys changes

Local testing:
- Manual control
- Faster iteration
- See immediate results
- No automatic deployment
- Good for debugging

## Next Steps

After testing locally and verifying changes:

```bash
# Stage your changes
git add index.html catalogue_data.json

# Commit with descriptive message
git commit -m "Update projects and publications lists"

# Push to GitHub (triggers automatic deployment)
git push origin main
```

The GitHub Actions workflow will:
1. Run your update scripts
2. Build the site
3. Deploy to GitHub Pages

Check the Actions tab in your GitHub repo to see the deployment progress.

