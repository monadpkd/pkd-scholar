"""
Stage 4: Passage Classification

For each matched segment, classify on Ted's ontology:
  - source_mode: fiction / exegesis / letter / interview / criticism
  - psych_mode: clinical / psychoanalytic / jungian / existential / etc.
  - ai_mode: economic_gatekeeper / diagnostic_authority / etc.
  - claim_type: definition / symptom_description / causal_theory / etc.
  - speaker_type: author / character / narrator / critic
  - stance: endorsed / dramatized / mentioned / questioned / contradicted
  - confidence: high / medium / low

Inputs:  topic_segments links from Stage 3
Outputs: claims table populated

Deterministic: source_mode can be inferred from work metadata (deterministic).
               psych_mode and claim_type require LLM (optional).
"""

import sqlite3


def run(conn: sqlite3.Connection, skip_llm: bool = False):
    """Classify all matched passages."""
    # TODO: Implement
    # Deterministic classifications:
    #   - source_mode from works.source_lane + works.work_type
    #   - speaker_type = "author" for Exegesis, "narrator/character" for fiction
    # LLM classifications:
    #   - psych_mode, claim_type, stance require contextual reading
    print("  [classify] Stage 4 stub — passage classification")
    print("  [classify] Deterministic: source_mode, speaker_type from metadata")
    if not skip_llm:
        print("  [classify] LLM: psych_mode, ai_mode, claim_type, stance")
    else:
        print("  [classify] LLM classification skipped (--skip-llm)")
