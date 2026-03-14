"""
Audit: Data integrity validation

Adapted from QueryPat's audit.py.
Checks all tables for completeness, orphans, and consistency.

QA types (from Ted's spec):
  - File-level QA (are all PDFs extracted?)
  - Extraction QA (is text quality sufficient?)
  - Chunk QA (are segments properly bounded?)
  - Retrieval QA (did the matchers find expected terms?)
  - Analysis QA (are claims properly classified?)
  - Citation QA (does every claim have a source reference?)
  - Fair-use QA (are quotes within length limits?)
  - Style QA (does prose follow the style guide?)

Outputs: audit_report.json + audit_report.md
"""

import json
import sqlite3
from pathlib import Path


def run(conn: sqlite3.Connection):
    """Run all audit checks."""
    report = {"checks": [], "summary": {}}

    # Count checks
    tables = ["works", "segments", "topics", "topic_aliases", "claims",
              "evidence_packets", "evidence_excerpts", "contradictions",
              "persons", "schools", "machine_roles", "dictionary_entries"]

    for table in tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            report["checks"].append({
                "check": f"count_{table}",
                "severity": "info",
                "value": count,
                "status": "ok" if count > 0 else "empty"
            })
        except Exception as e:
            report["checks"].append({
                "check": f"count_{table}",
                "severity": "error",
                "value": str(e),
                "status": "error"
            })

    # TODO: Add integrity checks
    # - Orphaned segments (no parent work)
    # - Claims without citations
    # - Evidence excerpts exceeding fair-use quote length
    # - Topics with no linked segments
    # - Dictionary entries with empty required fields

    errors = sum(1 for c in report["checks"] if c["status"] == "error")
    warnings = sum(1 for c in report["checks"] if c["status"] == "empty")

    report["summary"] = {
        "total_checks": len(report["checks"]),
        "errors": errors,
        "warnings": warnings,
        "passed": len(report["checks"]) - errors - warnings
    }

    print(f"  [audit] {report['summary']['total_checks']} checks: "
          f"{report['summary']['passed']} passed, "
          f"{report['summary']['warnings']} warnings, "
          f"{report['summary']['errors']} errors")

    return report
