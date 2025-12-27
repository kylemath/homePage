# Private Repository Automation Guide

## Problem: Private repos not appearing on homepage

When you have a **private GitHub repository** with a **public deployment** (Netlify, Vercel, etc.), the automation script needs special configuration to find it.

## Root Causes

1. **GitHub API Access**: Private repos require authentication via `GITHUB_TOKEN`
2. **Homepage URL**: The repo must have its homepage field set in GitHub
3. **Public Files**: The `catalogue.json` must be accessible on the public site

---

## Quick Fix Checklist

### ✅ Step 1: Set up GitHub Token

```bash
# Run the setup helper
./setup_github_token.sh
```

If you don't have a token yet:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scope: **repo** (full control of private repositories)
4. Copy the token
5. Add to your shell config:
   ```bash
   echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.zshrc
   source ~/.zshrc
   ```

### ✅ Step 2: Check Your Private Repos

```bash
# Activate virtual environment
source venv/bin/activate

# Run diagnostic script
python check_private_repos.py
```

This will show you:
- Which private repos are missing homepage URLs
- Which repos don't have `catalogue.json` files
- Which files are incorrectly configured
- Which screenshots are missing

### ✅ Step 3: Fix Each Private Repo

For each private repo that you want on your homepage:

#### 3a. Set Homepage URL in GitHub

1. Go to your repo on GitHub
2. Click "Settings" (gear icon)
3. Scroll to "Website" section
4. Enter your deployment URL: `https://yourproject.netlify.app`
5. Click "Save"

#### 3b. Create `catalogue.json` in Repo

Add this file to your repo root:

```json
{
  "id": "uniqueProjectId",
  "title": "Your Project Title",
  "oneLiner": "A brief description of your project",
  "kind": "page",
  "categories": ["category1", "category2"],
  "tags": ["tag1", "tag2"],
  "status": "published",
  "demoUrl": "https://yourproject.netlify.app",
  "screenshot": "screenshot.png"
}
```

**Important fields:**
- `kind`: Choose one:
  - `"page"` → Apps tab
  - `"longform"` → Writing tab  
  - `"project"` → Projects tab
- `screenshot`: Relative path to your screenshot file

#### 3c. Add Screenshot

1. Take a screenshot of your deployed site (recommended: 1200×800px)
2. Save as `screenshot.png` in repo root
3. Make sure it gets deployed with your site

#### 3d. Deploy Changes

```bash
git add catalogue.json screenshot.png
git commit -m "Add catalogue metadata"
git push
```

Wait for your deployment to complete (check Netlify/Vercel logs).

### ✅ Step 4: Verify Files Are Public

Test that your files are accessible:

```bash
# Test catalogue.json
curl https://yourproject.netlify.app/catalogue.json

# Test screenshot (should return 200)
curl -I https://yourproject.netlify.app/screenshot.png
```

Both should work even though the repo is private!

### ✅ Step 5: Update Your Homepage

```bash
# Make sure token is set
source venv/bin/activate

# Run the update script
python update_projects.py
```

Your private repo should now appear in `catalogue_data.json` and on your homepage!

---

## Example: Juventus2013 Repo

Here's how the Juventus repo was set up:

### GitHub Settings
- Repository: `kylemath/Juventus2013_Div3_2025` (private)
- Homepage: `https://juventus2013.netlify.app`

### catalogue.json
```json
{
  "id": "juventus2013teamsite",
  "title": "Juventus2013TeamSite",
  "oneLiner": "Webpage with schedule and roster and information for Juventus 2013 Boys Club Soccer Team",
  "demoUrl": "https://juventus2013.netlify.app",
  "screenshot": "https://raw.githubusercontent.com/kylemath/Juventus2013_Div3_2025/main/screenshot.png",
  "kind": "page",
  "categories": ["soccer", "webpage", "team"],
  "tags": ["soccer", "webpage", "team"],
  "status": "published"
}
```

### Public URLs (even though repo is private!)
- ✅ https://juventus2013.netlify.app/catalogue.json
- ✅ https://juventus2013.netlify.app/screenshot.png

