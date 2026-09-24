#!/usr/bin/env python3
"""Point paper cards at thumbnail files already saved in this repo.

Papers, news, and other items that are not GitHub repos do not use
screenshot.png. Their card images live under images/papers/<id>.png and are
kept here when the site is rebuilt. This script only attaches a file that
already exists. It does not download PDFs and it does not remove thumbnails.

    python3 link_paper_thumbnails.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "site_content.json"
PAPERS = ROOT / "images" / "papers"


def main() -> None:
    site = json.loads(CONTENT.read_text(encoding="utf-8"))
    linked = 0
    for paper in site.get("papers") or []:
        paper_id = paper.get("id")
        if not paper_id:
            continue
        image = PAPERS / f"{paper_id}.png"
        if not image.is_file():
            continue
        rel = image.relative_to(ROOT).as_posix()
        if paper.get("pdfPage") == rel and paper.get("composite") == rel:
            continue
        if not paper.get("pdfPage"):
            paper["pdfPage"] = rel
        if not paper.get("composite"):
            paper["composite"] = rel
        linked += 1
        print(f"linked {paper_id} -> {rel}")
    if linked:
        CONTENT.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
    print(f"Attached {linked} paper thumbnails")


if __name__ == "__main__":
    main()
