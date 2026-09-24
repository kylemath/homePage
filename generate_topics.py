#!/usr/bin/env python3
"""Write one static HTML page per site category into topics/."""

import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOPICS = ROOT / "topics"
SECTIONS = ("links", "teaching", "experience", "stages", "papers", "news")
SKIP_TEXT = {"id", "title", "color", "description", "names"}

THEME_HEAD = """
    <script>
    (function(){try{var s=localStorage.getItem("theme");var t=s==="light"||s==="dark"?s:(matchMedia("(prefers-color-scheme: light)").matches?"light":"dark");document.documentElement.setAttribute("data-theme",t)}catch(e){}})();
    </script>
    <link rel="stylesheet" href="../theme.css">
"""

PAGE_CSS = """
        :root {
            --bg:#0a0a0b;
            --bg-grad: radial-gradient(1100px 560px at 72% -12%, #16161b 0%, #0a0a0b 62%);
            --surface:#151518; --surface-2:#1c1c20; --surface-3:#26262c;
            --border:#2a2a31; --border-strong:#3b3b44;
            --text:#f5f5f6; --text-dim:#b6b6bf; --text-faint:#7c7c87;
            --accent:#6ea8fe; --radius:12px;
            --shadow:0 10px 32px rgba(0,0,0,.5);
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
            background: var(--bg); background-image: var(--bg-grad); background-attachment: fixed;
            color: var(--text); -webkit-font-smoothing: antialiased;
        }
        a { color: var(--accent); }
        .wrap { max-width: 1640px; margin: 0 auto; padding: 28px clamp(16px, 4vw, 48px) 64px; }
        .back { margin: 0 0 18px; font-size: 13px; font-weight: 600; }
        .back a { text-decoration: none; }
        .back a:hover { text-decoration: underline; }
        h1 { font-size: 26px; letter-spacing: -0.02em; margin: 0 0 12px; display: flex; align-items: center; gap: 10px; }
        h1::before { content: ''; width: 10px; height: 10px; border-radius: 3px; background: var(--dot, var(--text-faint)); flex-shrink: 0; }
        .body { margin: 0 0 10px; color: var(--text-dim); font-size: 16px; line-height: 1.6; max-width: 760px; }
        .extra { margin: 0 0 8px; color: var(--text-dim); font-size: 15px; line-height: 1.55; max-width: 760px; }
        .meta { margin: 0 0 18px; color: var(--text-faint); font-size: 13px; }
        .table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 12px; background: var(--surface); }
        table.data { width: 100%; border-collapse: collapse; font-size: 13px; }
        table.data th { position: sticky; top: 0; background: var(--surface-2); color: var(--text-dim); text-align: left; font-weight: 600; padding: 11px 14px; border-bottom: 1px solid var(--border); white-space: nowrap; }
        table.data.sortable th { cursor: pointer; user-select: none; }
        table.data.sortable th:hover { color: var(--text); }
        table.data th.on::after { content: ' ↑'; color: var(--accent); }
        table.data th.on.desc::after { content: ' ↓'; }
        table.data td { padding: 10px 14px; border-bottom: 1px solid var(--border); color: var(--text-dim); }
        table.data tr { position: relative; }
        table.data tr.has-link { cursor: pointer; }
        table.data tr.has-link:hover { background: var(--surface-2); }
        table.data td.title { color: var(--text); font-weight: 600; }
        table.data td.title a { color: inherit; text-decoration: none; font-weight: 600; }
        table.data td.title a.rowlink::after { content: ''; position: absolute; inset: 0; }
        table.data td.desc { max-width: 420px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-faint); }
        .empty { color: var(--text-faint); font-size: 14px; }
        .topic-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px; }
        .topic-list li { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
        .topic-list a.topic { color: var(--text); font-weight: 650; text-decoration: none; font-size: 16px; display: inline-flex; align-items: center; gap: 8px; }
        .topic-list a.topic:hover { color: var(--accent); }
        .topic-list .dot { width: 8px; height: 8px; border-radius: 3px; display: inline-block; }
        .topic-list p { margin: 6px 0 0; color: var(--text-dim); font-size: 14.5px; line-height: 1.5; max-width: 760px; }
        footer { margin-top: 18px; color: var(--text-faint); font-size: 12px; }
"""


