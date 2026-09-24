#!/usr/bin/env python3
"""Serve the homepage and save category edits from sorter.html.

    python3 serve.py
"""

import cgi
import json
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from compose_paper import compose_images
from push_repo_screenshots import push_files

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "site_content.json"
PAPER_DIR = ROOT / "images" / "papers"


def _save_png(raw, path):
    import io

    from PIL import Image

    image = Image.open(io.BytesIO(raw)).convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG", optimize=True)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path == "/save-screenshots":
            self.save_screenshots()
            return
        if path == "/save-paper-shots":
            self.save_paper_shots()
            return
        if path != "/save-categories":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            categories = payload.get("categories")
            if not isinstance(categories, list):
                raise ValueError("categories must be a list")
            site = json.loads(CONTENT.read_text(encoding="utf-8"))
            cleaned = []
            seen = set()
            for col in categories:
                if not isinstance(col, dict):
                    continue
                names = []
                for name in col.get("names") or []:
                    if isinstance(name, str) and name and name not in seen:
                        seen.add(name)
                        names.append(name)
                cleaned.append({
                    "id": str(col.get("id") or "untitled"),
                    "title": str(col.get("title") or "Untitled").strip() or "Untitled",
                    "description": str(col.get("description") or ""),
                    "color": str(col.get("color") or "#9aa0aa"),
                    "names": names,
                })
            site["categories"] = cleaned
            site["colsPerRow"] = str(payload.get("colsPerRow") or site.get("colsPerRow") or "auto")
            site["categoriesSaved"] = datetime.now(timezone.utc).isoformat()
            CONTENT.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
            body = json.dumps({"status": "ok", "group_count": len(cleaned)}).encode()
            self.send_response(200)
        except Exception as exc:
            body = json.dumps({"status": "error", "message": str(exc)}).encode()
            self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def save_screenshots(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > 40 * 1024 * 1024:
            self._json(400, {"status": "error", "message": "Upload is larger than 40 MB."})
            return
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
                "CONTENT_LENGTH": str(length),
            },
        )
        files = {}
        for key in form.keys():
            field = form[key]
            if isinstance(field, list):
                field = field[0]
            if getattr(field, "file", None) is None:
                continue
            files[key] = field.file.read()
        if not files:
            self._json(400, {"status": "error", "message": "No PNG files were uploaded."})
            return
        try:
            done = push_files(files)
        except Exception as exc:
            self._json(400, {"status": "error", "message": str(exc)})
            return
        self._json(200, {"status": "ok", "updated": done})

    def save_paper_shots(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > 80 * 1024 * 1024:
            self._json(400, {"status": "error", "message": "Upload is larger than 80 MB."})
            return
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
                "CONTENT_LENGTH": str(length),
            },
        )
        slots = {}
        for key in form.keys():
            if "::" not in key:
                continue
            paper_id, slot = key.split("::", 1)
            if slot not in ("page", "fig1", "fig2"):
                continue
            field = form[key]
            if isinstance(field, list):
                field = field[0]
            if getattr(field, "file", None) is None:
                continue
            slots.setdefault(paper_id, {})[slot] = field.file.read()
        ready = {pid: parts for pid, parts in slots.items() if {"page", "fig1", "fig2"} <= parts.keys()}
        if not ready:
            self._json(400, {"status": "error", "message": "Each paper needs a page image and two figures."})
            return
        try:
            site = json.loads(CONTENT.read_text(encoding="utf-8"))
            papers = {paper.get("id"): paper for paper in site.get("papers") or []}
            updated = []
            for paper_id, parts in ready.items():
                paper = papers.get(paper_id)
                if not paper or "/" in paper_id or ".." in paper_id:
                    raise ValueError(f"Unknown paper {paper_id}")
                page_path = PAPER_DIR / f"{paper_id}-page.png"
                fig1_path = PAPER_DIR / f"{paper_id}-fig1.png"
                fig2_path = PAPER_DIR / f"{paper_id}-fig2.png"
                composite_path = PAPER_DIR / f"{paper_id}.png"
                PAPER_DIR.mkdir(parents=True, exist_ok=True)
                for raw, path in ((parts["page"], page_path), (parts["fig1"], fig1_path), (parts["fig2"], fig2_path)):
                    _save_png(raw, path)
                compose_images(page_path, fig1_path, fig2_path, composite_path)
                rel = lambda path: str(path.relative_to(ROOT))
                paper["pdfPage"] = rel(page_path)
                paper["figures"] = [rel(fig1_path), rel(fig2_path)]
                paper["composite"] = rel(composite_path)
                updated.append(paper_id)
            CONTENT.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
        except Exception as exc:
            self._json(400, {"status": "error", "message": str(exc)})
            return
        self._json(200, {"status": "ok", "updated": updated})

    def _json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Homepage at http://127.0.0.1:8000")
    print("Category sorter at http://127.0.0.1:8000/sorter.html")
    print("Screenshot upload at http://127.0.0.1:8000/screenshots.html")
    print("Paper images at http://127.0.0.1:8000/paper-shots.html")
    server.serve_forever()
