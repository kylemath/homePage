#!/usr/bin/env python3
"""Add homepage paper cards for Scholar publications that are not already listed.

Does not download PDFs, generate thumbnails, or rewrite cards that already match.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_SITE = ROOT / "site_content.json"
SLUG_LIMIT = 60


def normalize_title(title):
    """Lowercase and remove punctuation and whitespace."""
    return re.sub(r"[^a-z0-9]+", "", (title or "").lower())


def citation_keys(url):
    """Stable identity for a Scholar citation URL, including citation_for_view."""
    if not url or not str(url).strip():
        return set()
    text = str(url).strip()
    keys = {text}
    match = re.search(r"citation_for_view=([^&#]+)", text)
    if match:
        keys.add("citation:" + match.group(1))
    return keys


def slugify(title, limit=SLUG_LIMIT):
    slug = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
    slug = slug[:limit].strip("-")
    return slug or "untitled"


def unique_paper_id(year_part, title, taken):
    base = f"paper-{year_part}-{slugify(title)}"
    if base not in taken:
        return base
    n = 2
    while f"{base}-{n}" in taken:
        n += 1
    return f"{base}-{n}"


def _year_int(pub):
    year_int = pub.get("year_int")
    if isinstance(year_int, int) and year_int > 0:
        return year_int
    raw = pub.get("year")
    if isinstance(raw, int) and raw > 0:
        return raw
    if isinstance(raw, str) and raw.isdigit():
        value = int(raw)
        return value if value > 0 else None
    return None


def _papers_category(site):
    for category in site.get("categories") or []:
        if category.get("id") == "papers":
            return category
    return None


def add_cards_to_site(publications, site):
    """Insert new paper cards into an in-memory site dict.

    Returns (added, skipped). Existing papers, names, and other fields are left
    unchanged. New cards are inserted at the front, in the given publication order.
    """
    papers = site.setdefault("papers", [])
    title_index = {}
    url_index = set()
    taken_ids = set()
    for paper in papers:
        paper_id = paper.get("id")
        if paper_id:
            taken_ids.add(paper_id)
        key = normalize_title(paper.get("title"))
        if key:
            title_index.setdefault(key, paper)
        url_index.update(citation_keys(paper.get("url")))

    category = _papers_category(site)
    names = list((category or {}).get("names") or [])
    taken_ids.update(name for name in names if name)

    new_cards = []
    skipped = 0
    for pub in publications or []:
        title = (pub.get("title") or "").strip()
        url = (pub.get("url") or "").strip()
        title_key = normalize_title(title)
        url_keys = citation_keys(url)
        if (title_key and title_key in title_index) or (url_keys and url_keys & url_index):
            skipped += 1
            continue

        year_int = _year_int(pub)
        year_part = year_int if year_int else "unknown"
        first_author = (pub.get("first_author") or pub.get("authors") or "").strip()
        paper_id = unique_paper_id(year_part, title, taken_ids)
        if year_int:
            one_liner = f"{first_author} ({year_int})"
        else:
            raw_year = pub.get("year")
            one_liner = f"{first_author} ({raw_year})" if raw_year else first_author

        card = {
            "id": paper_id,
            "kind": "paper",
            "title": title,
            "authors": first_author,
            "year": year_int,
            "url": url or None,
            "pdfPage": None,
            "figures": [],
            "oneLiner": one_liner,
        }
        new_cards.append(card)
        taken_ids.add(paper_id)
        if title_key:
            title_index[title_key] = card
        url_index.update(url_keys)

    if not new_cards:
        return 0, skipped

    site["papers"] = new_cards + papers
    if category is not None:
        existing_names = list(category.get("names") or [])
        seen = set(existing_names)
        front = [card["id"] for card in new_cards if card["id"] not in seen]
        category["names"] = front + existing_names
    return len(new_cards), skipped


def add_paper_cards(publications, site_content_path=None):
    """Add missing paper cards. Returns how many cards were added.

    Writes site_content.json only when at least one card is new.
    """
    path = Path(site_content_path) if site_content_path else DEFAULT_SITE
    site = json.loads(path.read_text(encoding="utf-8"))
    added, skipped = add_cards_to_site(publications, site)
    print(f"Paper cards: added {added}, skipped {skipped}")
    if added:
        path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {added} new paper card(s) to {path}")
    else:
        print(f"No new paper cards; left {path} unchanged")
    return added


def _self_test():
    import tempfile

    existing = {
        "id": "paper-2020-existing-title",
        "kind": "paper",
        "title": "Existing Title",
        "authors": "A Person",
        "year": 2020,
        "url": "https://scholar.google.com/citations?view_op=view_citation&citation_for_view=abc:1",
        "pdfPage": None,
        "figures": [],
        "oneLiner": "A Person (2020)",
    }
    site = {
        "papers": [existing],
        "categories": [
            {
                "id": "papers",
                "title": "Papers",
                "names": ["paper-2020-existing-title", "paper-keep-me"],
            }
        ],
    }
    publications = [
        {
            "title": "Existing Title!",
            "first_author": "Should Not Replace",
            "year": "2020",
            "year_int": 2020,
            "url": "https://scholar.google.com/citations?view_op=view_citation&hl=en&citation_for_view=abc:1",
        },
        {
            "title": "Brand New Discovery About Attention",
            "first_author": "B Person et al.",
            "year": "2026",
            "year_int": 2026,
            "url": "https://scholar.google.com/citations?view_op=view_citation&citation_for_view=abc:2",
        },
    ]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "site_content.json"
        path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
        added = add_paper_cards(publications, path)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert added == 1, added
        assert loaded["papers"][0]["id"] == "paper-2026-brand-new-discovery-about-attention"
        assert loaded["papers"][0]["authors"] == "B Person et al."
        assert loaded["papers"][0]["year"] == 2026
        assert loaded["papers"][0]["oneLiner"] == "B Person et al. (2026)"
        assert loaded["papers"][0]["pdfPage"] is None
        assert loaded["papers"][0]["figures"] == []
        assert loaded["papers"][1] == existing
        assert loaded["categories"][0]["names"][:2] == [
            "paper-2026-brand-new-discovery-about-attention",
            "paper-2020-existing-title",
        ]
        assert "paper-keep-me" in loaded["categories"][0]["names"]
        added_again = add_paper_cards(publications, path)
        assert added_again == 0
        reloaded = json.loads(path.read_text(encoding="utf-8"))
        assert reloaded == loaded
    print("self-test ok: added 1, skipped 1")


if __name__ == "__main__":
    _self_test()
