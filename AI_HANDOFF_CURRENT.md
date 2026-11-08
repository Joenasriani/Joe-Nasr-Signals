# CURRENT AI HANDOFF – Joe Nasr Signals

**Status:** ACTIVE / SINGLE AUTHORITATIVE CONTINUATION HANDOFF  
**Reconciled:** 2026-11-08  
**Applies to:** `Joenasriani/Joe-Nasr-Signals`, default branch `main`  
**Canonical production:** https://joe-nasr-signals.vercel.app/  
**Purpose:** Website state, factual public identity, machine-readable evidence, maintenance and safe future continuation. **This is not a game-development repository.**

## Read this first – current authority and boundaries

1. This file is the single current AI/maintainer handoff. Read this, then `README.md`, `llms.txt`, `identity.json`, `projects.json` and relevant page data before changing anything. Do not treat the historical archive as active instructions.
2. **NO UNAUTHORIZED CHANGES TO SIGNALS:** Never edit, deploy or touch the canonical Signals project or this repository without specific instruction from Joe **and confirmation**. The November 8, 2026 publications/continuity work was separately authorized; that is **not standing permission** for future changes. New add-on banks/registers/collections must remain external and may link to Signals as an outside reference.
3. Do not redesign or change layout, UI, existing workflows or other sections while fixing documentation. Commit the smallest changes and recheck saved files and public state.
4. ONEJOE: Joe Nasr = Joseph Ribal Nasr, with historical/public branch-specific identities. Preserve legitimate differences between professional, music, creator and research surfaces. Resolve namesakes using evidence. Do not merge people based on matching names.
5. Evidence precedence: each primary publication/deposit or first-party external source establishes only its documented claim; the separate research registry records DOI metadata and dated verification. The Signals hub defines the canonical current identity, but is not independent corroboration of every professional credit.
6. Never expose private instructions, chats, credentials, unapproved private addresses or operational records in public files.

## Current website and machine-data layout

| Purpose | Active repository location | Public route |
| --- | --- | --- |
| Canonical identity / work archive | `index.html` | `/` |
| Person/relationship evidence | `identity.json` | `/identity.json` |
| Project evidence index | `projects.json`, `data/projects-01.json` through `data/projects-05.json` | `/projects.json` and `/data/` |
| Publications | `publications/index.html` | `/publications/` |
| Certifications | `certifications/` | `/certifications/` |
| Interactive experiences | `interactive-projects/` | `/interactive-projects/` |
| Video campaigns | `video-campaigns/` | `/video-campaigns/` |
| Music | `music/` | `/music/` |
| Training/workshops/lectures | `training-workshops-lectures/` | `/training-workshops-lectures/` |
| Tools and technologies | `tools-technologies/` | `/tools-technologies/` |
| Games/development history | `games.json`, `games-development.json`, `games/itchio/` | corresponding root/catalogue routes |
| AI retrieval / crawling | `llms.txt`, `sitemap.xml`, `robots.txt` | corresponding root routes |
| Release guards | `scripts/`, `tests/`, `.github/workflows/`, `vercel.json` | source-only |

The site has a canonical root identity and integrated subject libraries. **Do not replace their design or merge the separate external site sources into this repository without fresh authorization.**

## Reconciled publication state – 2026-11-08

Authoritative DOI/record library: https://github.com/Joenasriani/joe-research-registry and https://github.com/Joenasriani/joe-research-registry/blob/main/registry.json. This is README-first research evidence, **not a live GitHub Pages website**.

Six distinct Zenodo DOI works; publication type follows recorded official Zenodo API checks dated **2026-11-06**:

| Work | Type | Version DOI |
| --- | --- | --- |
| The Composer's Prompt | Book | 10.5281/zenodo.23689714 |
| Tongue as Trackpad | Report | 10.5281/zenodo.23622202 |
| MPI-AIR | Working paper | 10.5281/zenodo.23592679 |
| Quest-MFTS | Report | 10.5281/zenodo.23552640 |
| Quest-XSA | Report | 10.5281/zenodo.23538919 |
| ICF-AI | Preprint | 10.5281/zenodo.23504055 |

