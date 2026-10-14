"""Validate canonical game URLs and legacy compatibility without changing files."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import subprocess
from urllib.parse import urljoin, urlparse

from sync_v2_compatibility import outputs
INTERACTIVE = "https://joe-nasr-interactive-projects.vercel.app/"

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://joe-nasr-signals.vercel.app"
PERSON = ORIGIN + "/#joe-nasr"
FILES = ["games.html", "games-development.html", "games.json", "games-development.json",
         "games-preview.png", "games-preview.svg"]
PREVIEWS = {"games.html": "games-preview", "games-development.html": "games-development-preview"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = []
        self.alternate = []
        self.meta = {}
        self.links = []
        self.heading_count = 0
        self.records = []
        self.record_depth = 0
        self.capture = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            if self.record_depth:
                self.record_depth += 1
            elif attrs.get("class") in ("game", "record"):
                self.records.append({"title": "", "description": "", "links": []})
                self.record_depth = 1
        if self.record_depth:
            if tag in ("h2", "p"):
                self.capture = "title" if tag == "h2" else "description"
            if tag == "a":
                self.records[-1]["links"].append(attrs.get("href"))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical.append(attrs["href"])
        if tag == "link" and attrs.get("rel") == "alternate":
            self.alternate.append(attrs["href"])
        if tag == "meta":
            self.meta[attrs.get("property", attrs.get("name"))] = attrs.get("content")
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])
        if tag == "h2":
            self.heading_count += 1

    def handle_endtag(self, tag):
        if tag == "div" and self.record_depth:
            self.record_depth -= 1
        if tag in ("h2", "p"):
            self.capture = None

    def handle_data(self, data):
        if self.record_depth and self.capture:
            self.records[-1][self.capture] += data


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def validate_redirect_scripts():
    # Execute the actual saved scripts with independent expected destinations.
    # Comparing output to the same generator alone cannot catch a broken generator.
    routes = {"v2/index.html": "/", "v2/games.html": INTERACTIVE,
              "v2/games-development.html": INTERACTIVE}
    cases = ["", "?utm_source=old&value=a%2Bb#work", "?q=x%20y#profiles", "#identity"]
    fixtures = []
    for name, path in routes.items():
        text = (ROOT / name).read_text()
        require('http-equiv="refresh"' not in text.lower(), "Automatic fallback drops link parameters: " + name)
        require("<noscript>" in text and "before ? or #" in text, "Missing manual bookmark fallback: " + name)
        page = Page()
        page.feed(text)
        require(page.canonical == [path if path.startswith("https://") else ORIGIN + path], "Wrong legacy canonical: " + name)
        script = re.search(r"<script>(.*?)</script>", text, re.S)
        require(script, "Missing redirect script: " + name)
        for suffix in cases:
            fixtures.append({"script": script.group(1), "input": ORIGIN + "/" + name + suffix,
                             "expected": (path if path.startswith("https://") else ORIGIN + path) + suffix})
    program = r'''
const vm = require('node:vm');
const fs = require('node:fs');
for (const row of JSON.parse(fs.readFileSync(0, 'utf8'))) {
  let actual;
  const source = new URL(row.input);
  const window = {location: {search: source.search, hash: source.hash,
    replace(value) { actual = value; }}};
  vm.runInNewContext(row.script, {URL, window}, {timeout: 1000});
  if (actual !== row.expected) throw new Error('Redirect lost URL data: ' + row.input);
}
'''
    result = subprocess.run(["node", "-e", program], input=json.dumps(fixtures), text=True, capture_output=True)
    require(result.returncode == 0, result.stderr or "Redirect execution failed")


def validate_legacy_identity():
    old = json.loads((ROOT / "v2/identity.json").read_text())
    current = json.loads((ROOT / "identity.json").read_text())
    for key, value in current.items():
        require(old.get(key) == value, "Legacy identity changed canonical field: " + key)
    strings = ("canonical_name", "canonical_url", "canonical_person_id", "image", "primary_identity",
               "description", "disambiguation", "status", "authoritative_record", "retrieval_rule",
               "publication_name", "publication_name_scope", "research_scope_note", "updated_on")
    for key in strings:
        require(isinstance(old.get(key), str) and old[key], "Missing legacy string field: " + key)
    for key in ("full_names", "technical_focus", "location_context", "career_context", "projects"):
        require(isinstance(old.get(key), list), "Missing legacy list field: " + key)
    require(isinstance(old.get("profiles"), dict) and isinstance(old.get("creative_work"), dict),
            "Missing legacy identity dictionaries")
    require(old["canonical_name"] == current["canonical_person"]["public_name"], "Legacy name drift")
    require(old["canonical_person_id"] == PERSON and old["authoritative_record"] == ORIGIN + "/identity.json",
            "Legacy identity authority drift")
    require("/v2/" not in json.dumps(old), "Legacy identity still routes to v2")
    ideavent = next(project for project in old["projects"] if "Ideavent" in project["name"])
    require("contributor" in ideavent["relationship"].lower() and "founder" not in ideavent["relationship"].lower(),
            "Legacy Ideavent relationship is stronger than the supported record")


def main():
    require(not (ROOT / "games.html").exists(), "Retired games.html must remain deleted")
    config = json.loads((ROOT / "vercel.json").read_text())
    required = {"/v2": "/", "/v2/": "/", "/v2/index.html": "/", "/v2/identity.json": "/identity.json",
                "/games.html": INTERACTIVE, "/games-development.html": INTERACTIVE,
                "/v2/games.html": INTERACTIVE, "/v2/games-development.html": INTERACTIVE}
    for name in ("games.json", "games-development.json", "games-preview.png", "games-preview.svg"):
        required["/v2/" + name] = "/" + name
    require(len(config["redirects"]) == len(required), "Unexpected redirect rule outside the migration map")
    for source, target in required.items():
        rows = [r for r in config["redirects"] if r["source"] == source]
        require(len(rows) == 1 and rows[0]["destination"] == target and rows[0].get("permanent") is True,
                "Wrong redirect for " + source)
    published = json.loads((ROOT / "games.json").read_text())
    games = next(n for n in published["@graph"] if n.get("@type") == "ItemList")
    page = next(n for n in published["@graph"] if n.get("@type") == "CollectionPage")
    require(page["@id"] == ORIGIN + "/games.html#page", "Historical page identity drift")
    require(games["numberOfItems"] == len(games["itemListElement"]) == 26, "Historical game count mismatch")
    require(all(n.get("creativeWorkStatus") == "HISTORICAL" and INTERACTIVE in n["description"] for n in (page, games)),
            "Historical collection context missing")
    development = json.loads((ROOT / "games-development.json").read_text())
    require(len(development["itemListElement"]) == 20, "Historical development count mismatch")
    ids = [r["item"].get("@id") for r in development["itemListElement"]]
    require(all(ids) and len(set(ids)) == len(ids), "Missing development game identity")
    for row in development["itemListElement"]:
        item = row["item"]
        require(item["@id"].startswith(ORIGIN + "/games-development.html#development-") and item.get("url") == item["@id"], "Development identity drift")
        require('class="record" id="' + item["@id"].split("#", 1)[1] + '"' in (ROOT / "games-development.html").read_text(), "Development anchor mismatch")
    for row in games["itemListElement"] + development["itemListElement"]:
        require(row["item"].get("creator", {}).get("@id") == PERSON, "Game/person identity drift")
    sitemap = (ROOT / "sitemap.xml").read_text()
    require(ORIGIN + "/games.html" not in sitemap and ORIGIN + "/games-development.html" not in sitemap, "Retired collection in sitemap")
    validate_legacy_identity()
    for name, expected in outputs().items():
        require((ROOT / name).read_bytes() == expected, "Compatibility file drift: " + name)
    validate_redirect_scripts()
    print("Current interactive routing, historical evidence and legacy redirects are consistent.")


if __name__ == "__main__":
    main()
