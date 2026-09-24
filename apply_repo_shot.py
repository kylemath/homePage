#!/usr/bin/env python3
"""Point one catalogue card at a local screenshot or logo.

Safe for several agents at once: catalogue_data.json is updated under an
exclusive lock, and only the named item is changed.

Usage:
  .venv/bin/python apply_repo_shot.py ITEM_ID images/repos/ITEM_ID.png
  .venv/bin/python apply_repo_shot.py ITEM_ID images/repos/ITEM_ID.svg --kind logo
"""

import argparse
import fcntl
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOGUE = ROOT / "catalogue_data.json"


def validate(path: Path, kind: str) -> None:
    if not path.is_file():
        sys.exit(f"missing file: {path}")
    raw = path.read_bytes()
    head = raw[:240].lstrip().lower()
    if head.startswith(b"<!doctype") or head.startswith(b"<html") or b"<html" in head:
        sys.exit(f"refusing HTML error page: {path}")
    if path.suffix.lower() == ".svg" or head.startswith(b"<svg") or head.startswith(b"<?xml"):
        if b"<svg" not in raw[:2000].lower():
            sys.exit(f"not an svg: {path}")
        if len(raw) < 40:
            sys.exit(f"svg too small: {path}")
        return
    try:
        from PIL import Image
    except ImportError:
        if len(raw) < 80:
            sys.exit(f"image too small: {path}")
        return
    try:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            w, h = im.size
    except Exception as exc:
        sys.exit(f"not a readable image ({exc}): {path}")
    floor = 16 if kind == "logo" else 48
    if w < floor or h < floor:
        sys.exit(f"image too small ({w}x{h}): {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("item_id")
    parser.add_argument("image")
    parser.add_argument("--kind", choices=("screenshot", "logo"), default="screenshot")
    args = parser.parse_args()

    image = Path(args.image)
    if not image.is_absolute():
        image = ROOT / image
    validate(image, args.kind)
    rel = image.relative_to(ROOT).as_posix()

    with CATALOGUE.open("r+", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        data = json.load(fh)
        match = None
        for item in data.get("items", []):
            if item.get("id") == args.item_id:
                match = item
                break
        if match is None:
            sys.exit(f"id not in catalogue: {args.item_id}")
        if args.kind == "logo":
            match["logo"] = rel
            match["screenshot"] = ""
        else:
            match["screenshot"] = rel
        fh.seek(0)
        json.dump(data, fh, indent=2)
        fh.write("\n")
        fh.truncate()
        fcntl.flock(fh, fcntl.LOCK_UN)
    print(f"updated {args.item_id} {args.kind} -> {rel}")


if __name__ == "__main__":
    main()
