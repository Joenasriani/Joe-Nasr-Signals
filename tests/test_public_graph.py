"""Reject the public graph regressions found during source review."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublicGraphChecks(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name) / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def tearDown(self):
        self.folder.cleanup()

    def change_json(self, name, fn):
        path = self.root / name
        data = json.loads(path.read_text())
        fn(data)
        path.write_text(json.dumps(data))

    def check(self, error=None):
        result = subprocess.run([sys.executable, 'scripts/validate_public_graph.py'], cwd=self.root, capture_output=True, text=True)
        if error:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(error, result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_current_graph(self):
        self.check()

    def test_removed_editorial_audit_stays_private(self):
        self.change_json('identity.json', lambda d: d['public_evidence_update_2026_10_04'].update(editorial_notability_status='audit only'))
        self.check('Internal editorial audit status')

    def test_missing_mamdani_schema(self):
        path = self.root / 'index.html'
        path.write_text(path.read_text().replace('https://mamdani-from-zero-to-hero.vercel.app/', 'https://example.invalid/not-mamdani', 1))
        self.check('Missing supported book schema')

    def test_missing_publication_identity(self):
        self.change_json('identity.json', lambda d: d['related_entities']['reasoning_and_logic']['publications'].pop())
        self.check('Bookstore publication identity count mismatch')

    def test_bookstore_sales_status_drift(self):
        self.change_json('identity.json', lambda d: next(x for x in d['related_entities']['reasoning_and_logic']['publications'] if x['title'] == 'Taxonomies and Classification Systems').update(sales_status='open'))
        self.check('Publication source mismatch')

    def test_public_identity_audit_material(self):
        self.change_json('identity.json', lambda d: d['client_relationship_bank_2026_10_04'].update(grouping_history={'internal': 'private plan'}))
        self.check('Private audit process exposed')

    def test_private_provenance_caveat(self):
        self.change_json('identity.json', lambda d: d['client_relationship_bank_2026_10_04'].pop('public_citation_boundary'))
        self.check('Private provenance caveat missing')

    def test_wrong_shard_count(self):
        self.change_json('data/projects-01.json', lambda d: d.update(project_count=9))
        self.check('Shard count mismatch')

    def test_missing_catalog_discovery(self):
        path = self.root / 'llms.txt'
        path.write_text(path.read_text().replace('https://joe-nasr-signals.vercel.app/games.json', ''))
        self.check('Missing direct catalog route')

    def test_initial_html_drift(self):
        path = self.root / 'index.html'
        path.write_text(path.read_text().replace('class="record-number">01', 'class="record-number">99', 1))
        self.check('Initial archive differs')

    def test_public_audit_instruction(self):
        self.change_json('games/itchio/catalog.json', lambda d: d['items'][0].update(audit_state='pending_fix'))
        self.check('Private correction instructions')

    def test_private_repository_citation(self):
        self.change_json('data/projects-04.json', lambda d: next(r for r in d['projects'] if r['id']=='SYN-0278')['public_urls'].append('https://github.com/Joenasriani/visual-framework-system-app'))
        self.check('Private repository in public evidence')

    def test_evidence_upgrade_in_index(self):
        self.change_json('projects.json', lambda d: next(r for r in d['projects'] if r['id']=='SYN-0277').update(evidence_class='PUBLIC'))
        self.check('Index/detail evidence mismatch')

    def test_unavailable_history_not_active_route(self):
        self.change_json('identity.json', lambda d: d['query_routes']['guitar_music_composer']['surface_ids'].append('reverbnation'))
        self.check('AssertionError')


if __name__ == '__main__':
    unittest.main()
