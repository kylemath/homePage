#!/usr/bin/env python3
"""Match PDFs in a folder to paper cards and write composite thumbnails.

Each thumbnail is page 1 beside the two largest figures in the PDF.
"""

import json
import re
from pathlib import Path

# Filename fragment -> title fragment. Used when the PDF front matter hides the title.
OVERRIDES = {
    "frontiers in perception science": "pulsed out of awareness",
    "frontiers,tacs": "10-hz cathodal",
    "natbioeng": "large-area mri-compatible epidermal",
    "restingo2": "electrophysiological correlates of hyperoxia",
    "skateboard eeg": "eeg in motion",
    "the moving wave  applications": "the moving wave",
}

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "site_content.json"
OUT_DIR = ROOT / "images" / "papers"


def pdfs_in(folder):
    paths = []
    for path in Path(folder).iterdir():
        if path.suffix.lower() != ".pdf":
            continue
        if "acceptedpreprint" in path.name.lower() or path.name.startswith("*40"):
            continue
        paths.append(path)
    return sorted(paths, key=lambda p: p.name)


def page_title_text(doc):
    text = doc[0].get_text("text") if doc.page_count else ""
    return re.sub(r"\s+", " ", text)[:800].lower()


def score(paper, blob, filename):
    title = re.sub(r"[^a-z0-9 ]+", " ", (paper.get("title") or "").lower())
    words = [w for w in title.split() if len(w) > 3]
    if not words:
        return 0
    hits = sum(1 for w in words if w in blob or w in filename)
    return hits / len(words)


def figure_pixmaps(doc, fitz):
    found = []
    seen = set()
    for page_index in range(doc.page_count):
        page = doc[page_index]
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen:
                continue
            seen.add(xref)
            try:
                pix = fitz.Pixmap(doc, xref)
            except Exception:
                continue
            if pix.width < 120 or pix.height < 80:
                continue
            if pix.n >= 5:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            elif pix.n == 4 and pix.alpha:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            found.append((pix.width * pix.height, pix))
    found.sort(key=lambda item: item[0], reverse=True)
    return [pix for _, pix in found[:2]]


def render_page(page, fitz, max_w):
    scale = max_w / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return pix


def pix_to_image(pix, Image, fitz):
    if pix.n != 3 or pix.alpha:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def compose(doc, fitz, Image, out_path, width=1200, height=780):
    page_pix = render_page(doc[0], fitz, int(width * 0.58))
    page_img = pix_to_image(page_pix, Image, fitz)
    canvas = Image.new("RGB", (width, height), (255, 255, 255))
    page_img.thumbnail((int(width * 0.58), height))
    canvas.paste(page_img, (0, max(0, (height - page_img.height) // 2)))

    figs = figure_pixmaps(doc, fitz)
    gutter = int(width * 0.58) + 8
    fig_w = width - gutter
    fig_h = (height - 8) // 2
    for index in range(2):
        slot = Image.new("RGB", (fig_w, fig_h), (247, 245, 240))
        if index < len(figs):
            fig = pix_to_image(figs[index], Image, fitz)
            fig.thumbnail((fig_w - 8, fig_h - 8))
            slot.paste(fig, ((fig_w - fig.width) // 2, (fig_h - fig.height) // 2))
        y = index * (fig_h + 8)
        canvas.paste(slot, (gutter, y))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "PNG", optimize=True)
    return len(figs)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", default=str(Path.home() / "Downloads" / "MINE"))
    parser.add_argument("--min-score", type=float, default=0.45)
    args = parser.parse_args()

    import fitz
    from PIL import Image

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"No PDF folder at {folder}. Existing images/papers thumbnails were left in place.")
        return

    site = json.loads(CONTENT.read_text())
    papers = site.get("papers") or []
    used = set()
    matched = 0
    for path in pdfs_in(folder):
        doc = fitz.open(path)
        blob = page_title_text(doc) + " " + path.name.lower()
        forced = next((fragment for key, fragment in OVERRIDES.items() if key in path.name.lower()), None)
        best = None
        best_score = 0
        for paper in papers:
            if paper["id"] in used:
                continue
            title = (paper.get("title") or "").lower()
            if forced and forced in title and "correction" not in title and "(vol" not in title:
                best = paper
                best_score = 1
                break
            value = score(paper, blob, path.name.lower())
            if value > best_score:
                best_score = value
                best = paper
        if not best or best_score < args.min_score:
            print(f"SKIP {path.name} best={best_score:.2f} {best['title'][:60] if best else ''}")
            doc.close()
            continue
        out = OUT_DIR / f"{best['id']}.png"
        nfigs = compose(doc, fitz, Image, out)
        doc.close()
        rel = str(out.relative_to(ROOT))
        best["composite"] = rel
        best["pdfPage"] = rel
        used.add(best["id"])
        matched += 1
        print(f"OK {best_score:.2f} figs={nfigs} {path.name} -> {best['title'][:70]}")
    for paper in papers:
        if paper["id"] in used:
            continue
        if str(paper.get("composite") or "").startswith("images/papers/"):
            paper.pop("composite", None)
            if str(paper.get("pdfPage") or "").startswith("images/papers/"):
                paper["pdfPage"] = None
    CONTENT.write_text(json.dumps(site, indent=2) + "\n")
    print(f"Matched {matched} papers")


if __name__ == "__main__":
    main()
