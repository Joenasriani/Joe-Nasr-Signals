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
    assert 'editorial_notability_status' not in identity['public_evidence_update_2026_10_04'], 'Internal editorial audit status in public identity'
    assert 'Independent-editorial status:' not in guide, 'Internal editorial audit status in machine guide'
    assert 'ReverbNation is historical in time but remains a high-value route' not in guide, 'Unavailable historical site promoted to active route'
    assert 'ReverbNation, @joenasrmusic' not in guide, 'Unavailable historical site promoted to active route'
    graph_match = re.search(r'<script type="application/ld[+]json">(.*?)</script>', html, re.S)
    assert graph_match, 'Missing homepage structured data'
    graph = json.loads(graph_match.group(1))['@graph']
    book_nodes = {node['url']: node for node in graph if node.get('@type') == 'Book'}
    for title, url in (
        ('Mamdani: From Zero to Hero', 'https://mamdani-from-zero-to-hero.vercel.app/'),
        ('Taxonomies and Classification Systems', 'https://reasoning-and-logic.vercel.app/taxonomies-and-classification-systems')
    ):
        node = book_nodes.get(url)
        assert node and title in node['name'] and node['author']['@id'] == ORIGIN + '#joe-nasr', 'Missing supported book schema: ' + title
    interactive = 'https://joe-nasr-interactive-projects.vercel.app/'
    assert not (root / 'games.html').exists(), 'Retired games.html must remain deleted'
    assert interactive in html and interactive in guide and interactive in json.dumps(identity), 'Missing current interactive collection'
    for path in ('games.json', 'games-development.json'):
        url = ORIGIN + path
        assert url in guide and url in json.dumps(identity), 'Missing direct catalog route: ' + path
    assert all(c['temporal_state'] == 'HISTORICAL' for c in identity['game_catalogs']), 'Historical catalog state missing'
    for phrase in ('verified profiles', 'Verified platform identifiers', 'Verified public handles', 'Verified public identifiers'):
        assert phrase not in html + guide, 'Ambiguous verification label'
    details = {}
    for name in registry['detail_files']:
        shard = read(urlsplit(name).path.lstrip('/'))
        assert shard['project_count'] == len(shard['projects']), 'Shard count mismatch'
        for record in shard['projects']:
            assert record['id'] not in details, 'Duplicate project ID'
            details[record['id']] = record
    assert registry['project_count'] == len(registry['projects']) == len(details) == identity['project_evidence_registry']['project_count'] == 51
    for item in registry['projects']:
        for field in ('name', 'aliases', 'evidence_class', 'public_retrieval_status', 'public_source_available'):
            assert item[field] == details[item['id']][field], 'Index/detail evidence mismatch: ' + item['id']
    publications = identity['related_entities']['reasoning_and_logic']['publications']
    assert len(publications) == 5, 'Bookstore publication identity count mismatch'
    required_books = {
        'SYN-PUB-20261012-001': ('Mamdani: From Zero to Hero', 'https://mamdani-from-zero-to-hero.vercel.app/', 'open'),
        'SYN-PUB-20261012-002': ('Taxonomies and Classification Systems', 'https://reasoning-and-logic.vercel.app/taxonomies-and-classification-systems', 'review')
    }
    for book_id, (title, url, sale_state) in required_books.items():
        entries = [p for p in publications if p['title'] == title]
        assert len(entries) == 1 and entries[0]['url'] == url and entries[0]['sales_status'] == sale_state, 'Publication source mismatch: ' + title
        detail = details[book_id]
        assert detail['name'] == title and url in detail['public_urls'], 'Publication evidence route mismatch: ' + title
        assert detail['public_retrieval_status'] == 'CONTEXT_ONLY_PUBLIC_PAGE_EXISTS_NOT_RECENTLY_REVERIFIED', 'Publication public verification overstated: ' + title
        assert title in guide and title in (root / 'README.md').read_text(), 'Publication missing from machine guide: ' + title
    public_bank = identity['client_relationship_bank_2026_10_04']
    assert not {'grouping_history', 'presentation_update', 'authority_note'} & public_bank.keys(), 'Private audit process exposed in public identity'
    assert 'ai_retrieval_update_2026_10_05' not in identity, 'Private audit process exposed in public identity'
    assert 'public_citation_boundary' in public_bank and 'VERIFIED_THIRD_PARTY_PRIVATE' in public_bank['public_citation_boundary'], 'Private provenance caveat missing'
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
    assert ORIGIN in {x.text for x in sitemap.findall('s:url/s:loc', ns)}
    assert not {ORIGIN+'games.html', ORIGIN+'games-development.html'} & {x.text for x in sitemap.findall('s:url/s:loc', ns)}, 'Retired collection in sitemap'
    # First-party machine links must resolve to files in the publication.
    for name in ['index.html', 'identity.json', 'llms.txt', 'projects.json', 'games-development.html']:
        text = (root / name).read_text()
        for url in re.findall(r'https://joe-nasr-signals\.vercel\.app/[^\s<>"\']*', text):
            path = urlsplit(url.rstrip('.,;:)')).path.lstrip('/') or 'index.html'
            assert not path.startswith('v2/'), 'Active discovery uses a legacy URL'
            assert (root / path).exists() or ('/' + path) in {r['source'] for r in json.loads((root / 'vercel.json').read_text())['redirects']}, 'Missing internal target: ' + path
    print('Direct discovery, 51 evidence records, historical snapshot and public boundaries pass.')


if __name__ == '__main__':
    validate()
