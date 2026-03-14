#!/usr/bin/env python3
"""
pkd-scholar build pipeline orchestrator.
Adapted from QueryPat's build_all.py.

Stages:
  0 — Corpus intake (PDF extraction, metadata, stable IDs)
  1 — Segmentation (chapter/scene for fiction, date-block for Exegesis)
  2 — Vocabulary bootstrapping (controlled terms + aliases)
  3 — Candidate detection (deterministic regex + LLM classification)
  4 — Passage classification (source_mode, psych_mode, claim_type)
  5 — Evidence packet generation (multi-lane, with contradiction lists)
  6 — Entry drafting (rigid template, evidentiary layers separated)
  7 — Review and adjudication (fair use, style, false positive checks)
  8 — Export and linking (JSON for site, cross-links)

Usage:
  python build_all.py                    # full pipeline
  python build_all.py --fresh            # drop and rebuild database
  python build_all.py --skip-llm         # deterministic stages only
  python build_all.py --stage 3          # run single stage
  python build_all.py --export-only      # just regenerate JSON exports
  python build_all.py --audit-only       # validation report only
"""

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "pkd_scholar.sqlite"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
CORPUS_DIR = PROJECT_ROOT / "corpus"  # PDFs go here (gitignored)
EXPORT_DIR = PROJECT_ROOT / "site" / "public" / "data"


def init_db(fresh: bool = False) -> sqlite3.Connection:
    """Initialize database from schema.sql."""
    if fresh and DB_PATH.exists():
        DB_PATH.unlink()
        print("[init] Removed existing database")

    exists = DB_PATH.exists()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    if not exists:
        print("[init] Creating database from schema.sql")
        with open(SCHEMA_PATH) as f:
            conn.executescript(f.read())
        print("[init] Database created")
    else:
        print(f"[init] Using existing database ({DB_PATH})")

    return conn


def log_run(conn: sqlite3.Connection, stage: str, script: str,
            processed: int = 0, created: int = 0, updated: int = 0,
            errors: int = 0, notes: str = ""):
    """Log a pipeline run to the audit table."""
    conn.execute(
        "INSERT INTO pipeline_runs (stage, script_name, completed_at, "
        "records_processed, records_created, records_updated, errors, notes) "
        "VALUES (?, ?, datetime('now'), ?, ?, ?, ?, ?)",
        (stage, script, processed, created, updated, errors, notes)
    )
    conn.commit()


# ── Stage 0: Corpus Intake ─────────────────────────────────────
def stage_0_corpus_intake(conn):
    """Extract text from PDFs, assign stable IDs, store metadata."""
    from ingest.ingest_corpus import run
    return run(conn, CORPUS_DIR)


# ── Stage 1: Segmentation ──────────────────────────────────────
def stage_1_segmentation(conn):
    """Chunk works by genre: chapters/scenes for fiction, date-blocks for Exegesis."""
    from ingest.ingest_segments import run
    return run(conn)


# ── Stage 2: Vocabulary Bootstrapping ──────────────────────────
def stage_2_vocabulary(conn):
    """Load controlled vocabulary (AI + psychology terms) and aliases."""
    from ingest.ingest_vocabulary import run
    return run(conn, PROJECT_ROOT / "vocabulary")


# ── Stage 3: Candidate Detection ───────────────────────────────
def stage_3_detection(conn, skip_llm: bool = False):
    """Run deterministic matchers, then optional LLM tagging."""
    from discover.discovery_pipeline import run
    return run(conn, skip_llm=skip_llm)


# ── Stage 4: Passage Classification ────────────────────────────
def stage_4_classification(conn, skip_llm: bool = False):
    """Classify passages: source_mode, psych_mode, claim_type, confidence."""
    from classify.classify_passages import run
    return run(conn, skip_llm=skip_llm)


# ── Stage 5: Evidence Packets ──────────────────────────────────
def stage_5_evidence(conn):
    """Assemble evidence packets per topic with contradiction lists."""
    from evidence.build_packets import run
    return run(conn)


# ── Stage 6: Entry Drafting ────────────────────────────────────
def stage_6_drafting(conn):
    """Generate dictionary entries from evidence packets."""
    from draft.draft_entries import run
    return run(conn)


# ── Stage 7: Review ────────────────────────────────────────────
def stage_7_review(conn):
    """Fair use check, style revision, false positive flagging."""
    # This stage is primarily human-in-the-loop
    print("[stage 7] Review stage — run audit.py for automated checks")
    print("[stage 7] Human review gates: false positives, over-psychologizing, fair use")


# ── Stage 8: Export ────────────────────────────────────────────
def stage_8_export(conn):
    """Export JSON for site + cross-links."""
    from export.export_json import run
    return run(conn, EXPORT_DIR)


# ── Audit ──────────────────────────────────────────────────────
def run_audit(conn):
    """Run validation checks across all tables."""
    from audit import run
    return run(conn)


# ── Main ───────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="pkd-scholar build pipeline")
    parser.add_argument("--fresh", action="store_true", help="Drop and rebuild database")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM-assisted stages")
    parser.add_argument("--stage", type=int, help="Run a single stage (0-8)")
    parser.add_argument("--export-only", action="store_true", help="Only regenerate JSON exports")
    parser.add_argument("--audit-only", action="store_true", help="Only run audit")
    args = parser.parse_args()

    conn = init_db(fresh=args.fresh)

    if args.audit_only:
        run_audit(conn)
        return

    if args.export_only:
        stage_8_export(conn)
        return

    stages = {
        0: ("Corpus Intake", lambda: stage_0_corpus_intake(conn)),
        1: ("Segmentation", lambda: stage_1_segmentation(conn)),
        2: ("Vocabulary", lambda: stage_2_vocabulary(conn)),
        3: ("Detection", lambda: stage_3_detection(conn, args.skip_llm)),
        4: ("Classification", lambda: stage_4_classification(conn, args.skip_llm)),
        5: ("Evidence Packets", lambda: stage_5_evidence(conn)),
        6: ("Entry Drafting", lambda: stage_6_drafting(conn)),
        7: ("Review", lambda: stage_7_review(conn)),
        8: ("Export", lambda: stage_8_export(conn)),
    }

    if args.stage is not None:
        if args.stage in stages:
            name, fn = stages[args.stage]
            print(f"\n{'='*60}")
            print(f"  Stage {args.stage}: {name}")
            print(f"{'='*60}")
            t0 = time.time()
            fn()
            print(f"  [{name}] completed in {time.time()-t0:.1f}s")
        else:
            print(f"Unknown stage: {args.stage}")
            sys.exit(1)
        return

    # Full pipeline
    for num, (name, fn) in sorted(stages.items()):
        print(f"\n{'='*60}")
        print(f"  Stage {num}: {name}")
        print(f"{'='*60}")
        t0 = time.time()
        fn()
        print(f"  [{name}] completed in {time.time()-t0:.1f}s")

    print(f"\n{'='*60}")
    print("  Audit")
    print(f"{'='*60}")
    run_audit(conn)

    conn.close()
    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
