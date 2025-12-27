# Private Repos Documentation Index

## 🚀 Quick Start
**Start here:** [`QUICK_CHECKLIST.md`](QUICK_CHECKLIST.md) - 5-minute setup per repo

## 📚 Documentation

### Setup Guides
1. **[FINAL_SETUP_SUMMARY.md](FINAL_SETUP_SUMMARY.md)** - Complete overview and setup
2. **[QUICK_CHECKLIST.md](QUICK_CHECKLIST.md)** - Fast checklist for each repo
3. **[SETUP_GITHUB_TOKEN.md](SETUP_GITHUB_TOKEN.md)** - Token setup for local testing (optional)

### Reference Docs
4. **[AUTOMATION_FLOW.md](AUTOMATION_FLOW.md)** - Visual flow diagram showing how it works
5. **[PRIVATE_REPO_INSTRUCTIONS.md](PRIVATE_REPO_INSTRUCTIONS.md)** - Detailed technical docs
6. **[FUNGIO_EXAMPLE.md](FUNGIO_EXAMPLE.md)** - Real working example

### Tools
7. **[AI_PROMPT_FOR_PRIVATE_REPOS.txt](AI_PROMPT_FOR_PRIVATE_REPOS.txt)** - Copy/paste for AI assistants
8. **[test_with_token.py](test_with_token.py)** - Test script for local development

## 🎯 What This Solves

You have **private GitHub repos** that deploy to **public Netlify sites**. You want them to appear on your homepage catalogue automatically.

### The Solution
- ✅ Keep repos private (code stays hidden)
- ✅ Public sites host metadata (`catalogue.json`, `screenshot.png`)
- ✅ Automation fetches from public sites daily
- ✅ No manual homepage updates needed

## ⚡ Quick Setup (Per Repo)

1. **GitHub**: Set "Website" field to Netlify URL
2. **Repo**: Add `catalogue.json` and `screenshot.png`
3. **Deploy**: Push to Netlify
4. **Wait**: Runs daily at 1 AM (or trigger manually)

**Time:** ~5 minutes per repo

## 📋 Current Status

### ✅ Already Working
- [x] GitHub Actions configured with GITHUB_TOKEN
- [x] update_projects.py updated to fetch from public sites
- [x] Runs daily at 1 AM automatically
- [x] Example working: fungioergosum.netlify.app

### 📦 Ready to Add
- [ ] gnosisHermesKabel (follow QUICK_CHECKLIST.md)
- [ ] Any other private repos

## 🔍 How It Works

```
Private Repo (hidden code)
    ↓
    Deploys to
    ↓
Public Netlify Site (visible)
    ├── catalogue.json (metadata)
    └── screenshot.png (image)
    ↓
    Fetched by
    ↓
GitHub Actions (daily at 1 AM)
    ├── Uses GITHUB_TOKEN to list repos
    ├── Finds homepage URLs
    └── Fetches from public sites
    ↓
    Generates
    ↓
catalogue_data.json
    ↓
    Powers
    ↓
Homepage Tabs
    ├── Writing (kind: "longform")
    ├── Apps (kind: "page")
    └── Projects (kind: "project")
```

## 🛠️ Key Files

### In Homepage Repo (homePage)
- `update_projects.py` - Updated fetching logic
- `catalogue_data.json` - Generated catalogue (don't edit manually)
- `.github/workflows/update-all-and-deploy.yml` - Automation (already configured)

### In Each Private Repo
- `catalogue.json` - Metadata (you create)
- `screenshot.png` - Image (you create)
- GitHub Settings → Website → Your Netlify URL (you set)

## 💡 Examples

### Real Working Example
**Repo:** kylemath/fungio-manifesto-site (private)
**Site:** https://fungioergosum.netlify.app
**Files:**
- ✅ https://fungioergosum.netlify.app/catalogue.json
- ✅ https://fungioergosum.netlify.app/screenshot.png
**Result:** Appears in **Writing** tab automatically

### Your Next Repo (gnosisHermesKabel)
**Setup:** Follow [QUICK_CHECKLIST.md](QUICK_CHECKLIST.md)
**Time:** 5 minutes
**Result:** Appears in chosen tab automatically

## 🔧 Testing

### Local Testing (Optional)
```bash
# Set token (see SETUP_GITHUB_TOKEN.md)
export GITHUB_TOKEN="ghp_your_token"

# Test access
cd ~/homePage
source venv/bin/activate
python test_with_token.py

# Run full update
python update_projects.py
```

### Testing Without Token
Automation works via GitHub Actions (token already configured).
Local token only needed if you want to test before pushing.

## ❓ Troubleshooting

See [FINAL_SETUP_SUMMARY.md](FINAL_SETUP_SUMMARY.md#troubleshooting) for:
- Private repo not appearing
- Wrong tab
- Screenshot not loading
- GitHub Actions errors

## 📞 Next Steps

1. **Read:** [QUICK_CHECKLIST.md](QUICK_CHECKLIST.md)
2. **Setup:** First private repo (5 minutes)
3. **Test:** Trigger GitHub Action or wait for 1 AM
4. **Verify:** Check kylemathewson.com for new entry
5. **Repeat:** For each additional private repo

---

## Summary

🎉 **You're all set!** The automation is configured and ready. Just follow the quick checklist for each private repo you want to add.

**Questions?** Check the relevant doc from the list above.

