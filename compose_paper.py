#!/usr/bin/env python3
"""Build a paper-card image: PDF page 1 beside two figures.

Writes images/papers/<id>.png and can point a site_content.json paper entry
at that file plus the two figure paths.

    python3 compose_paper.py PAPER_ID paper.pdf fig1.png fig2.png

Requires PyMuPDF. Install it in a virtual environment:

    python3 -m venv .venv && . .venv/bin/activate && pip install pymupdf
"""

import argparse
import json
from pathlib import Path


def compose_images(page_image, fig_a, fig_b, out_path, width=1200, height=780):
    """Place a page image beside two figures, matching the paper-card thumbnail."""
    from PIL import Image

    def opened(src):
        if hasattr(src, "read"):
            img = Image.open(src)
        else:
            img = Image.open(src)
        return img.convert("RGB")

    page_img = opened(page_image)
    canvas = Image.new("RGB", (width, height), (255, 255, 255))
    page_img.thumbnail((int(width * 0.58), height))
    canvas.paste(page_img, (0, max(0, (height - page_img.height) // 2)))

    gutter = int(width * 0.58) + 8
    fig_w = width - gutter
    fig_h = (height - 8) // 2
    for index, src in enumerate((fig_a, fig_b)):
        slot = Image.new("RGB", (fig_w, fig_h), (247, 245, 240))
        if src:
            fig = opened(src)
            fig.thumbnail((fig_w - 8, fig_h - 8))
            slot.paste(fig, ((fig_w - fig.width) // 2, (fig_h - fig.height) // 2))
        canvas.paste(slot, (gutter, index * (fig_h + 8)))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "PNG", optimize=True)
    return out_path


def compose(pdf_path, fig_a, fig_b, out_path, width=1200, height=780):
    import fitz
    from PIL import Image

    doc = fitz.open(pdf_path)
    page = doc[0]
    scale = (width * 0.58) / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    page_img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    canvas = Image.new("RGB", (width, height), (255, 255, 255))
    page_img.thumbnail((int(width * 0.58), height))
    canvas.paste(page_img, (0, 0))

    gutter = int(width * 0.58) + 8
    fig_w = width - gutter
    fig_h = (height - 8) // 2
    for index, src in enumerate((fig_a, fig_b)):
        fig = Image.open(src).convert("RGB")
        fig.thumbnail((fig_w, fig_h))
        y = index * (fig_h + 8)
        canvas.paste(fig, (gutter, y))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "PNG")
    return out_path


def attach(content_path, paper_id, image_path, figures):
    data = json.loads(Path(content_path).read_text())
    for paper in data.get("papers", []):
        if paper.get("id") == paper_id:
            paper["pdfPage"] = str(image_path)
            paper["figures"] = figures
            paper["composite"] = str(image_path)
            break
    else:
        raise SystemExit(f"No paper with id {paper_id} in {content_path}")
    Path(content_path).write_text(json.dumps(data, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper_id")
    parser.add_argument("pdf")
    parser.add_argument("figure_a")
    parser.add_argument("figure_b")
    parser.add_argument("--content", default="site_content.json")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    out = Path(args.out or f"images/papers/{args.paper_id}.png")
    compose(args.pdf, args.figure_a, args.figure_b, out)
    attach(args.content, args.paper_id, out, [args.figure_a, args.figure_b])
    print(f"Wrote {out} and updated {args.paper_id}")


if __name__ == "__main__":
    main()