def load_json(name):
    with (ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def esc(value):
    return escape("" if value is None else str(value), quote=True)


def safe_filename(category_id):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", str(category_id)).strip(".-_")
    if cleaned.lower() in {"", "index"}:
        cleaned = f"{cleaned or 'topic'}-page"
    return cleaned


def item_href(item):
    return item.get("demoUrl") or item.get("url") or item.get("githubUrl") or ""


def year_label(item):
    year = item.get("year")
    return "" if year in (None, "") else str(year)


def updated_label(item):
    raw = item.get("lastCommit")
    if raw:
        return str(raw)[:10]
    return year_label(item)


def stamp(item):
    raw = item.get("lastCommit") or item.get("createdAt") or item.get("year") or ""
    return str(raw)


def build_lookup(site, catalogue):
    lookup = {}
    for item in catalogue.get("items") or []:
        key = str(item.get("id") or "").lower()
        if not key:
            continue
        merged = dict(item)
        merged["kind"] = item.get("kind") or "project"
        lookup[key] = merged
    for section in SECTIONS:
        for item in site.get(section) or []:
            key = str(item.get("id") or "").lower()
            if not key:
                continue
            base = lookup.get(key, {})
            merged = dict(base)
            for field, value in item.items():
                if value not in (None, "", [], {}):
                    merged[field] = value
            lookup[key] = merged
    return lookup


def resolve_items(category, lookup):
    items = []
    seen = set()
    for name in category.get("names") or []:
        key = str(name).lower()
        if key in seen:
            continue
        seen.add(key)
        item = lookup.get(key)
        if item:
            items.append(item)
    return items


def extra_text(category):
    lines = []
    for key, value in category.items():
        if key in SKIP_TEXT or not isinstance(value, str) or not value.strip():
            continue
        label = re.sub(r"([a-z])([A-Z])", r"\1 \2", key).replace("_", " ").strip().capitalize()
        lines.append((label, value.strip()))
    return lines


def description_html(category):
    text = (category.get("description") or "").strip()
    if text:
        return f'<p class="body">{esc(text)}</p>'
    return '<p class="body">This category has no description.</p>'


def rows_html(category, items):
    if not items:
        return '<p class="empty">No matching items.</p>'
    body = []
    title = category.get("title") or ""
    for item in items:
        href = item_href(item)
        name = item.get("title") or item.get("id") or ""
        if href:
            title_cell = f'<a class="rowlink" href="{esc(href)}">{esc(name)}</a>'
            row_class = ' class="has-link"'
        else:
            title_cell = esc(name)
            row_class = ""
        body.append(
            f"<tr{row_class}>"
            f'<td class="title">{title_cell}</td>'
            f"<td>{esc(item.get('kind') or '')}</td>"
            f"<td>{esc(title)}</td>"
            f'<td class="desc">{esc(item.get("oneLiner") or "")}</td>'
            f"<td>{esc(year_label(item))}</td>"
            f"<td>{esc(updated_label(item))}</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table class="data"><thead><tr>'
        "<th>Title</th><th>Kind</th><th>Category</th><th>Description</th><th>Year</th><th>Updated</th>"
        f"</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def shell(title, dot, inner, home_href, depth_note):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>{THEME_HEAD}
    <style>{PAGE_CSS}
    </style>
</head>
<body>
<div class="wrap">
    <p class="back"><a href="{esc(home_href)}">Home</a> · <a href="{'index.html' if depth_note == 'topic' else 'topics/index.html'}">All topics</a></p>
    <h1 style="--dot:{esc(dot)}">{esc(title)}</h1>
    {inner}
</div>
<script src="../theme.js"></script>
</body>
</html>
"""


def topic_page(category, items, filename):
    extras = "".join(f'<p class="extra"><strong>{esc(label)}.</strong> {esc(text)}</p>' for label, text in extra_text(category))
    missing = len(category.get("names") or []) - len(items)
    note = f"{len(items)} items"
    if missing > 0:
        note += f" · {missing} listed names had no matching record"
    inner = (
        description_html(category)
        + extras
        + f'<p class="meta">{esc(note)}</p>'
        + rows_html(category, items)
    )
    page_title = category.get("title") or filename
    dot = category.get("color") or "#9aa0aa"
    return shell(page_title, dot, inner, "../index.html", "topic")


def index_page(entries):
    cards = []
    for category, filename, items in entries:
        text = (category.get("description") or "").strip() or "This category has no description."
        dot = category.get("color") or "#9aa0aa"
        cards.append(
            "<li>"
            f'<a class="topic" href="{esc(filename)}"><span class="dot" style="background:{esc(dot)}"></span>{esc(category.get("title") or filename)}</a>'
            f"<p>{esc(text)}</p>"
            f'<p class="meta">{len(items)} items</p>'
            "</li>"
        )
    inner = f'<ul class="topic-list">{"".join(cards)}</ul>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Topics</title>{THEME_HEAD}
    <style>{PAGE_CSS}
    </style>
</head>
<body>
<div class="wrap">
    <p class="back"><a href="../index.html">Home</a></p>
    <h1 style="--dot:#6ea8fe">Topics</h1>
    <p class="body">One page for each category, with its description and the items listed under it.</p>
    {inner}
</div>
<script src="../theme.js"></script>
</body>
</html>
"""


def main():
    site = load_json("site_content.json")
    catalogue = load_json("catalogue_data.json")
    lookup = build_lookup(site, catalogue)
    categories = site.get("categories") or []
    TOPICS.mkdir(exist_ok=True)
    used = {"index"}
    entries = []
    for category in categories:
        filename = safe_filename(category.get("id") or category.get("title") or "topic")
        base = filename
        n = 2
        while filename.lower() in used:
            filename = f"{base}-{n}"
            n += 1
        used.add(filename.lower())
        items = resolve_items(category, lookup)
        (TOPICS / f"{filename}.html").write_text(topic_page(category, items, filename), encoding="utf-8")
        entries.append((category, f"{filename}.html", items))
    (TOPICS / "index.html").write_text(index_page(entries), encoding="utf-8")
    print(f"Wrote {len(entries)} topic pages and topics/index.html")


if __name__ == "__main__":
    main()
