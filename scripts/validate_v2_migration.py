"""Validate canonical game URLs and legacy compatibility without changing files."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse

from sync_v2_compatibility import outputs

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://joe-nasr-signals.vercel.app"
PERSON = ORIGIN + "/#joe-nasr"
FILES = ["games.html", "games-development.html", "games.json", "games-development.json",
         "games-preview.png", "games-preview.svg"]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = []
        self.alternate = []
        self.meta = {}
        self.links = []
        self.heading_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
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


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    for name in FILES:
        require((ROOT / name).is_file(), "Missing canonical file: " + name)
        if not name.endswith(".png"):
            require("/v2/" not in (ROOT / name).read_text(), "Legacy URL in canonical file: " + name)

    config = json.loads((ROOT / "vercel.json").read_text())
    required = {"/v2": "/", "/v2/": "/", "/v2/index.html": "/",
                "/v2/identity.json": "/identity.json"}
    required.update({"/v2/" + name: "/" + name for name in FILES})
    for old, new in required.items():
        rules = [rule for rule in config["redirects"] if rule["source"] == old]
        require(len(rules) == 1, "Expected one redirect for " + old)
        require(rules[0]["destination"] == new and rules[0].get("permanent") is True,
                "Wrong redirect for " + old)

    published = json.loads((ROOT / "games.json").read_text())
    games = next(node for node in published["@graph"] if node.get("@type") == "ItemList")
    require(games["numberOfItems"] == len(games["itemListElement"]), "Published game count mismatch")
    development = json.loads((ROOT / "games-development.json").read_text())
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
        for key in ("og:image", "twitter:image"):
            require(page.meta.get(key) == ORIGIN + "/games-preview.png", "Incorrect image: " + html_name)
        for link in page.links:
            target = urlparse(urljoin(canonical, link))
            if target.netloc == urlparse(ORIGIN).netloc:
                path = target.path.lstrip("/") or "index.html"
                require((ROOT / path).is_file(), "Missing local link: " + link)
        schemas = [json.loads(block) for block in re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.S)]
        require(schemas, "Missing page schema: " + html_name)
        page_node = schemas[0]
        if "@graph" in page_node:
            page_node = next(node for node in page_node["@graph"] if node.get("@type") == "CollectionPage")
        require(page_node["url"] == canonical and page_node["author"]["@id"] == PERSON,
                "Page/person identity mismatch: " + html_name)

    sitemap = (ROOT / "sitemap.xml").read_text()
    require("/v2/" not in sitemap, "Legacy URL in sitemap")
    for name in ("games.html", "games-development.html"):
        require(ORIGIN + "/" + name in sitemap, "Missing sitemap entry: " + name)
    for name, expected in outputs().items():
        require((ROOT / name).read_bytes() == expected, "Compatibility file drift: " + name)
    print("Canonical game pages, catalogs, assets and ten legacy redirects are consistent.")


if __name__ == "__main__":
    main()
