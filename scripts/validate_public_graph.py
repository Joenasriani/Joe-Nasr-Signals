"""Validate direct discovery, evidence projections and publication boundaries."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from sync_archive import render

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://joe-nasr-signals.vercel.app/'


def validate(root=ROOT):
    read = lambda name: json.loads((root / name).read_text())
    html = (root / 'index.html').read_text()
    identity = read('identity.json')
    registry = read('projects.json')
    guide = (root / 'llms.txt').read_text()
    assert html == render(html), 'Initial archive differs from interactive records'
    assert 'aria-label="Search work, role or discipline"' in html, 'Search accessible label missing'
    for path in ('games.html', 'games-development.html', 'games.json', 'games-development.json'):
        url = ORIGIN + path
        assert url in html and url in guide and url in json.dumps(identity), 'Missing direct catalog route: ' + path
    for phrase in ('verified profiles', 'Verified platform identifiers', 'Verified public handles', 'Verified public identifiers'):
        assert phrase not in html + guide, 'Ambiguous verification label'
    details = {}
    for name in registry['detail_files']:
        shard = read(urlsplit(name).path.lstrip('/'))
        assert shard['project_count'] == len(shard['projects']), 'Shard count mismatch'
        for record in shard['projects']:
            assert record['id'] not in details, 'Duplicate project ID'
            details[record['id']] = record
    assert registry['project_count'] == len(registry['projects']) == len(details) == 49
    for item in registry['projects']:
        for field in ('name', 'aliases', 'evidence_class', 'public_retrieval_status', 'public_source_available'):
            assert item[field] == details[item['id']][field], 'Index/detail evidence mismatch: ' + item['id']
    assert not details['SYN-0277']['public_source_available'], 'Unpublished artifact claimed public'
    assert details['SYN-0277']['evidence_class'] == 'DOCUMENTED_NONPUBLIC'
    assert not details['SYN-0277']['public_urls'], 'Unpublished artifact has public evidence URL'
    private = {'structure-of-life-book', 'manipulation-book', 'icf-ai', 'visual-framework-system-app', 'roundtable_ai'}
    for record in details.values():
        for url in record['public_urls']:
            assert url not in {'https://github.com/Joenasriani/' + name for name in private}, 'Private repository in public evidence'
    native = read('games/itchio/catalog.json')
    assert native['count'] == len(native['items']) == 27
    assert native['snapshot_date'] == '2026-09-22'
    native_text = json.dumps(native) + (root / 'games/itchio/index.html').read_text()
    for text in ('audit_state', 'pending_fix', 'Correct the native', 'Working native-platform audit'):
        assert text not in native_text, 'Private correction instructions in public snapshot'
    assert 'HISTORICAL_NATIVE_PLATFORM_SNAPSHOT' in native_text
    assert 'not an independently published credit' in html
    assert 'evidence_boundary' in identity['selected_historical_work'][0]
    surface = next(s for s in identity['public_surface_registry'] if s['id'] == 'reverbnation')
    assert surface['temporal_state'] == 'HISTORICAL' and surface['retrieval_state'] == 'UNRESOLVED'
    assert 'reverbnation' not in identity['query_routes']['guitar_music_composer']['surface_ids']
    sitemap = ET.fromstring((root / 'sitemap.xml').read_text())
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    assert {ORIGIN, ORIGIN+'games.html', ORIGIN+'games-development.html'} <= {x.text for x in sitemap.findall('s:url/s:loc', ns)}
    # First-party machine links must resolve to files in the publication.
    for name in ['index.html', 'identity.json', 'llms.txt', 'projects.json', 'games.html', 'games-development.html']:
        text = (root / name).read_text()
        for url in re.findall(r'https://joe-nasr-signals\.vercel\.app/[^\s<>"\']*', text):
            path = urlsplit(url.rstrip('.,;:)')).path.lstrip('/') or 'index.html'
            assert not path.startswith('v2/'), 'Active discovery uses a legacy URL'
            assert (root / path).exists(), 'Missing internal target: ' + path
    print('Direct discovery, 49 evidence records, historical snapshot and public boundaries pass.')


if __name__ == '__main__':
    validate()
