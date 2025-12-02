# Fungio Site - Working Example

## Current Setup ✅

Your **fungio-manifesto-site** is perfectly configured as a private repo with public deployment:

### What's Working:
- **Private GitHub Repo**: `kylemath/fungio-manifesto-site` (not publicly searchable)
- **Public Netlify Site**: https://fungioergosum.netlify.app
- **Public metadata**: https://fungioergosum.netlify.app/catalogue.json
- **Public screenshot**: https://fungioergosum.netlify.app/screenshot.png

### Current catalogue.json:
```json
{
  "id": "fungio-manifesto-site",
  "title": "Fungio Manifesto Site",
  "oneLiner": "A complete manifesto on Life's hidden partnerships",
  "demoUrl": "https://fungioergosum.com/",
  "screenshot": "https://raw.githubusercontent.com/kylemath/fungio-manifesto-site/main/screenshot.png",
  "kind": "longform",
  "categories": ["writing", "symbiosis", "biology"],
  "tags": ["writing", "symbiosis", "biology"],
  "status": "published"
}
```

## How It Will Appear

When you run `update_projects.py`:

1. ✅ Script fetches your private repo list via GitHub API
2. ✅ Finds `homepage` URL pointing to Netlify
3. ✅ Fetches `catalogue.json` from public Netlify site
4. ✅ Uses `kind: "longform"` → **Writing tab**
5. ✅ Uses existing screenshot URL

**Result**: The project appears in your **Writing** tab with all metadata, no GitHub access needed!

## Optional Improvements

### Make Screenshot Self-Hosted

Your current screenshot URL points to GitHub:
```json
"screenshot": "https://raw.githubusercontent.com/kylemath/fungio-manifesto-site/main/screenshot.png"
```

If the repo is private, this won't work publicly. Consider changing to:
```json
"screenshot": "screenshot.png"
```

This will resolve to: `https://fungioergosum.netlify.app/screenshot.png` (which already exists!)

### Setup Checklist for Future Private Repos

For your next private repo (like gnosisHermesKabel):

1. ✅ Deploy to Netlify/Vercel
2. ✅ Set GitHub repo "Website" field to deployment URL
3. ✅ Add `catalogue.json` to repo (gets deployed)
4. ✅ Add `screenshot.png` to repo (gets deployed)
5. ✅ Verify both accessible on public site
6. ✅ Run `update_projects.py`

## Testing

Test the full flow:
```bash
cd /Users/kylemathewson/homePage
source venv/bin/activate
python update_projects.py
```

Check `catalogue_data.json` for your fungio entry with `kind: "longform"`.

Deploy and verify it appears in the Writing tab!

## Notes

- The updated script prioritizes public deployment URLs over GitHub
- Works seamlessly with both public and private repos
- Existing public repos continue to work unchanged
- No GitHub token needed for private repo metadata (only for repo list)

