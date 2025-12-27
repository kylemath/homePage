# ✅ Complete Setup Summary - Private Repos with Public Sites

## Current Status

### What's Already Working ✅
1. ✅ **GitHub Actions has GITHUB_TOKEN** (line 56 in `.github/workflows/update-all-and-deploy.yml`)
2. ✅ **Script updated** to fetch from public Netlify sites
3. ✅ **Runs daily** at 1 AM automatically
4. ✅ **Example working**: fungioergosum.netlify.app

### What's Needed for Each Private Repo 📋

## Setup for Private Repos (5 Steps)

### Example: gnosisHermesKabel

#### Step 1: Set GitHub Homepage URL
Go to your private repo settings:
- **Repo**: `github.com/kylemath/gnosisHermesKabel`
- **Settings** → **General** → **Website**
- **Set to**: `https://gnosishermeskabel.netlify.app` (or your Netlify URL)

#### Step 2: Create `catalogue.json` in Repo
Add this file to your repo root:

```json
{
  "id": "gnosisHermesKabel",
  "title": "Gnosis Hermes Kabel",
  "oneLiner": "Exploring the hermetic tradition",
  "kind": "longform",
  "categories": ["writing", "philosophy", "hermetics"],
  "tags": ["gnosis", "philosophy"],
  "status": "published",
  "demoUrl": "https://gnosishermeskabel.netlify.app",
  "screenshot": "screenshot.png"
}
```

**Choose `kind` based on where you want it:**
- `"longform"` → **Writing** tab
- `"page"` → **Apps** tab
- `"project"` → **Projects** tab

#### Step 3: Add `screenshot.png`
- Take a screenshot of your deployed site
- Save as `screenshot.png` in repo root
- Recommended size: 1200x800px

#### Step 4: Deploy Both Files
Make sure your Netlify build includes both files at the root:
- ✅ `https://gnosishermeskabel.netlify.app/catalogue.json`
- ✅ `https://gnosishermeskabel.netlify.app/screenshot.png`

Test accessibility:
```bash
curl https://gnosishermeskabel.netlify.app/catalogue.json
curl -I https://gnosishermeskabel.netlify.app/screenshot.png
```

Both should return 200 OK.

#### Step 5: Wait for Automation (or Run Manually)
The GitHub Action runs daily at 1 AM, or you can trigger manually:
- Go to: `github.com/kylemath/homePage/actions`
- Click: **Update All Content and Deploy**
- Click: **Run workflow**

**That's it!** Your private repo will now appear on your homepage.

---

## How Automation Works

### Daily Automation (Already Set Up! ✅)

```
Every day at 1 AM:
┌─────────────────────────────────────────┐
│ GitHub Action Triggers                  │
│ Environment: GITHUB_TOKEN=***           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Runs: python update_projects.py         │
│ Fetches ALL repos (public + private)    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ For each repo with homepage URL:        │
│ • Fetch catalogue.json from Netlify     │
│ • Build catalogue entry                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Writes: catalogue_data.json             │
│ Commits & Deploys to kylemathewson.com  │
└─────────────────────────────────────────┘
```

### What Gets Fetched from Private Repos?
- ✅ Repo name, description, dates (via GitHub API)
- ✅ Homepage URL (via GitHub API)
- ❌ No code access

### What Gets Fetched from Public Sites?
- ✅ catalogue.json (from Netlify)
- ✅ screenshot.png (from Netlify)
- 🌐 Anyone can access these

---

## Testing Locally (Optional)

To test on your local machine before the automated run:

### 1. Set up token locally:
```bash
# Create token at: https://github.com/settings/tokens
# Scope: repo (Full control of private repositories)

# Add to shell profile
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.zshrc
source ~/.zshrc

# Verify it's set
echo $GITHUB_TOKEN
```

### 2. Run test script:
```bash
cd ~/homePage
source venv/bin/activate
python test_with_token.py
```

Should show:
```
✅ GITHUB_TOKEN found - testing with authentication
📊 Repository Count:
   Public:  XX
   Private: XX
   Total:   XXX

🔐 Private repos with public sites (will be auto-discovered):
   • fungio-manifesto-site
     Homepage: https://fungioergosum.netlify.app
     ✅ catalogue.json found!
        Kind: longform
        Title: Fungio Manifesto Site
```

### 3. Run full update:
```bash
python update_projects.py
```

Check `catalogue_data.json` for your entries!

---

## Quick Reference

### Files You Updated in Homepage Repo ✅
- ✅ `update_projects.py` - Fetches from public sites first
- ✅ `SETUP_GITHUB_TOKEN.md` - Token setup instructions
- ✅ `PRIVATE_REPO_INSTRUCTIONS.md` - Complete guide
- ✅ `AI_PROMPT_FOR_PRIVATE_REPOS.txt` - AI assistant prompt
- ✅ `AUTOMATION_FLOW.md` - Visual flow diagram
- ✅ `FUNGIO_EXAMPLE.md` - Working example
- ✅ `test_with_token.py` - Test script

### Files Needed in Each Private Repo
- `catalogue.json` (metadata)
- `screenshot.png` (image)
- Both deployed to Netlify root

### GitHub Repo Settings
- **Website** field → Netlify URL

### No Manual Updates Needed!
Once configured, everything happens automatically daily at 1 AM.

---

## Troubleshooting

### Private repo not appearing?

**Check 1**: Is homepage URL set in GitHub repo settings?
```bash
# Should return your repo with homepage field
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/kylemath/YOUR-REPO
```

**Check 2**: Is catalogue.json accessible on Netlify?
```bash
curl https://yoursite.netlify.app/catalogue.json
```

**Check 3**: Is screenshot accessible?
```bash
curl -I https://yoursite.netlify.app/screenshot.png
```

**Check 4**: Check GitHub Actions logs
- Go to: github.com/kylemath/homePage/actions
- Click latest run
- Check for errors

### Wrong tab?
- Check `kind` in `catalogue.json`
- Must be: `"longform"`, `"page"`, or `"project"`

### Screenshot not loading?
- Verify URL in browser
- Check CORS settings on Netlify
- Try using relative path: `"screenshot": "screenshot.png"`

---

## Copy/Paste for AI Assistant

When setting up a new private repo, copy this to your AI:

```
Please set up homepage catalogue integration:

1. Create catalogue.json:
{
  "title": "[Project Name]",
  "oneLiner": "[Description]",
  "kind": "page",
  "categories": ["cat1", "cat2"],
  "tags": ["tag1", "tag2"],
  "status": "published",
  "demoUrl": "[Netlify URL]",
  "screenshot": "screenshot.png"
}

2. Create screenshot.png (1200x800px recommended)

3. Ensure both files deploy to Netlify root

4. Verify accessible at:
   - [Netlify URL]/catalogue.json
   - [Netlify URL]/screenshot.png

5. Set GitHub repo "Website" field to: [Netlify URL]
```

---

## Summary

✅ **Automation already set up** - runs daily at 1 AM
✅ **Private repos supported** - via GitHub API + public Netlify sites
✅ **No code exposure** - only public metadata
✅ **Fully automatic** - just configure each repo once

**Per repo setup time:** ~5 minutes
**Result:** Private repo appears on homepage automatically! 🎉

