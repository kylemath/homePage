# 5-Minute Private Repo Setup Checklist

## ✅ For Each Private Repo with Netlify Site

### 1. Set Homepage URL (30 seconds)
- [ ] Go to GitHub repo → Settings → Website
- [ ] Enter Netlify URL: `https://yoursite.netlify.app`
- [ ] Save

### 2. Create catalogue.json (2 minutes)
```json
{
  "title": "Your Project Name",
  "oneLiner": "One-line description",
  "kind": "longform",
  "screenshot": "screenshot.png",
  "demoUrl": "https://yoursite.netlify.app"
}
```
- [ ] Add to repo root
- [ ] Set `kind`: `"longform"` (Writing), `"page"` (Apps), or `"project"` (Projects)

### 3. Add Screenshot (1 minute)
- [ ] Save as `screenshot.png` in repo root
- [ ] Size: ~1200x800px

### 4. Deploy (1 minute)
- [ ] Commit and push
- [ ] Verify files are accessible:
  - [ ] `https://yoursite.netlify.app/catalogue.json`
  - [ ] `https://yoursite.netlify.app/screenshot.png`

### 5. Wait for Automation
- [ ] Runs daily at 1 AM automatically
- [ ] Or trigger manually: `github.com/kylemath/homePage/actions`

## ✅ Done!
Your private repo will appear on kylemathewson.com automatically.

---

## Quick Test Commands

```bash
# Test catalogue.json
curl https://yoursite.netlify.app/catalogue.json

# Test screenshot
curl -I https://yoursite.netlify.app/screenshot.png

# Both should return 200 OK
```

---

## Tab Selection

| kind | Tab |
|------|-----|
| `"longform"` | Writing |
| `"page"` | Apps |
| `"project"` | Projects |

---

## Example catalogue.json Templates

### For Writing Tab
```json
{
  "title": "My Essay",
  "oneLiner": "An exploration of...",
  "kind": "longform",
  "categories": ["writing", "essay"],
  "screenshot": "screenshot.png"
}
```

### For Apps Tab
```json
{
  "title": "My Tool",
  "oneLiner": "A tool that...",
  "kind": "page",
  "categories": ["tool", "web"],
  "screenshot": "screenshot.png"
}
```

### For Projects Tab
```json
{
  "title": "My Project",
  "oneLiner": "A project about...",
  "kind": "project",
  "categories": ["research", "code"],
  "screenshot": "screenshot.png"
}
```

