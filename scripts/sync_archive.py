"""Keep the initial archive HTML aligned with the interactive record source."""
import argparse
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def array(html, name):
    match = re.search(r'\bconst\s+' + name + r'\s*=\s*', html)
    return json.JSONDecoder().raw_decode(html[match.end():])[0]


def render(html):
    records = array(html, 'records')
    categories = array(html, 'categories')[1:]
    rows = []
    number = 0
    for category in categories:
        group = [(i, r) for i, r in enumerate(records) if r['category'] == category]
        if not group:
            continue
        label = escape(category)
        rows.append(f'        <div class="archive-group-label" data-archive-group="{label}"><strong>{label}</strong></div>')
        for i, record in group:
            number += 1
            title, description, url, source, status = [escape(record[k], quote=True) for k in ('title', 'description', 'url', 'source', 'status')]
            status_html = '' if status == 'Official' else f'<span class="record-status" data-status="{status}">{status}</span>'
            rows.append(f'''        <article class="archive-record" id="signal-{i+1:03d}">
          <div class="record-number">{number:02d}</div>
          <div class="record-main">
            <div class="record-topline">{status_html}</div>
            <h3 class="record-title">{title}</h3>
            <p class="record-description">{description}</p>
            <div class="record-url-wrap"><a class="record-url" href="{url}" target="_blank" rel="noopener noreferrer">{url}</a></div>
          </div>
          <div class="record-source"><span>SOURCE</span><strong>{source}</strong></div>
          <div class="record-actions"><button class="copy-button" type="button" aria-label="Copy direct URL" data-url="{url}">Copy URL</button><a class="open-button" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="Open {title} on {source}">Open ↗</a></div>
        </article>''')
    pattern = r'(<div class="archive-list" id="archiveList">\n).*?(\n      </div>\n      <div class="empty-state")'
    result, count = re.subn(pattern, lambda m: m[1] + '\n'.join(rows) + m[2], html, flags=re.S)
    if count != 1:
        raise ValueError('Expected one initial archive container')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'index.html'
    current = path.read_text()
    expected = render(current)
    if args.check and current != expected:
        raise SystemExit('Initial archive HTML differs from the interactive records')
    if not args.check:
        path.write_text(expected)
    print('Initial archive and interactive records are aligned.')
