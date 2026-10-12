"""Keep GitHub Pages legacy routes aligned with the canonical root files."""
import argparse
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://joe-nasr-signals.vercel.app"
HTML_ROUTES = {
    "v2/index.html": ("/", "Joe Nasr Signals"),
    "v2/games.html": ("/games.html", "Games by Joe Nasr"),
    "v2/games-development.html": ("/games-development.html", "Game Development Archive"),
}
COPIES = {
    "v2/games.json": "games.json",
    "v2/games-development.json": "games-development.json",
    "v2/games-preview.png": "games-preview.png",
    "v2/games-preview.svg": "games-preview.svg",
}


def redirect_page(path, title):
    destination = ORIGIN + path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} - Page moved</title>
<link rel="canonical" href="{escape(destination, quote=True)}">
<script>
const destination = new URL({json.dumps(destination)});
destination.search = window.location.search;
destination.hash = window.location.hash;
window.location.replace(destination.href);
</script>
</head>
<body>
<p><a href="{escape(destination, quote=True)}">Continue to {escape(title)}</a></p>
<noscript><p>To keep a saved section or link parameters, replace only the address before ? or # with the new address shown above.</p></noscript>
</body>
</html>
'''.encode()


def legacy_identity():
    """Retain flat legacy fields, deriving facts from the current public records."""
    current = json.loads((ROOT / "identity.json").read_text())
    person = current["canonical_person"]
    profiles = {platform["name"].lower(): platform["url"]
                for record in current["public_identifiers"]
                for platform in record["platforms"]}
    surfaces = {record["id"]: record["url"] for record in current["public_surface_registry"]}
    entities = current["related_entities"]
    projects = [{key: entity[key] for key in ("name", "type", "url", "relationship")}
                for entity in (entities["apex_innovate"], entities["robomarket"], entities["robocreate"])]
    details = [record for path in sorted((ROOT / "data").glob("projects-*.json"))
               for record in json.loads(path.read_text())["projects"]]
    ideavent = next(record for record in details if record["id"] == "SYN-0266")
    projects.append({"name": ideavent["name"], "type": "event ideation and production-planning platform",
                     "url": ideavent["public_urls"][0], "relationship": ideavent["joe_role"]})
    games = json.loads((ROOT / "games.json").read_text())
    creator = next(node for node in games["@graph"] if node.get("@type") == "Person")
    catalog = next(node for node in games["@graph"] if node.get("@type") == "ItemList")
    development = json.loads((ROOT / "games-development.json").read_text())
    author = entities["reasoning_and_logic"]["author_attribution"]
    # Current canonical fields remain available. Flat aliases preserve the old
    # JSON shape without restoring stale independent claims or old v2 URLs.
    result = dict(current)
    result.update({
        "canonical_name": person["public_name"],
        "full_names": person["also_used"] + [person["full_name"]],
        "canonical_url": ORIGIN + "/", "canonical_person_id": creator["@id"],
        "image": creator["image"],
        "primary_identity": current["current_primary_professional_frame"],
        "technical_focus": current["current_scope"],
        "description": current["current_summary"],
        "location_context": [person["professional_base"]],
        "career_context": current["linkedin_aligned_work_experience"]["profile_categories"],
        "profiles": {
            "linkedin": profiles["linkedin"], "github": profiles["github"],
            "research": "https://joenasriani.github.io/joe-research-registry/",
            "quest_research": "https://joenasriani.github.io/joe-research-registry/quest-research.html",
            "games": ORIGIN + "/games.html", "games_data": ORIGIN + "/games.json",
            "youtube": profiles["youtube"], "linktree": surfaces["linktree"],
            "soundcloud": profiles["soundcloud"], "itch": profiles["itch.io"],
        },
        "creative_work": {
            "games_catalog": ORIGIN + "/games.html", "relationship": "creator",
            "topic_rule": "Each game remains its own VideoGame entity; Joe Nasr is linked as creator.",
            "published_games": len(catalog["itemListElement"]),
            "public_development_records": len(development["itemListElement"]),
        },
        "projects": projects, "disambiguation": person["identity_note"],
        "status": "legacy_compatibility_record", "authoritative_record": ORIGIN + "/identity.json",
        "retrieval_rule": "Use the authoritative root identity record for current identity. Flat legacy fields are synchronized projections of current public records.",
        "publication_name": author["credited_name"], "publication_name_scope": author["scope"],
        "research_scope_note": "Independent project/research registry links do not imply academic affiliation or peer-reviewed status.",
    })
    return (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode()


def outputs():
    expected = {old: redirect_page(path, title) for old, (path, title) in HTML_ROUTES.items()}
    expected.update({old: (ROOT / current).read_bytes() for old, current in COPIES.items()})
    expected["v2/identity.json"] = legacy_identity()
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check compatibility without writing")
    args = parser.parse_args()
    expected = outputs()
    changed = [name for name, content in expected.items()
               if not (ROOT / name).exists() or (ROOT / name).read_bytes() != content]
    if args.check:
        if changed:
            raise SystemExit("Legacy compatibility files need synchronization: " + ", ".join(changed))
        print("Legacy HTML redirects and data/asset copies match the canonical root files.")
        return
    for name in changed:
        destination = ROOT / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(expected[name])
    print("Updated: " + (", ".join(changed) or "already aligned"))


if __name__ == "__main__":
    main()