- The Composer's Prompt has a longer descriptive subtitle; the current Zenodo title is the short form. Concept DOI `10.5281/zenodo.23689713` is the same book across versions, **not a seventh work**.
- ResearchGate book/full-text listing: https://www.researchgate.net/publication/417607181_The_Composer%27s_Prompt_Music_Theory_and_Harmony_for_Computational_Music_Prompting – separate distribution of the **same book**, recorded verified 2026-11-07; no independent PDF checksum verification.
- Harvard Dataverse companion dataset: https://doi.org/10.7910/DVN/STHUVV – **separate published dataset**, version 1.1 RELEASED 2026-11-04 and API checked 2026-11-06. Separate old book record `10.7910/DVN/ZCZ0NA` public state **UNKNOWN**, do not assert publication/deletion.
- ORCID: https://orcid.org/0009-0004-5698-9097 – six unique DOI works reported in public API, with a duplicate ICF-AI ORCID entry requiring put-code investigation before any user-authorized cleanup.
- Google Scholar: https://scholar.google.com/citations?user=V_8fZGQAAAAJ – twelve entries previously observed, current live indexing not independently rechecked.
- Production Publications nav order: **ORCID | Zenodo | Google Scholar | ResearchGate | Harvard Dataverse**.
- The HTML page, JSON-LD, README, research section in identity.json, `llms.txt`, and sitemap were reconciled on 2026-11-08. Date-scoped verification claims do **not** mean experiments were validated or publications peer-reviewed.

## Other counts and relationships – do not conflate

- **67** interactive-project showcase entries; **68** machine-readable interactive collection records, including the distinct non-showcase RoboSim/RoboWebSim-related record. **51** separate projects in the broader evidence graph. Different granularity, not conflict.
- Historical game evidence and the separate 20-record development inventory remain valid as archives, not instructions to restore retired game pages.
- Current professional framing: `Creative Director | Digital Experiences | Interactive Prototyping`. Other surface descriptions such as composer or lecturer can be correct within context.
- Historical account status/identity relationships must preserve provenance and time; do not equate historical with obsolete or delete for cosmetic simplification.
- Avoid inflation: a distribution copy is not a new DOI work; a dataset is not another Zenodo publication; a company, project, book or game is not a `Person.sameAs` identity.

## Release and validation procedure

1. Read current `main` files and compare with any proposed source of truth; log **BEFORE → ACTION → AFTER → VERIFICATION**.
2. Verify exact scope and user authorization. Prefer one file/claim per edit, archive obsolete instructions rather than leaving them active.
3. Check JSON parsing, JSON-LD, project-index vs shards, visible vs structured record counts, exact DOI/title/type/version pairings, live internal links and canonical URLs. The repository's existing commands include:
   - `python scripts/sync_archive.py --check`
   - `python scripts/validate_signals.py`
   - `python scripts/validate_public_graph.py`
   - `python scripts/validate_training_audiences.py`
   - `python -m unittest discover -s tests -v`
4. Inspect Github Actions under `.github/workflows/`, especially validations. Validate the production Vercel deployment and its `githubCommitSha` against the actual intended release commit and target `production`. A READY deployment alone does not establish UI parity, full link health, indexing, AI citation or test success.
5. Reopen the committed file, check every changed pointer, and distinguish `COMMITTED`, `DEPLOYED_READY`, `PUBLIC_RECHECKED`, `VERIFIED` and `NOT_RECHECKED`. Do not close an issue merely because the edit was saved.
6. Never promote the ResearchGate book distribution to another work, an unresolved Dataverse record to published, or an evidence source to independent verification of unproven claims.

## Historical archives and avoided errors

- **Only historical reconciliation guidance:** [docs/archive/RECONCILIATION_HISTORY_2026-11-08.md](docs/archive/RECONCILIATION_HISTORY_2026-11-08.md).
- Retired GitHub Pages research routes belong to the historical archive, not navigation, README current routing or `identity.json`.
- No earlier `AI_HANDOFF_*.md` files were present in the audited `main` tree when this handoff was established; do not create competing current handoffs.
- Do not change the canonical root website or subject libraries on your own initiative. External research banks are separate sources and link back only as intended.

## Scope and verification notes for this reconciliation

The tree-level inventory and high-value source documents were inspected, with identified stale publication links and type conflicts repaired. GitHub source-file rechecks and production commit verification are required after the last handoff commit. Complete external third-party link checking, independent Zenodo/Dataverse/ResearchGate API re-verification, and comprehensive test-suite execution are **not implied** by this handoff. Report any outstanding checks honestly rather than converting them to `VERIFIED`.

The most reliable continuation starts here, then follows `README.md` and individual source-of-truth files; archived material is evidence, not instruction.
