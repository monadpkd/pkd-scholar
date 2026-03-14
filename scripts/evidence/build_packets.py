"""
Stage 5: Evidence Packet Generation

For each topic, assemble packets with five components (per Ted's spec):
  1. Representative PKD fiction passages (Lane A)
  2. Exegesis passages (Lane A)
  3. Top secondary commentary (Lane C)
  4. Chronology of the concept in Dick's work
  5. Contradiction list (first-class — crucial for PKD)

Inputs:  claims table, topic_segments links
Outputs: evidence_packets, evidence_excerpts, contradictions tables

Deterministic: Assembly is deterministic. Ranking may use LLM.
"""

import sqlite3


def run(conn: sqlite3.Connection):
    """Assemble evidence packets for all topics with sufficient claims."""
    # TODO: Implement
    print("  [evidence] Stage 5 stub — evidence packet assembly")
    print("  [evidence] Per topic: fiction passages, Exegesis passages, commentary")
    print("  [evidence] Chronology: order by work year + segment position")
    print("  [evidence] Contradictions: detect incompatible claims on same topic")
