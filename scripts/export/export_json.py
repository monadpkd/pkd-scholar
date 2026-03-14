"""
Stage 8: Export JSON for Site

Adapted from QueryPat's export_json.py.
Two-tier lazy-loading pattern:
  - Index files: list all items (minimal fields)
  - Detail files: loaded on demand (full content)

Output structure:
  site/public/data/
    studies/
      index.json          — all studies with summaries
      ai-automation.json  — AI/robot study detail
      psychology.json     — psychology study detail
    topics/
      index.json          — all topics
      {slug}.json         — per-topic detail with evidence
    works/
      index.json          — all works
      {slug}.json         — per-work detail with linked topics
    entries/
      index.json          — all dictionary entries
      {slug}.json         — per-entry detail
    search_index.json     — Fuse.js fuzzy search index
    analytics.json        — counts and coverage stats
    graph.json            — cross-entity connections

Inputs:  All database tables
Outputs: JSON files in site/public/data/

Deterministic: Yes
"""

import json
import sqlite3
from pathlib import Path


def run(conn: sqlite3.Connection, export_dir: Path):
    """Export all data to JSON for the static site."""
    # TODO: Implement — adapt QueryPat's export_json.py
    export_dir.mkdir(parents=True, exist_ok=True)

    print(f"  [export] Target: {export_dir}")
    print("  [export] Stage 8 stub — JSON export")
    print("  [export] Will create: studies/, topics/, works/, entries/")
    print("  [export] Plus: search_index.json, analytics.json, graph.json")
