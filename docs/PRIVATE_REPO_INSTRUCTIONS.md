# Instructions for Private Repos with Public Deployments

Use these instructions when you have a **private GitHub repo** that deploys to a **public site** (e.g., Netlify, Vercel, GitHub Pages from a private repo).

## Setup Steps

### 1. Ensure Homepage URL is Set in GitHub

Your GitHub repo must have the **homepage URL** field set to your public deployment URL:

- Go to your repo settings on GitHub
- Set the "Website" field to your deployment URL (e.g., `https://yoursite.netlify.app`)
- This makes the URL available via the GitHub API

### 2. Create `catalogue.json` in Your Repo

Add a `catalogue.json` file to your repo root (or in a directory that gets deployed):

```json
{
  "id": "gnosisHermesKabel",
  "title": "Gnosis Hermes Kabel",
  "oneLiner": "A one-line description of your project",
  "kind": "page",
  "categories": ["writing", "philosophy"],
  "tags": ["gnosis", "hermetics"],
  "status": "published",
  "demoUrl": "https://yoursite.netlify.app",
  "screenshot": "screenshot.png"
}
```

**Important fields:**
- `kind`: Set to `"longform"` (Writing tab), `"page"` (Apps tab), or `"project"` (Projects tab)
- `screenshot`: Relative path to your screenshot file (will be resolved relative to your homepage URL)
- `demoUrl`: Your public site URL

### 3. Add a Screenshot

Create a screenshot of your deployed site:
- Take a screenshot (recommended size: 1200x800px or similar)
- Save it as `screenshot.png` in your repo
- Make sure it gets deployed to the same location as `catalogue.json`

### 4. Deploy Your Files

Ensure both files are accessible on your public site:
- `https://yoursite.netlify.app/catalogue.json`
- `https://yoursite.netlify.app/screenshot.png`

The script will check these locations:
1. `https://yoursite.netlify.app/catalogue.json` ✅ (most common)
2. `https://yoursite.netlify.app/assets/catalogue.json`
3. `https://yoursite.netlify.app/public/catalogue.json`
4. `https://yoursite.netlify.app/.well-known/catalogue.json`

## Testing

After deploying, verify the files are accessible:

```bash
# Test catalogue.json
curl https://yoursite.netlify.app/catalogue.json

# Test screenshot
curl -I https://yoursite.netlify.app/screenshot.png
```

Both should return 200 OK.

## Example Repos

### Private Repo → Netlify Deployment

**Repo Structure:**
```
my-private-repo/
├── catalogue.json          # ← Add this
├── screenshot.png          # ← Add this
├── index.html
└── ... (your other files)
```

**catalogue.json:**
```json
{
  "title": "My Private Project",
  "oneLiner": "Publicly deployed site from private repo",
  "kind": "page",
  "demoUrl": "https://my-project.netlify.app",
  "screenshot": "screenshot.png",
  "categories": ["tool", "web"],
  "tags": ["netlify", "private"],
  "status": "published"
}
```

**GitHub Settings:**
- Homepage: `https://my-project.netlify.app`
- Visibility: Private ✅

## How It Works

1. The `update_projects.py` script fetches all your repos (public and private) via GitHub API
2. For each repo with a `homepage` URL, it tries to fetch `catalogue.json` from that public URL first
3. If the repo is public, it falls back to GitHub raw URLs
4. Screenshots are resolved the same way (public URL first, then GitHub)

## AI Assistant Instructions

When working in a private repo that needs catalogue integration, copy/paste this to your AI:

---

**Please set up this private repo for the homepage catalogue:**

1. Create a `catalogue.json` file in the repo root with this structure:
```json
{
  "title": "[Project Name]",
  "oneLiner": "[One-line description]",
  "kind": "[page/longform/project]",
  "categories": ["category1", "category2"],
  "tags": ["tag1", "tag2"],
  "status": "published",
  "demoUrl": "[Your deployed site URL]",
  "screenshot": "screenshot.png"
}
```

2. Add a `screenshot.png` file (take a screenshot of the deployed site)

3. Ensure both files are deployed to the public site and accessible at:
   - `[Your Site URL]/catalogue.json`
   - `[Your Site URL]/screenshot.png`

4. Verify the GitHub repo homepage field is set to: `[Your Site URL]`

---

## Troubleshooting

**Problem:** Catalogue entry not appearing after running `update_projects.py`

**Solutions:**
1. Verify homepage URL is set in GitHub repo settings
2. Check that `catalogue.json` is accessible: `curl https://yoursite.netlify.app/catalogue.json`
3. Check that screenshot is accessible: `curl -I https://yoursite.netlify.app/screenshot.png`
4. Run the script with `GITHUB_TOKEN` set to access private repo metadata
5. Check the console output for any fetch errors

**Problem:** Screenshot not displaying

**Solutions:**
1. Verify the screenshot URL in your browser
2. Check the `screenshot` field in `catalogue.json` matches the deployed filename
3. Ensure the image is actually deployed (check your Netlify/Vercel deploy logs)

**Problem:** Wrong tab (Projects instead of Writing/Apps)

**Solution:**
- Check the `kind` field in `catalogue.json`
- Must be exactly: `"longform"` (Writing), `"page"` (Apps), or `"project"` (Projects)

