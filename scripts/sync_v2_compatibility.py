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
    "v2/identity.json": "identity.json",
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
<meta http-equiv="refresh" content="0;url={escape(destination, quote=True)}">
</head>
<body>
<p><a href="{escape(destination, quote=True)}">Continue to {escape(title)}</a></p>
</body>
</html>
'''.encode()


def outputs():
    expected = {old: redirect_page(path, title) for old, (path, title) in HTML_ROUTES.items()}
    expected.update({old: (ROOT / current).read_bytes() for old, current in COPIES.items()})
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
