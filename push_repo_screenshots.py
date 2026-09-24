#!/usr/bin/env python3
"""Commit screenshot.png into each project repo and point the catalogue at it.

Other sites read screenshot.png from the repo (or from its homepage). Images
dropped on screenshots.html are sent here, then published with the GitHub
contents API. Papers stay in images/papers/ and are not uploaded.

Requires GITHUB_TOKEN with permission to write the target repos. The token
built into GitHub Actions for this homepage cannot push to other repos.

    GITHUB_TOKEN=... .venv/bin/python push_repo_screenshots.py id path.png [id path.png ...]
"""

import base64
import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
CATALOGUE = ROOT / "catalogue_data.json"
OWNER = "kylemath"
PNG = b"\x89PNG\r\n\x1a\n"


def repo_name(item):
    url = item.get("githubUrl") or ""
    prefix = f"https://github.com/{OWNER}/"
    if not url.startswith(prefix):
        raise ValueError(f"{item.get('id')} has no {OWNER} repo URL")
    return url[len(prefix):].strip("/")


def raw_screenshot_url(name, branch):
    return f"https://raw.githubusercontent.com/{OWNER}/{name}/{branch}/screenshot.png"


def push_png(token, name, png_bytes):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    repo = requests.get(f"https://api.github.com/repos/{OWNER}/{name}", headers=headers, timeout=30)
    if repo.status_code != 200:
        raise RuntimeError(f"{name}: cannot read repo ({repo.status_code}) {repo.text[:180]}")
    branch = repo.json().get("default_branch") or "main"
    existing = requests.get(
        f"https://api.github.com/repos/{OWNER}/{name}/contents/screenshot.png",
        headers=headers,
        params={"ref": branch},
        timeout=30,
    )
    body = {
        "message": "Add screenshot.png for homepage cards",
        "content": base64.b64encode(png_bytes).decode("ascii"),
        "branch": branch,
    }
    if existing.status_code == 200:
        body["sha"] = existing.json().get("sha")
    put = requests.put(
        f"https://api.github.com/repos/{OWNER}/{name}/contents/screenshot.png",
        headers=headers,
        json=body,
        timeout=60,
    )
    if put.status_code not in (200, 201):
        raise RuntimeError(f"{name}: upload failed ({put.status_code}) {put.text[:180]}")
    return raw_screenshot_url(name, branch)


def update_catalogue(updates):
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    by_id = {item.get("id"): item for item in data.get("items", [])}
    for item_id, url in updates.items():
        item = by_id.get(item_id)
        if item is None:
            raise KeyError(item_id)
        item["screenshot"] = url
    CATALOGUE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def push_files(files):
    """files: {catalogue id: png bytes}. Returns {id: raw url}."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Set GITHUB_TOKEN to a token that can write these repos.")
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    by_id = {item.get("id"): item for item in data.get("items", [])}
    done = {}
    for item_id, png_bytes in files.items():
        if not png_bytes.startswith(PNG):
            raise ValueError(f"{item_id} is not a PNG")
        item = by_id.get(item_id)
        if item is None:
            raise KeyError(f"{item_id} is not in the catalogue")
        name = repo_name(item)
        done[item_id] = push_png(token, name, png_bytes)
        print(f"pushed {name} -> {done[item_id]}")
    update_catalogue(done)
    return done


def main(argv):
    if len(argv) < 2 or len(argv) % 2 != 0:
        raise SystemExit("usage: push_repo_screenshots.py ID path.png [ID path.png ...]")
    files = {}
    for item_id, path in zip(argv[::2], argv[1::2]):
        raw = Path(path).read_bytes()
        files[item_id] = raw
    push_files(files)


if __name__ == "__main__":
    main(sys.argv[1:])
