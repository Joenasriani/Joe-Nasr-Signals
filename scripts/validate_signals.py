"""Validate published data without rewriting profiles, designs or game records."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
for path in ROOT.rglob("*.json"):
    if ".git" not in path.parts:
        json.loads(path.read_text())
for path in ROOT.rglob("*.html"):
    for block in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', path.read_text(), re.S):
        json.loads(block)

html = (ROOT / "index.html").read_text()
schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
person = next(node for node in schema["@graph"] if node.get("@type") == "Person")
organizations = [node for node in schema["@graph"] if node.get("@type") == "Organization"]
for organization in organizations:
    assert organization.get("url", "").startswith("https://"), "Organization URL must remain intact"
    assert organization["url"] not in person["sameAs"], "Organizations are distinct from the person"

identity = json.loads((ROOT / "identity.json").read_text())
records_block = re.search(r'const records = \[(.*?)\n\];', html, re.S).group(1)
records = re.findall(r'\{(.*?)\}', records_block, re.S)
categories = json.loads(re.search(r'const categories = (\[.*?\]);', html).group(1))
urls = []
linkedin_memberships = None
for record in records:
    url = re.search(r'url: "([^"]+)"', record).group(1)
    urls.append(url)
    primary = re.search(r'category: "([^"]+)"', record).group(1)
    match = re.search(r'categories: (\[.*?\])', record)
    memberships = json.loads(match.group(1)) if match else [primary]
    assert primary in memberships, "Primary category must be included"
    assert len(memberships) == len(set(memberships)), "Duplicate category membership"
    assert all(category in categories and category != "All" for category in memberships)
    if url == "https://www.linkedin.com/in/joenasrprofile":
        linkedin_memberships = memberships
assert len(urls) == len(set(urls)), "Duplicate archive URL"
assert linkedin_memberships == identity["linkedin_aligned_work_experience"]["profile_categories"]

ids = re.findall(r'\bid="([^"]+)"', html)
assert len(ids) == len(set(ids)), "Duplicate HTML id"
for target in re.findall(r'href="#([^"]+)"', html):
    assert target in ids, f"Broken section link: #{target}"
print(f"Published JSON and JSON-LD valid; {len(records)} unique archive records; category and section links valid.")
