"""Regression cases for the failures found during the held migration audit."""
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("publication_gate", ROOT / "scripts/wait_for_publication.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class MigrationChecks(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="signals-migration-test-")
        self.root = Path(self.folder.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def tearDown(self):
        self.folder.cleanup()

    def validate(self):
        return subprocess.run([sys.executable, "scripts/validate_v2_migration.py"],
                              cwd=self.root, capture_output=True, text=True)

    def sync(self):
        subprocess.run([sys.executable, "scripts/sync_v2_compatibility.py"],
                       cwd=self.root, check=True, capture_output=True)

    def rejected(self, expected):
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected, result.stderr)

    def test_current_migration_passes(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_development_game_id(self):
        path = self.root / "games-development.json"
        data = json.loads(path.read_text())
        data["itemListElement"][0]["item"].pop("@id")
        path.write_text(json.dumps(data))
        self.sync()
        self.rejected("Missing development game identity")

    def test_bad_development_anchor(self):
        path = self.root / "games-development.html"
        text = path.read_text().replace('id="development-bmx-xtreme"', 'id="development-wrong"', 1)
        path.write_text(text)
        self.rejected("Development anchor mismatch")

    def test_historical_page_identity_is_preserved(self):
        path = self.root / "games.json"
        data = json.loads(path.read_text())
        data["@graph"][0]["@id"] = "https://example.invalid/wrong#page"
        path.write_text(json.dumps(data))
        self.sync()
        self.rejected("Historical page identity drift")

    def test_retired_page_must_not_return(self):
        (self.root / "games.html").write_text("Obsolete catalog")
        self.rejected("Retired games.html must remain deleted")

    def test_wrong_current_collection_redirect(self):
        path = self.root / "vercel.json"
        data = json.loads(path.read_text())
        next(r for r in data["redirects"] if r["source"] == "/games.html")["destination"] = "/"
        path.write_text(json.dumps(data))
        self.rejected("Wrong redirect for /games.html")

    def test_historical_context_required(self):
        path = self.root / "games.json"
        data = json.loads(path.read_text())
        data["@graph"][0].pop("creativeWorkStatus")
        path.write_text(json.dumps(data))
        self.sync()
        self.rejected("Historical collection context missing")

    def test_broken_generator_loses_query_and_fragment(self):
        path = self.root / "scripts/sync_v2_compatibility.py"
        path.write_text(path.read_text().replace("destination.search = window.location.search;\n", "")
                        .replace("destination.hash = window.location.hash;\n", ""))
        self.sync()
        self.rejected("Redirect lost URL data")

    def test_automatic_static_fallback_is_rejected(self):
        path = self.root / "v2/index.html"
        path.write_text(path.read_text().replace("</head>", '<meta http-equiv="refresh" content="0;url=https://joe-nasr-signals.vercel.app/">\n</head>'))
        self.rejected("Compatibility file drift")

    def test_legacy_field_contract_survives_generation(self):
        path = self.root / "scripts/sync_v2_compatibility.py"
        path.write_text(path.read_text().replace('"canonical_name": person["public_name"],', '"missing_name": person["public_name"],'))
        self.sync()
        self.rejected("Missing legacy string field: canonical_name")

    def test_extra_broad_redirect_is_rejected(self):
        path = self.root / "vercel.json"
        data = json.loads(path.read_text())
        data["redirects"].insert(0, {"source": "/:path*", "destination": "/", "permanent": True})
        path.write_text(json.dumps(data))
        self.rejected("Unexpected redirect rule")


class Response:
    def __init__(self, body=b"", status=200, headers=None):
        self.body, self.status, self.headers = body, status, headers or {}

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class PublishedFiles:
    def __init__(self, stale=None, redirect_status=308, keep_query=True):
        self.stale, self.redirect_status, self.keep_query = stale, redirect_status, keep_query
        self.rules = {row["source"]: row["destination"] for row in json.loads((ROOT / "vercel.json").read_text())["redirects"]}

    def open(self, request, timeout):
        url = urlsplit(request.full_url)
        if url.path in self.rules:
            location = self.rules[url.path]
            if self.keep_query:
                location += "?" + url.query
            return Response(status=self.redirect_status, headers={"Location": location})
        name = url.path.lstrip("/")
        body = b"older deployment" if name == self.stale else (ROOT / name).read_bytes()
        return Response(body)


class PublicationChecks(unittest.TestCase):
    def test_ready_publication_passes(self):
        self.assertEqual(gate.check_once(opener=PublishedFiles()), [])

    def test_existing_key_does_not_allow_stale_game_catalog(self):
        failures = gate.check_once(opener=PublishedFiles(stale="games.json"))
        self.assertEqual(len(failures), 1)
        self.assertIn("games.json", failures[0])

    def test_temporary_redirect_is_not_ready(self):
        self.assertEqual(len(gate.check_once(opener=PublishedFiles(redirect_status=307))), len(PublishedFiles().rules))

    def test_lost_query_is_not_ready(self):
        self.assertEqual(len(gate.check_once(opener=PublishedFiles(keep_query=False))), len(PublishedFiles().rules))


if __name__ == "__main__":
    unittest.main()

