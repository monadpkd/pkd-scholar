"""
Stage 1: Segmentation

Chunks works by genre:
- Fiction (novels): by chapter or scene-sized windows
- Fiction (short stories): by scene breaks or fixed-size windows
- Exegesis: by notebook/date block
- Criticism: by section headings or paragraph clusters

Inputs:  works table with raw text
Outputs: segments table populated

Deterministic: Yes
"""

import sqlite3


def run(conn: sqlite3.Connection):
    """Segment all works that have extracted text but no segments yet."""
    # TODO: Implement genre-aware chunking
    # For now, stub that shows the approach
    print("  [segments] Stage 1 stub — implement genre-aware chunking")
    print("  [segments] Fiction novels → chapter boundaries")
    print("  [segments] Short stories → scene breaks or ~2000 word windows")
    print("  [segments] Exegesis → date-block parsing (reuse QueryPat logic)")
    print("  [segments] Criticism → section headings or ~1500 word windows")
