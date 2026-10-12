#!/usr/bin/env python3
"""Generate crawlable credentials HTML and JSON-LD from the public data catalog."""
import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://joe-nasr-signals.vercel.app/credentials/"
CATEGORIES = (
    "University Education", "VR / XR & Interactive", "AI & Machine Learning",
    "Programming & Cloud", "Creative Direction & Branding", "3D & Animation",
    "Film, Video & VFX", "UX / UI Design", "Marketing & Advertising",
    "Recognition & Awards",
)

def escape(value):
    return html.escape(str(value), quote=True)

def card(r):
    date = r["date"] or "0000"
    issuer_year = escape(r["issuer"]) + (" · " + escape(r["date"][:4]) if r["date"] else "")
    return (
        f'<article class="credential" id="{escape(r["id"])}" data-category="{escape(r["category"])}" '
        f'data-title="{escape(r["title"].lower())}" data-date="{escape(date)}">'
        '<div class="preview" aria-hidden="true"><span class="paper"><span class="paper-mark">JN / EDUCATION</span>'
        '<span class="paper-line"></span>'
        f'<span class="paper-name">{escape(r["title"])}</span>'
        f'<span class="paper-issuer">{escape(r["issuer"])}</span></span></div>'
        '<div class="details">'
        f'<p class="kind">{escape(r["category"])} · {escape(r["type"])}</p>'
        f'<h2>{escape(r["title"])}</h2>'
        f'<p class="issuer">{issuer_year}</p>'
        '<p class="evidence">Documented completion; public issuer verification not yet established.</p>'
        '</div></article>'
    )

def schema(records, person_ref):
    return {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": BASE + "#webpage", "url": BASE,
             "name": "Education & Credentials | Joe Nasr",
             "isPartOf": {"@id": "https://joe-nasr-signals.vercel.app/#website"},
             "about": {"@id": person_ref}, "mainEntity": {"@id": BASE + "#list"}},
            {"@type": "ItemList", "@id": BASE + "#list",
             "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "url": BASE + "#" + r["id"], "name": r["title"]}
                 for i, r in enumerate(records)
             ]},
        ],
    }

def replace_block(source, tag, content):
    start = f"<!-- GENERATED {tag}: run python scripts/build_credentials.py -->"
    end = f"<!-- END GENERATED {tag} -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    assert len(pattern.findall(source)) == 1, f"Missing/duplicate generated block: {tag}"
    return pattern.sub(lambda _: start + "\n" + content + "\n" + end, source)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Fail if generated HTML differs from catalog")
    args = ap.parse_args()
    catalog = json.loads((ROOT / "data/credentials.json").read_text(encoding="utf-8"))
    records = catalog["records"]
    assert len({r["id"] for r in records}) == len(records), "Duplicate credential IDs"
    assert all(r["category"] in CATEGORIES for r in records), "Unknown credential category"
    assert all(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", r["id"]) for r in records), "Invalid anchor ID"
    assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["date"]) or not r["date"] for r in records), "Invalid date"
    assert catalog["person_ref"] == "https://joe-nasr-signals.vercel.app/#joe-nasr"
    original = (ROOT / "credentials/index.html").read_text(encoding="utf-8")
    encoded_schema = json.dumps(schema(records, catalog["person_ref"]), ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
    output = replace_block(original, "JSON-LD", encoded_schema)
    output = replace_block(output, "CATEGORIES",
        '<option value="">All subject categories</option>' +
        "".join(f"<option>{escape(cat)}</option>" for cat in CATEGORIES))
    output = replace_block(output, "CARDS", "\n".join(card(r) for r in records))
    if args.check:
        assert output == original, "Generated credentials HTML is stale: run python scripts/build_credentials.py"
        print(f"Credentials HTML synchronized: {len(records)} records")
    else:
        (ROOT / "credentials/index.html").write_text(output, encoding="utf-8")
        print(f"Generated credentials HTML: {len(records)} records")

if __name__ == "__main__":
    main()
