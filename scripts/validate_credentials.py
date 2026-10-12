#!/usr/bin/env python3
"""Validate public credential records against static HTML without contacting providers."""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(root / "scripts/build_credentials.py"), "--check"], cwd=root, check=True)
catalog = json.loads((root / "data/credentials.json").read_text(encoding="utf-8"))
page = (root / "credentials/index.html").read_text(encoding="utf-8")
records = catalog["records"]
assert catalog["status"] == "initial_documentary_subset_not_complete"
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), "Duplicate credential IDs"
assert len({(r["title"].lower(), r["issuer"].lower(), r["date"]) for r in records}) == len(records), "Duplicate qualification records"
assert catalog["person_ref"] == "https://joe-nasr-signals.vercel.app/#joe-nasr"
assert 'rel="canonical" href="https://joe-nasr-signals.vercel.app/credentials/"' in page
assert 'href="/favicon.svg"' in page
cards = re.findall(r'<article class="credential" id="([^"]+)" data-category="([^"]+)"[^>]*>(.*?)</article>', page, re.S)
assert len(cards) == len(records), f"Expected {len(records)} cards, got {len(cards)}"
cards_by_id = {id: (html.unescape(cat), body) for id, cat, body in cards}
assert len(cards_by_id) == len(cards)
for r in records:
    assert r["id"] in cards_by_id, f"Missing {r['id']}"
    category, body = cards_by_id[r["id"]]
    assert category == r["category"], f"Wrong category: {r['id']}"
    for text in (r["title"], r["issuer"], r["type"]):
        assert html.escape(text, quote=True) in body, f"Missing content {text}: {r['id']}"
    if r["date"]:
        assert r["date"][:4] in body, f"Missing year: {r['id']}"
    assert f'<option>{html.escape(r["category"], quote=True)}</option>' in page
    assert r.get("public_verification_url") is None, "Issuer links require separate approved verification"
m = re.search(r'<script type="application/ld\+json">([\s\S]*?)</script>', page)
assert m, "Structured data missing"
schema = json.loads(m.group(1))
graph = schema["@graph"]
person_refs = [v["about"]["@id"] for v in graph if v.get("@type") == "CollectionPage"]
assert person_refs == [catalog["person_ref"]], "Canonical Person mismatch"
list_records = next(v for v in graph if v.get("@type") == "ItemList")["itemListElement"]
assert [(v["url"].split("#")[-1], v["name"]) for v in list_records] == [(r["id"], r["title"]) for r in records], "Schema/HTML catalog mismatch"
assert all("https://www.dropbox.com/" not in str(r) for r in records), "Private Dropbox reference exposed"
assert "Preview graphics are placeholders" in page
assert "Issuer verification" in page or "issuer verification" in page
print(f"Credentials pass: {len(records)} unique documentary records, HTML and JSON-LD consistent")
