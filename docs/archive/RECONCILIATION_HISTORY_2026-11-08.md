# Historical reconciliation record – 2026-11-08

**ARCHIVED / SUPERSEDED GUIDANCE – NOT ACTIVE INSTRUCTIONS**

This is a historical provenance record. It must not be used as the current AI handoff, a live website route, a deployment instruction, or authorization for changing Signals. The only current continuation handoff is [AI_HANDOFF_CURRENT.md](../../AI_HANDOFF_CURRENT.md). The canonical identity hub is https://joe-nasr-signals.vercel.app/ .

## BEFORE → ACTION → AFTER

1. **Research registry routing**
   - BEFORE: `README.md` and `identity.json` directed users and machines to `https://joenasriani.github.io/joe-research-registry/`.
   - BEFORE: `README.md` also linked to `https://joenasriani.github.io/joe-research-registry/quest-research.html`.
   - WHY SUPERSEDED: The current `Joenasriani/joe-research-registry` repository is explicitly README-first; the legacy HTML site was archived on the research repository's historical branch and is not the current library.
   - ACTION: Replaced active references with `https://github.com/Joenasriani/joe-research-registry`, `registry.json`, and the Signals Publications page. Original URLs are retained **here solely for historical identification**.
   - AFTER: The live source repository and its relationship to the integrated Publications page are explicit. Do not restore the retired links to active routing.

2. **DOI publication types and verification**
   - BEFORE: `identity.json` described the five non-book Zenodo entries with a generic `ScholarlyArticle` publication type and described their DOI verification as pending. The book's descriptive subtitle appeared as its full title.
   - ACTION: Reconciled with the research registry's dated Zenodo API checks (2026-11-06): **one Book**, **three Reports**, **one Working paper**, **one Preprint**. Book title is `The Composer’s Prompt`; the longer phrase is a descriptive subtitle, not another book.
   - AFTER: Six works and six version DOIs remain; concept DOI `10.5281/zenodo.23689713` is an all-versions identifier for the same book and is not a seventh publication.
   - CAVEAT: These are dated recorded source checks; this maintenance does not independently verify scientific claims, peer review, institutional affiliation, or PDF-byte identity.

3. **ResearchGate and Harvard Dataverse**
   - BEFORE: Distribution and dataset links were absent from the integrated publication machine graph and visible navigation.
   - ACTION: Signals Publications links the ResearchGate record of the **same** Composer's Prompt book (registry verification 2026-11-07), and the separately published Harvard Dataverse companion dataset `10.7910/DVN/STHUVV` (version 1.1 released 2026-11-04 and API checked 2026-11-06).
   - AFTER: Both are represented without inflating the six Zenodo works. Separate historical Dataverse book record `10.7910/DVN/ZCZ0NA` remains unresolved and is not claimed published.

4. **AI/readability and indexing**
   - BEFORE: `llms.txt` referenced the retired GitHub Pages registry route. Publications sitemap metadata preceded the 2026-11-08 content corrections.
   - ACTION: Updated `llms.txt` to cite the correct registry and dated evidence; updated `sitemap.xml` and Publications JSON-LD modification date to 2026-11-08.
   - AFTER: Keep source, AI guide, schema and sitemap aligned. Indexing/ranking or AI citation changes are **not** presumed from publication alone.

## Historical evidence, not removal instructions

- The integrated Interactive Projects collection retains **67 visible showcase entries**, **68 structured collection records** including one non-showcase related release, and an independent **51-entry** project-evidence registry. Different counts reflect different grains and must not be “deduplicated” without evidence.
- Older actual credits, music identities, game releases, and public references remain legitimate history. `HISTORICAL` does not mean incorrect, weak, or deletable.
- The public site is the identity/evidence hub. The external subject libraries remain distinct alternatives, and the research registry is a separate README-first DOI source.
- Do not restore old instructions solely because they are preserved here.

## Verification boundaries

Previous publication work received GitHub commit and Vercel READY verification. Later document updates require fresh saved-source verification and production-state checks. The deployment's READY state does not prove external links resolve, search engines have indexed content, or complete test suites have passed.

**Current handoff:** [AI_HANDOFF_CURRENT.md](../../AI_HANDOFF_CURRENT.md).
