# Automation Scripts - Fixed for Tabbed Layout

## ✅ What Was Fixed

### 1. `update_projects.py`
**Issues:**
- Wiped `catalogue_data.json` when GitHub API failed (rate limiting)
- Used deprecated `datetime.utcnow()`

**Fixes:**
- Now refuses to write empty data (prevents data loss)
- Shows helpful error message about GITHUB_TOKEN
- Updated to use `datetime.now(timezone.utc)`

### 2. `update_publications.py`
**Issues:**
- Regex pattern couldn't find publications section (didn't account for `<p>` tag between `<h2>` and `<ol>`)

**Fixes:**
- Updated pattern to allow optional paragraph between header and list
- Now matches: `<h2>...<p>...</p><ol>` or `<h2>...<ol>`

### 3. `catalogue_data.json`
**Status:** ✅ Restored from git (75 items)

---

## 🚀 How to Use Automations

### Prerequisites

**Create GitHub Personal Access Token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo` and `read:user`
4. Copy the token
5. Set as environment variable:
   ```bash
   export GITHUB_TOKEN='your_token_here'
   ```

### Running the Scripts

```bash
# Make sure you're in the venv
cd /Users/kylemathewson/homePage
source venv/bin/activate

# Set your GitHub token first!
export GITHUB_TOKEN='your_token_here'

# Run the automation scripts
python update_projects.py               # Updates catalogue_data.json
python update_contributor_projects.py   # Updates contributor list
python update_publications.py           # Updates publications

# Deactivate when done
deactivate
```

### What Each Script Does

| Script | Updates | Output |
|--------|---------|--------|
| `update_projects.py` | Project catalogue cards | `catalogue_data.json` |
| `update_contributor_projects.py` | Contributor projects list | `index.html` |
| `update_publications.py` | Publications list | `index.html` |

---

## 📋 Compatibility with Tabbed Layout

All scripts are now compatible with the new tabbed structure:

- ✅ **Projects Tab**: Catalogue cards load from `catalogue_data.json`
- ✅ **Apps Tab**: Catalogue cards for "page" kind items
- ✅ **Writing Tab**: Catalogue cards for "longform" kind items
- ✅ **Publications Tab**: Publications list updated by script
- ✅ **Recent Projects**: Traditional list updated by script

---

## 🔒 Safety Features

### `update_projects.py`
- **Won't overwrite data** if GitHub API returns 0 repos
- Shows warning about GITHUB_TOKEN if needed

### `update_publications.py`
- Only updates if pattern matches
- Won't corrupt HTML if section not found

---

## 🐛 Troubleshooting

### "0 repositories found"
→ Set `GITHUB_TOKEN` environment variable (see Prerequisites)

### "No publications section found"
→ Check that `index.html` has `<h2 id="publications">Recent Publications</h2>`

### "catalogue_data.json is empty"
→ Restore from git: `git checkout HEAD -- catalogue_data.json`

### Scripts don't update HTML
→ Make sure you're editing `index.html` not a backup file

---

## 📝 Notes

- The automation scripts are designed to work with GitHub Actions (see `.github/workflows/`)
- Local runs are useful for testing before pushing
- Always commit `catalogue_data.json` changes to preserve data

