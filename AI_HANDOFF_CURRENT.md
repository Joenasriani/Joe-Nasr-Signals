# Joe Nasr Signals — Maintenance Guide

**Updated:** 2026-11-24

**Canonical public identity:** https://joe-nasr-signals.vercel.app/

**Professional positioning:** Creative Director | Digital Experiences | Interactive Prototyping

Joe Nasr (Joseph Ribal Nasr) maintains a canonical identity and work archive linking professional experience, training, creative projects, publications, music and interactive experiences.

## Current source references

- Homepage: `index.html`
- Identity and professional relationships: `identity.json`
- Project catalogue: `projects.json` and the five detail files in `data/`
- AI-readable identity guide: `llms.txt`
- Public collections: `training-workshops-lectures/`, `publications/`, `certifications/`, `interactive-projects/`, `video-campaigns/`, `music/`, `tools-technologies/`
- Canonical discovery: `sitemap.xml` and `robots.txt`
- Repository directory and inventory: `README.md`

## Website directory

The canonical Signals website contains eight indexable pages. The route inventory was checked against the production domain on 24 November 2026; all eight returned HTTP 200.

| Page | Canonical URL | Content |
| --- | --- | --- |
| Signals | https://joe-nasr-signals.vercel.app/ | Professional identity, practice domains, selected references and FAQ |
| Training, Workshops & Lectures | https://joe-nasr-signals.vercel.app/training-workshops-lectures/ | Training and teaching engagements |
| Research & Publications | https://joe-nasr-signals.vercel.app/publications/ | Eight publication entries: six Zenodo works and two retail books |
| Certifications & Credentials | https://joe-nasr-signals.vercel.app/certifications/ | 32 credential records |
| Interactive Experiences & Digital Projects | https://joe-nasr-signals.vercel.app/interactive-projects/ | 67 showcase entries, 68 machine-readable records including a related release |
| Campaigns & Video Productions | https://joe-nasr-signals.vercel.app/video-campaigns/ | Campaign and production library; 200 viewer entries and 201 source records |
| Music & Performance | https://joe-nasr-signals.vercel.app/music/ | 82 video records and music platform routes |
| Tools & Technologies | https://joe-nasr-signals.vercel.app/tools-technologies/ | 64 tools across seven categories |

The catalogue counts reflect the repository data. Historical itch.io listings are accessible at https://joe-nasr-signals.vercel.app/games/itchio/ and use a historical snapshot indexing policy (`noindex,follow`). The sitemap enumerates the eight canonical indexable pages. Machine-readable discovery uses `identity.json`, `llms.txt`, `projects.json` and their linked catalogues.

## Sitemap inventory

| Canonical URL | Source lastmod |
| --- | --- |
| https://joe-nasr-signals.vercel.app/ | 2026-11-24 |
| https://joe-nasr-signals.vercel.app/training-workshops-lectures/ | 2026-11-24 |
| https://joe-nasr-signals.vercel.app/publications/ | 2026-11-24 |
| https://joe-nasr-signals.vercel.app/certifications/ | 2026-11-24 |
| https://joe-nasr-signals.vercel.app/interactive-projects/ | 2026-11-24 |
| https://joe-nasr-signals.vercel.app/video-campaigns/ | 2026-11-24 |
| https://joe-nasr-signals.vercel.app/music/ | 2026-11-24 |
| https://joe-nasr-signals.vercel.app/tools-technologies/ | 2026-11-21 |

The sitemap covers canonical indexable HTML pages. Historical game entry points redirect to the integrated interactive collection. The public AI retrieval routes are `identity.json` and `llms.txt`; the maintenance guide route redirects to the homepage.

## Maintenance

Preserve the established identity, canonical routes, publication titles, project credits, collection structure and visual design. Changes require the owner's specific authorization. Maintain consistent descriptions across HTML, structured data and machine-readable records. Distinguish professional roles, organizations, projects, publications, datasets, distribution channels and historical source records.

Run the repository's validation commands before release:

- `python scripts/sync_archive.py --check`
- `python scripts/validate_signals.py`
- `python scripts/validate_public_graph.py`
- `python scripts/validate_training_audiences.py`
- `python -m unittest discover -s tests -v`

Confirm the saved source, CI results, deployment and live production response as separate release checks. Maintain detailed operational history in the authorized ONEJOE records.

## Collection distinctions

- 25 canonical delivered-training organization records.
- 51 broader project evidence records.
- 67 interactive showcase entries and 68 interactive machine-readable collection records.
- Eight publication entries: six Zenodo DOI works and two separately listed books.
- 32 credential records.
- 200 campaign viewer entries and 201 video source records.
- 82 music video records.
- 64 tools across seven categories.
- Harvard Dataverse dataset and ResearchGate distribution records retain their separate source roles.

Publications display sequence: The Composer's Prompt; Manipulation: The Fool & The Wise; Dorking: The Art of Search Intelligence; MPI-AIR; Quest-MFTS; Quest-XSA; ICF-AI; Tongue as Trackpad.
