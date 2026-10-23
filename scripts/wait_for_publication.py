"""Wait for the checked-out public files and permanent routes before indexing."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import build_opener, HTTPRedirectHandler, Request

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://joe-nasr-signals.vercel.app"
PUBLIC_FILES = ["index.html", "publications/index.html", "certifications/index.html", "interactive-projects/index.html", "video-campaigns/index.html", "music/index.html", "identity.json", "projects.json", "llms.txt", "sitemap.xml", "robots.txt", "games/itchio/index.html", "games/itchio/catalog.json",
                "games.json", "games-development.json",
                "games-preview.png", "games-preview.svg", "games-development-preview.png",
                "games-development-preview.svg", "pre-institutional-human-order.html",
                "4f2a8c9d71b64e35a0f3c8d92e7b1a56.txt"]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def check_once(root=ROOT, origin=ORIGIN, opener=None):
    opener = opener or build_opener(NoRedirect())
    failures = []
    files = PUBLIC_FILES + [str(path.relative_to(root)) for path in sorted((root / "data").glob("projects-*.json"))]
    for name in files:
        expected = (root / name).read_bytes()
        digest = hashlib.sha256(expected).hexdigest()
        url = origin + "/" + name + "?publication_check=" + digest
        try:
            with opener.open(Request(url, headers={"Accept-Encoding": "identity"}), timeout=15) as response:
                if response.status != 200 or response.read() != expected:
                    failures.append(name + ": deployed bytes do not match this checkout")
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            failures.append(name + ": " + str(error))
    for rule in json.loads((root / "vercel.json").read_text())["redirects"]:
        query = "?publication_check=1&value=a%2Bb"
        url = origin + rule["source"] + query
        try:
            with opener.open(Request(url), timeout=15) as response:
                status, location = response.status, response.headers.get("Location", "")
        except HTTPError as error:
            status, location = error.code, error.headers.get("Location", "")
        except (URLError, TimeoutError, OSError) as error:
            failures.append(rule["source"] + ": " + str(error))
            continue
        if status != 308 or urljoin(url, location) != urljoin(origin + "/", rule["destination"]) + query:
            failures.append(rule["source"] + ": permanent target or query preservation is not ready")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--interval", type=float, default=10)
    args = parser.parse_args()
    if args.timeout < 0 or args.interval <= 0:
        parser.error("timeout must be nonnegative and interval must be positive")
    deadline = time.monotonic() + args.timeout
    while True:
        failures = check_once()
        if not failures:
            print("Public files match this checkout; all configured permanent routes preserve query strings.")
            return
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SystemExit("Publication is not ready; IndexNow must not run. " + "; ".join(failures[:5]))
        print("Publication pending: " + "; ".join(failures[:3]), flush=True)
        time.sleep(min(args.interval, remaining))


if __name__ == "__main__":
    main()
