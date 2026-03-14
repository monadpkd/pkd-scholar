# pkd-scholar — Project Context

## What This Is
AI-assisted scholarly workbench for studying Philip K. Dick's fiction corpus.
Built on patterns from [QueryPat](https://github.com/t3dy/QueryPat) (Ted Hand's Exegesis knowledge graph).

## Collaborators
- **Paul Shelton** (monadpkd) — filmmaker, PKD archive builder, Claude Code user
- **Ted Hand** — PKD scholar, built QueryPat, designed the analytical framework

## Architecture
Three-lane evidence pipeline with synthesis layer:
- **Lane A:** Primary fiction (novels, stories, Exegesis, interviews, essays)
- **Lane B:** Contextual sources (Jung, Freud, Laing, anti-psychiatry, split-brain lit, etc.)
- **Lane C:** Secondary scholarship (biographies, criticism, academic articles)
- **Lane D:** Synthesis/dictionary layer — all claims traceable to A, B, or C

## Two Study Lenses (same pipeline, different topic families)
1. **AI/Robot/Capitalism Study** — machine authority, spurious reality, automation, turnstile motif
2. **Psychology Study** — paranoia, schizophrenia, empathy, identity, Jungian archetypes, anti-psychiatry

## Pipeline Stages
0. Corpus intake (PDF extraction, metadata, stable IDs)
1. Segmentation (chapter/scene for fiction, date-block for Exegesis, section for criticism)
2. Vocabulary bootstrapping (controlled terms + aliases)
3. Candidate detection (deterministic regex + LLM classification)
4. Passage classification (source_mode, psych_mode/ai_mode, claim_type, confidence)
5. Evidence packet generation (per-topic, multi-lane, with contradiction lists)
6. Entry drafting (rigid template, evidentiary layers separated in prose)
7. Review and adjudication (human gates for false positives, over-psychologizing, fair use)
8. Export and linking (JSON for site, SQLite for dashboards)

## Tech Stack
- **Python** — pipeline scripts, SQLite, PyMuPDF
- **SQLite** — primary data store
- **React 19 + TypeScript + Vite** — static site (same as QueryPat)
- **GitHub Pages** — deployment

## Key Rules
1. Never collapse fiction motifs into claims about Dick's actual beliefs
2. Keep evidentiary lanes separate: "In the fiction..." / "In the Exegesis..." / "In criticism..."
3. Do not diagnose Dick — describe represented states, self-descriptions, interpretive debates
4. Fair use: paraphrase over quotation, brief quotes only when analytically necessary
5. Every claim traceable to page/chunk in a specific source
6. Contradictions are features, not bugs — preserve tension between incompatible explanations
7. College-level prose: clear, analytical, evidence-based, no hype

## Folder Structure
```
database/           — SQLite schema + reference CSVs
scripts/            — Python pipeline (ingest, discover, classify, evidence, draft, link, enrich, export)
vocabulary/         — Controlled vocabularies (AI terms, psychology terms, machine roles)
  prompt_templates/ — LLM prompts for each pipeline stage
guides/             — Fair use guide, writing style guide, entry structure
site/               — React + Vite static site
```

## Upstream
- QueryPat patterns: discovery pipeline, matchers, scoring, export, site architecture
- PKDCatalog: document catalog data
- ExegesisSummaries: Exegesis segment data

## IDs
Follows pkd-archive unified namespace: `PKD-{TYPE}-{DATE}-{MNEMONIC}`
- `PKD-WRK-1969-UBIK` — works (novels, stories, essays)
- `PKD-SEG-UBIK-CH03` — segments (chapters, scenes, date-blocks)
- `PKD-PSY-PARANOIA` — psychology topics
- `PKD-AIT-ECONGATEKEEPER` — AI/automation topics
- `PKD-ENT-PARANOIA` — dictionary entries
- `PKD-EVP-PARANOIA-001` — evidence packets
- `PKD-CLM-PARANOIA-UBIK-001` — traceable claims
- `PKD-SRC-1989-SUTIN` — secondary sources
- `PKD-PER-JUNG` — persons (real)
- `PKD-CHR-DECKARD` — characters (fictional)
- `PKD-SCH-JUNGIAN` — schools of thought

IDs are permanent. Never reused, never changed, never deleted.
See pkd-archive `_schema/pkd_id_namespace.json` for full spec.

## Canonical Data Sources (pkd-archive)
Psychology topics list: `monadpkd/pkd-archive` → `psychology/pkd_psychology_topics.json` (158 topics, 7 families)
Psychology schema: `monadpkd/pkd-archive` → `psychology/pkd_psychology_schema.json`
Psychology seed entries: `monadpkd/pkd-archive` → `psychology/pkd_psychology_master.json` (20 stubs)
ID namespace: `monadpkd/pkd-archive` → `_schema/pkd_id_namespace.json`
Controlled vocabularies: `monadpkd/pkd-archive` → `_schema/controlled_vocabularies.json`

DO NOT duplicate psychology topic lists here. Pull from pkd-archive.