---

## Troubleshooting

### Issue: "GITHUB_TOKEN not set"

**Solution:**
```bash
export GITHUB_TOKEN="your_token_here"
# Or add to ~/.zshrc permanently
```

### Issue: "No homepage URL set in GitHub"

**Solution:**
1. Go to repo Settings on GitHub
2. Add Website URL
3. Save changes
4. Run `python check_private_repos.py` again

### Issue: "catalogue.json NOT found"

**Solution:**
1. Create `catalogue.json` in repo root
2. Commit and push
3. Wait for deployment
4. Test: `curl https://yoursite.netlify.app/catalogue.json`

### Issue: "Screenshot not accessible"

**Solution:**
1. Verify screenshot file exists in repo
2. Check that it's not in `.gitignore`
3. Verify it's deployed: `curl -I https://yoursite.netlify.app/screenshot.png`
4. Check the `screenshot` field in `catalogue.json` matches the filename

### Issue: "Repo appears in wrong tab"

**Solution:**
1. Check the `kind` field in `catalogue.json`
2. Change to: `"page"`, `"longform"`, or `"project"`
3. Redeploy and run `python update_projects.py`

### Issue: "Token is invalid or expired"

**Solution:**
1. Create a new token at https://github.com/settings/tokens
2. Make sure "repo" scope is selected
3. Update your token: `export GITHUB_TOKEN="new_token"`

---

## How It Works

The automation script (`update_projects.py`) works like this:

1. **Fetch all repos** (public + private) using GitHub API with token
2. **For each repo**:
   - Check if it has a `homepage` URL set
   - If yes: Try to fetch `catalogue.json` from public homepage
   - If no homepage: Try GitHub raw URLs (only works for public repos)
3. **Parse catalogue.json** to get metadata
4. **Resolve screenshot** URL (homepage or GitHub)
5. **Write to `catalogue_data.json`**
6. **Homepage reads** `catalogue_data.json` and displays projects

### Why Private Repos Need Special Setup

- GitHub raw URLs (`raw.githubusercontent.com`) don't work for private repos
- BUT public deployments (Netlify/Vercel) work fine!
- The script checks the homepage URL **first**, so it finds your public files
- This is why setting the homepage URL in GitHub is critical

---

## Automation Workflow

To keep your homepage up to date:

```bash
# 1. Set token (once)
export GITHUB_TOKEN="your_token"

# 2. Add to automation script or cron job
cd /Users/kylemathewson/homePage
source venv/bin/activate
python update_projects.py

# Optional: commit changes automatically
git add catalogue_data.json index.html
git commit -m "Update projects [automated]"
git push
```

You can add this to a cron job or GitHub Action to run daily/weekly.

---

## Manual Workaround (No Token Required)

If you don't have a GitHub token set up yet, you can manually add private repos:

```bash
# Simple one-command solution
python add_private_repo.py https://yourproject.netlify.app
```

This script will:
1. Fetch `catalogue.json` from your public deployment
2. Resolve the correct screenshot URL
3. Add it to `catalogue_data.json` automatically
4. Your homepage will update immediately

**Requirements:**
- Repository must have `catalogue.json` deployed at the public URL
- Screenshot must be accessible
- No GitHub token needed!

**Example:**
```bash
python add_private_repo.py https://psych275.netlify.app
```

---

## Summary

For **private repos with public deployments**:

### Automated Approach (Recommended)

1. ✅ Create GitHub token with `repo` scope
2. ✅ Set `GITHUB_TOKEN` environment variable
3. ✅ Set homepage URL in GitHub repo settings
4. ✅ Add `catalogue.json` to repo and deploy it
5. ✅ Add `screenshot.png` to repo and deploy it
6. ✅ Verify both files are publicly accessible
7. ✅ Run `python update_projects.py`

Run `python check_private_repos.py` anytime to diagnose issues!

### Manual Approach (Quick Fix)

If token setup is problematic:
```bash
python add_private_repo.py https://yourproject.netlify.app
```

This works immediately but won't auto-update. Set up the token eventually for full automation.
