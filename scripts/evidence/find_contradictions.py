"""
Contradiction Finder

Identifies cases where Dick or critics offer incompatible explanations
of the same phenomenon. These are first-class data per Ted's spec.

Types of contradictions:
  - temporal_shift: Dick changes position over time
  - genre_difference: fiction says X, Exegesis says Y
  - self_revision: explicit retraction or revision
  - interpretive_dispute: critics disagree

Inputs:  claims table (multiple claims per topic)
Outputs: contradictions table

Deterministic: Detection heuristics are deterministic.
               Nuanced contradiction analysis may use LLM.
"""

import sqlite3


def run(conn: sqlite3.Connection):
    """Find contradictions within topics."""
    # TODO: Implement
    print("  [contradictions] Stub — detect incompatible claims per topic")
