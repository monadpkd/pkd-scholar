"""
Stage 3: Candidate Detection

Adapted from QueryPat's discovery_pipeline.py.
Scans corpus text to find passages matching AI and psychology vocabularies.

Architecture (from QueryPat):
  1. Materialize corpus text (one query per source lane)
  2. Load existing entities for dedup
  3. Batched matching (all topic families per row)
  4. Aggregation (group by normalized name, collect provenance)
  5. Filter, score, finalize

Inputs:  segments table with raw_text, topics table with vocabulary
Outputs: topic_segments links, discovery output JSONs

Deterministic: Regex stage is deterministic. LLM tagging is optional.
"""

import sqlite3


def run(conn: sqlite3.Connection, skip_llm: bool = False):
    """Run discovery pipeline across corpus."""
    # TODO: Implement — adapt QueryPat's discovery_pipeline.py
    # Key adaptations needed:
    # 1. Use AI + psychology vocabularies instead of Exegesis terms
    # 2. Match against fiction text (different text characteristics)
    # 3. Score with domain-specific markers
    # 4. Optional LLM pass for passage-level classification
    print("  [discover] Stage 3 stub — adapt QueryPat discovery pipeline")
    print("  [discover] Step 1: Materialize segments by source lane")
    print("  [discover] Step 2: Compile matchers from vocabulary JSONs")
    print("  [discover] Step 3: Batch scan (all topic families per row)")
    print("  [discover] Step 4: Aggregate hits, score, deduplicate")
    if not skip_llm:
        print("  [discover] Step 5: LLM tagging (source_mode, psych_mode, stance)")
    else:
        print("  [discover] Step 5: Skipped (--skip-llm)")
