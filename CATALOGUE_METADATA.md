# Catalogue Metadata Instructions for `gir` Script

Use these steps **in every repo** that should appear in the homepage catalogue.

## 1. Create `catalogue.json`
Generate the file at the repo root with this schema:

```json
{
  "id": "collisionDetectionForcefield",          // optional, defaults to repo name
  "title": "Collision Detection Force Field",
  "oneLiner": "Interactive comparison of discrete vs molecular collision physics.",
  "demoUrl": "https://kylemath.github.io/collisionDetectionForcefield/",  // fallback: repo homepage or GitHub URL
  "screenshot": "./screenshot.png",              // raw URL or committed asset
  "kind": "project",                             // optional: project | longform | page | any future kind
  "categories": ["simulation", "web"],
  "tags": ["physics", "p5.js"],
  "status": "published"
}
```

Notes:
- `kind` overrides topic-based detection. Use `project`, `longform`, `page`, or new kinds when needed.
- `screenshot` can reference the auto-generated PNG that `gir` already captures; raw GitHub URLs also work.
- Fields you omit will be inferred (e.g., `id`, `title`, `demoUrl`).

## 2. Ensure a Screenshot Exists
Commit the screenshot you reference (e.g., `screenshot.png`) so the catalogue preview has a thumbnail.

## 3. Assign GitHub Topics for Hierarchy
Add one or more topics that start with the kind name. Hierarchical paths use dashes:

- `project-science`, `project-kids-robots`
- `longform-essay`, `longform-book-history`
- `page-community`, `page-lab-applab`

The first segment sets the kind (unless `catalogue.json.kind` is set). Remaining segments feed the category path. You can chain more levels as needed.

## 4. Push to GitHub
After `catalogue.json`, screenshot, and topics are in place:

1. Push the repo normally.
2. The `homePage` GitHub Action pulls each repo's metadata, regenerates `catalogue_data.json`, and redeploys the homepage with updated cards.

Running `gir` should automate as much of this as possible (creating `catalogue.json`, capturing `screenshot.png`, prompting for demo URL, etc.).
