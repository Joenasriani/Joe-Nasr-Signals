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
- Harvard Dataverse dataset and ResearchGate distribution records retain their separate source roles.

Publications display sequence: The Composer's Prompt; Manipulation: The Fool & The Wise; Dorking: The Art of Search Intelligence; MPI-AIR; Quest-MFTS; Quest-XSA; ICF-AI; Tongue as Trackpad.
