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
def read_json_array(name):
    match = re.search(r'\bconst\s+' + re.escape(name) + r'\s*=\s*', html)
    assert match, f"Missing {name} array"
    value, _ = json.JSONDecoder().raw_decode(html[match.end():])
    assert isinstance(value, list), f"{name} must be an array"
    return value


records = read_json_array("records")
categories = read_json_array("categories")
assert records, "Archive records must not be empty"
urls = []
linkedin_memberships = None
for record in records:
    assert isinstance(record, dict), "Archive records must be JSON objects"
    url = record["url"]
    urls.append(url)
    primary = record["category"]
    memberships = record.get("categories", [primary])
    assert primary in memberships, "Primary category must be included"
    assert len(memberships) == len(set(memberships)), "Duplicate category membership"
    assert all(category in categories and category != "All" for category in memberships)
    if url == "https://www.linkedin.com/in/joenasrprofile":
        linkedin_memberships = memberships
assert len(urls) == len(set(urls)), "Duplicate archive URL"
prerendered = re.findall(r'<article class="archive-record" id="signal-\d{3}">', html)
assert len(prerendered) == len(records), "Pre-rendered archive count must match JavaScript record count"
hero_static = re.search(r'<strong id="heroCount">(\d+) records</strong>', html)
result_static = re.search(r'<span id="resultCount">(\d+) references</span>', html)
assert hero_static and int(hero_static.group(1)) == len(records), "Hero archive count is stale"
assert result_static and int(result_static.group(1)) == len(records), "Result archive count is stale"
assert linkedin_memberships, "LinkedIn archive route must remain present"
# Professional tags and visitor-facing archive categories are separate taxonomies.
# Archive memberships are validated against the site's categories above.
profile_categories = identity["linkedin_aligned_work_experience"]["profile_categories"]
assert isinstance(profile_categories, list) and profile_categories, "Professional tags must be a non-empty list"
assert all(isinstance(tag, str) and tag for tag in profile_categories), "Invalid professional tag"
assert len(profile_categories) == len(set(profile_categories)), "Duplicate professional tag"


# Query-aware public-surface registry integrity.
registry = identity.get("public_surface_registry", [])
assert registry, "public_surface_registry must not be empty"
surface_ids = [surface["id"] for surface in registry]
assert len(surface_ids) == len(set(surface_ids)), "Duplicate public-surface id"
surface_urls = [surface["url"] for surface in registry]
assert len(surface_urls) == len(set(surface_urls)), "Duplicate public-surface URL"

allowed_temporal = {"CURRENT", "HISTORICAL"}
allowed_priority = {"PRIMARY_CURRENT", "SECONDARY_SPECIALIST", "HISTORICAL_SUPPORT", "PENDING_VERIFICATION"}
allowed_retrieval = {"ACTIVE", "ACTIVE_QUERY_SPECIFIC", "WEAK", "UNRESOLVED"}
allowed_relationship = {"PROFILE", "DIRECTORY_PROFILE", "CATALOGUE_PROFILE", "ROUTER", "EVIDENCE", "PENDING_PUBLIC_PROFILE", "CREATOR_OPERATED_ECOSYSTEM"}
for surface in registry:
    assert surface["temporal_state"] in allowed_temporal, f"Invalid temporal state: {surface['id']}"
    assert surface["nervous_system_priority"] in allowed_priority, f"Invalid priority: {surface['id']}"
    assert surface["retrieval_state"] in allowed_retrieval, f"Invalid retrieval state: {surface['id']}"
    assert surface["relationship_to_joe"] in allowed_relationship, f"Invalid relationship: {surface['id']}"
    if surface["nervous_system_priority"] == "PENDING_VERIFICATION":
        assert surface["retrieval_state"] == "UNRESOLVED", f"Pending surface must remain unresolved: {surface['id']}"

surface_id_set = set(surface_ids)
for route_name, route in identity.get("query_routes", {}).items():
    for surface_id in route.get("surface_ids", []):
        assert surface_id in surface_id_set, f"Unknown surface id in query route {route_name}: {surface_id}"

reverbnation = next(surface for surface in registry if surface["id"] == "reverbnation")
assert reverbnation["temporal_state"] == "HISTORICAL"
assert reverbnation["retrieval_state"] == "ACTIVE_QUERY_SPECIFIC"
assert reverbnation["query_relevance"].get("Joe Nasr guitar") == "HIGH"

ids = re.findall(r'\bid="([^"]+)"', html)
assert len(ids) == len(set(ids)), "Duplicate HTML id"
for target in re.findall(r'href="#([^"]+)"', html):
    assert target in ids, f"Broken section link: #{target}"
print(f"Published JSON and JSON-LD valid; {len(records)} unique archive records; category and section links valid.")

