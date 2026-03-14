"""
Stage 6: Entry Drafting

Generates dictionary entries from evidence packets using rigid template.
The model must NOT improvise a unified theory unless the evidence warrants one.
Must explicitly separate: "Dick dramatizes," "Dick proposes in the Exegesis,"
and "critics argue."

Template (from guides/entry_structure.md):
  1. Definition (scholarly, plain English)
  2. PKD Relevance
  3. In the Fiction (Lane A)
  4. In the Exegesis (Lane A)
  5. Intellectual Background (Lane B)
  6. Scholarly Debate (Lane C)
  7. Chronology
  8. Key Passages
  9. Contradictions
  10. Related Entries
  11. Editorial Note / Open Questions

Inputs:  evidence_packets, claims, topics
Outputs: dictionary_entries table

LLM-assisted: Yes (entry prose generation)
"""

import sqlite3


def run(conn: sqlite3.Connection):
    """Draft dictionary entries for topics with sufficient evidence."""
    # TODO: Implement
    # Key constraints:
    # 1. Use prompt from vocabulary/prompt_templates/psychology_analysis.md or ai_analysis.md
    # 2. Apply fair_use_style_guide.md constraints
    # 3. Apply writing_style_guide.md constraints
    # 4. Keep evidentiary lanes separate in prose
    # 5. Include contradictions
    # 6. Do not diagnose Dick
    print("  [draft] Stage 6 stub — dictionary entry generation")
    print("  [draft] Template: guides/entry_structure.md")
    print("  [draft] Style: guides/writing_style_guide.md")
    print("  [draft] Fair use: guides/fair_use_style_guide.md")
