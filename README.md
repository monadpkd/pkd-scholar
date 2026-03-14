# pkd-scholar

AI-assisted scholarly workbench for studying Philip K. Dick's fiction — thematic analysis pipeline with multi-lane evidence architecture.

## What This Is

A research production system that takes PKD's novels, stories, and the Exegesis as PDFs, runs them through a deterministic + LLM-assisted pipeline, and produces structured scholarly entries suitable for a web viewer, database, or research portal.

Built on patterns from [QueryPat](https://github.com/t3dy/QueryPat) (Ted Hand's PKD Exegesis knowledge graph). Uses the [pkd-archive](https://github.com/monadpkd/pkd-archive) ID namespace and controlled vocabularies.

## Two Study Lenses

1. **AI, Robots & Capitalism** — machine authority, spurious reality, automation, the "turnstile" motif
2. **Psychology** — paranoia, schizophrenia, empathy, Jungian archetypes, anti-psychiatry, dream states

Both lenses share the same pipeline and three-lane evidence architecture.

## Three-Lane Evidence Architecture

Every claim is traceable to one of three evidentiary lanes:

- **Lane A** — Primary fiction: novels, stories, Exegesis, interviews, essays
- **Lane B** — Contextual sources: Jung, Freud, Laing, split-brain lit, cybernetics
- **Lane C** — Secondary scholarship: biographies, criticism, academic articles
- **Lane D** — Synthesis layer: dictionary entries with visible provenance

## Pipeline

```
Stage 0  Corpus intake (PDF extraction, metadata, stable IDs)
Stage 1  Segmentation (chapter/scene for fiction, date-block for Exegesis)
Stage 2  Vocabulary bootstrapping (AI + psychology controlled terms)
Stage 3  Candidate detection (regex matchers + optional LLM tagging)
Stage 4  Passage classification (source_mode, psych_mode, claim_type)
Stage 5  Evidence packet generation (multi-lane, with contradiction lists)
Stage 6  Entry drafting (rigid template, evidentiary layers separated)
Stage 7  Review and adjudication (human gates)
Stage 8  Export (JSON for site, cross-links)
```

## Structure

```
database/           SQLite schema + reference data
scripts/            Python pipeline (ingest → discover → classify → evidence → draft → export)
vocabulary/         AI themes vocabulary + prompt templates
  cache/            Cached pkd-archive data (psychology topics)
  prompt_templates/ LLM prompts for each pipeline stage
guides/             Fair use guide, writing style guide, entry structure
site/               React + Vite static site (viewer)
```

## Related Repos

- [pkd-archive](https://github.com/monadpkd/pkd-archive) — Museum-grade PKD knowledge graph (canonical data, ID namespace, psychology topics)
- [QueryPat](https://github.com/t3dy/QueryPat) — PKD Exegesis knowledge portal (upstream pipeline patterns)
- [PKDCatalog](https://github.com/t3dy/PKDCatalog) — PKD document catalog

## Collaborators

- Paul Shelton (monadpkd)
- Ted Hand (t3dy)
