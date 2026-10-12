"""Validate canonical game URLs and legacy compatibility without changing files."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import subprocess
from urllib.parse import urljoin, urlparse

from sync_v2_compatibility import outputs

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
    routes = {"v2/index.html": "/", "v2/games.html": "/games.html",
              "v2/games-development.html": "/games-development.html"}
    cases = ["", "?utm_source=old&value=a%2Bb#work", "?q=x%20y#profiles", "#identity"]
    fixtures = []
    for name, path in routes.items():
        text = (ROOT / name).read_text()
        require('http-equiv="refresh"' not in text.lower(), "Automatic fallback drops link parameters: " + name)
        require("<noscript>" in text and "before ? or #" in text, "Missing manual bookmark fallback: " + name)
        page = Page()
        page.feed(text)
        require(page.canonical == [ORIGIN + path], "Wrong legacy canonical: " + name)
        script = re.search(r"<script>(.*?)</script>", text, re.S)
        require(script, "Missing redirect script: " + name)
        for suffix in cases:
            fixtures.append({"script": script.group(1), "input": ORIGIN + "/" + name + suffix,
                             "expected": ORIGIN + path + suffix})
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
    for name in FILES:
        require((ROOT / name).is_file(), "Missing canonical file: " + name)
        if not name.endswith(".png"):
            require("/v2/" not in (ROOT / name).read_text(), "Legacy URL in canonical file: " + name)

    config = json.loads((ROOT / "vercel.json").read_text())
    required = {"/v2": "/", "/v2/": "/", "/v2/index.html": "/",
                "/v2/identity.json": "/identity.json"}
    required.update({"/v2/" + name: "/" + name for name in FILES})
    require(len(config["redirects"]) == len(required), "Unexpected redirect rule outside the migration map")
    for old, new in required.items():
        rules = [rule for rule in config["redirects"] if rule["source"] == old]
        require(len(rules) == 1, "Expected one redirect for " + old)
        require(rules[0]["destination"] == new and rules[0].get("permanent") is True,
                "Wrong redirect for " + old)

    published = json.loads((ROOT / "games.json").read_text())
    games = next(node for node in published["@graph"] if node.get("@type") == "ItemList")
    require(games["numberOfItems"] == len(games["itemListElement"]), "Published game count mismatch")
    development = json.loads((ROOT / "games-development.json").read_text())
    require(len({row["item"]["@id"] for row in games["itemListElement"]}) == len(games["itemListElement"]),
            "Duplicate game identity")
    require(games["@id"] == ORIGIN + "/games.html#games" and games["url"] == ORIGIN + "/games.html",
            "Wrong published catalog identity")
    require(development["@id"] == ORIGIN + "/games-development.html#development-games", "Wrong development catalog identity")
    for html_name, data_name, count in [
        ("games.html", "games.json", len(games["itemListElement"])),
        ("games-development.html", "games-development.json", len(development["itemListElement"])),
    ]:
        text = (ROOT / html_name).read_text()
        page = Page()
        page.feed(text)
        canonical = ORIGIN + "/" + html_name
        require(page.canonical == [canonical], "Incorrect canonical: " + html_name)
        require(page.meta.get("og:url") == canonical, "Incorrect share URL: " + html_name)
        require(any(urljoin(canonical, link) == ORIGIN + "/" + data_name for link in page.alternate),
                "Missing machine-readable catalog: " + html_name)
        require(page.heading_count == count, "Visible/catalog game count mismatch: " + html_name)
        preview = PREVIEWS[html_name]
        for key in ("og:image", "twitter:image"):
            require(page.meta.get(key) == ORIGIN + "/" + preview + ".png", "Incorrect image: " + html_name)
        for extension in ("png", "svg"):
            require((ROOT / (preview + "." + extension)).is_file(), "Missing preview: " + preview)
        png = (ROOT / (preview + ".png")).read_bytes()
        require(png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (1200, 630),
                "Invalid preview dimensions: " + preview)
        svg = (ROOT / (preview + ".svg")).read_text()
        require("/v2/" not in svg and ORIGIN.removeprefix("https://") + "/" + html_name in svg,
                "Preview points to the wrong page: " + preview)
        label = "PUBLISHED" if html_name == "games.html" else "DEVELOPMENT"
        require(str(count) + " " + label in svg, "Wrong preview count or status: " + preview)
        for link in page.links:
            target = urlparse(urljoin(canonical, link))
            if target.netloc == urlparse(ORIGIN).netloc:
                path = target.path.lstrip("/") or "index.html"
                require((ROOT / path).is_file(), "Missing local link: " + link)
        schemas = [json.loads(block) for block in re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.S)]
        require(schemas, "Missing page schema: " + html_name)
        page_node = schemas[0]
        data = published if data_name == "games.json" else development
        if html_name == "games.html":
            require(page_node == data, "Published HTML schema differs from its JSON catalog")
        if "@graph" in page_node:
            page_node = next(node for node in page_node["@graph"] if node.get("@type") == "CollectionPage")
        require(page_node["@id"] == canonical + "#page" and page_node["url"] == canonical
                and page_node["author"]["@id"] == PERSON,
                "Page/person identity mismatch: " + html_name)
        expected_list = games if html_name == "games.html" else development
        require(page_node["mainEntity"]["@id"] == expected_list["@id"], "Wrong page/catalog link: " + html_name)
        require(len(page.records) == count, "Visible record count mismatch: " + html_name)
        for visible, row in zip(page.records, expected_list["itemListElement"]):
            item = row["item"]
            require(item.get("creator", {}).get("@id") == PERSON, "Game/person identity drift: " + item["name"])
            aliases = [item["name"], *([item.get("alternateName")] if isinstance(item.get("alternateName"), str) else item.get("alternateName", []))]
            if item["name"] == "Happy Collector: Good Habits Adventure":
                aliases.append("Happy Collector")
            require(visible["title"] in aliases, "Visible game name drift: " + item["name"])
            sources = item.get("sameAs", [])
            if isinstance(sources, str):
                sources = [sources]
            for link in visible["links"]:
                require(link == item.get("url") or link in sources, "Visible game link drift: " + link)
            if "legocraft" in item.get("url", ""):
                require("experimental" in visible["description"] and "Meta Quest hardware testing is not yet complete" in visible["description"],
                        "Visible LegoCraft caption lost the experimental boundary")

    sitemap = (ROOT / "sitemap.xml").read_text()
    require("/v2/" not in sitemap, "Legacy URL in sitemap")
    for name in ("games.html", "games-development.html"):
        require(ORIGIN + "/" + name in sitemap, "Missing sitemap entry: " + name)
    for name, expected in outputs().items():
        require((ROOT / name).read_bytes() == expected, "Compatibility file drift: " + name)
    validate_legacy_identity()
    validate_redirect_scripts()
    print("Canonical game pages, catalogs, assets and ten legacy redirects are consistent.")


if __name__ == "__main__":
    main()
