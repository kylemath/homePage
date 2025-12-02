# Complete Automation Flow for Private Repos

## Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. LOCAL OR GITHUB ACTION                                       │
│    Run: python update_projects.py                               │
│    Environment: GITHUB_TOKEN=ghp_xxxxx                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. FETCH ALL REPOS (GitHub API)                                 │
│    GET https://api.github.com/users/kylemath/repos              │
│    Headers: Authorization: token ghp_xxxxx                      │
│                                                                  │
│    Returns:                                                      │
│    ├─ 🔓 Public Repos (everyone can see)                        │
│    └─ 🔐 Private Repos (only with token)                        │
│                                                                  │
│    For each repo, we get:                                       │
│    • name: "fungio-manifesto-site"                              │
│    • private: true                                              │
│    • homepage: "https://fungioergosum.netlify.app" ← KEY!      │
│    • description: "..."                                         │
│    • created_at, updated_at, etc.                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. FOR EACH REPO WITH HOMEPAGE URL                              │
│    Private Repo: fungio-manifesto-site                          │
│    Homepage: https://fungioergosum.netlify.app                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. FETCH FROM PUBLIC NETLIFY SITE (No auth needed!)             │
│                                                                  │
│    Try in order:                                                │
│    ✅ GET https://fungioergosum.netlify.app/catalogue.json      │
│    ❌ GET https://fungioergosum.netlify.app/assets/catalogue... │
│    ❌ GET https://fungioergosum.netlify.app/public/catalogue... │
│                                                                  │
│    ✅ Found! Returns:                                           │
│    {                                                            │
│      "kind": "longform",                                        │
│      "title": "Fungio Manifesto Site",                          │
│      "screenshot": "screenshot.png",                            │
│      ...                                                        │
│    }                                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. RESOLVE SCREENSHOT URL                                       │
│    screenshot: "screenshot.png" (relative)                      │
│    + homepage: "https://fungioergosum.netlify.app"             │
│    = https://fungioergosum.netlify.app/screenshot.png          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. BUILD CATALOGUE ENTRY                                        │
│    {                                                            │
│      "id": "fungio-manifesto-site",                             │
│      "kind": "longform",                    ← Goes to Writing   │
│      "title": "Fungio Manifesto Site",                          │
│      "screenshot": "https://fungioergosum.netlify.app/scree...",│
│      "demoUrl": "https://fungioergosum.netlify.app",            │
│      "githubUrl": "https://github.com/kylemath/fungio-manif...",│
│      ...                                                        │
│    }                                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. WRITE TO catalogue_data.json                                 │
│    {                                                            │
│      "generatedAt": "2025-12-02T...",                           │
│      "items": [                                                 │
│        { ... fungio entry ... },                                │
│        { ... other repos ... }                                  │
│      ]                                                          │
│    }                                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. DEPLOY TO GITHUB PAGES                                       │
│    index.html loads catalogue_data.json                         │
│    Filters by kind: "longform" → Writing tab                    │
│    Displays card with screenshot from Netlify                   │
└─────────────────────────────────────────────────────────────────┘
```

## Key Points

### 🔐 Private Repo Access
- Script uses GITHUB_TOKEN to **list** private repos
- Only gets metadata: name, homepage, description
- **Never accesses private code**

### 🌐 Public Site Access
- Fetches `catalogue.json` from **public Netlify URL**
- No authentication needed
- Anyone can access this file

### 🔄 Complete Automation
Once GITHUB_TOKEN is set:
1. ✅ Script automatically finds ALL repos (public + private)
2. ✅ Checks each for homepage URL
3. ✅ Fetches metadata from public sites
4. ✅ Generates catalogue_data.json
5. ✅ Deploys to homepage

## Setup Checklist

### One-Time Setup (Homepage Repo)
- [ ] Create GitHub token with `repo` scope
- [ ] Set `GITHUB_TOKEN` environment variable
- [ ] Add to GitHub Actions secrets (for automation)

### Per Private Repo Setup
- [ ] Set GitHub repo "Website" field to Netlify URL
- [ ] Add `catalogue.json` to repo
- [ ] Add `screenshot.png` to repo
- [ ] Deploy both to Netlify
- [ ] Verify accessible:
  - `curl https://yoursite.netlify.app/catalogue.json`
  - `curl -I https://yoursite.netlify.app/screenshot.png`

### Run Automation
```bash
export GITHUB_TOKEN="ghp_xxxxx"  # If not in profile
cd ~/homePage
source venv/bin/activate
python update_projects.py
```

## Example: Adding a New Private Repo

1. **Create private repo** `my-secret-project`
2. **Build and deploy** to Netlify: `my-secret-project.netlify.app`
3. **Set GitHub homepage**: Add `my-secret-project.netlify.app` to repo settings
4. **Add catalogue.json** to repo:
   ```json
   {
     "title": "My Secret Project",
     "kind": "page",
     "screenshot": "screenshot.png"
   }
   ```
5. **Add screenshot.png** to repo
6. **Deploy to Netlify**
7. **Wait for GitHub Action** (or run manually)
8. **Done!** Appears in Apps tab

No manual updates to homepage repo needed!

