"""
Stage 3: Candidate Detection

Scans corpus text to find passages matching AI and psychology vocabularies.
Uses deterministic regex matching against controlled vocabulary terms.

Inputs:  segments table with raw_text, topics table with vocabulary
Outputs: topic_segments links, topic_works aggregated links

Deterministic: Yes (regex only, no LLM)
"""

import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "scripts"))

from discover.matchers import load_matchers, scan_text


def run(conn: sqlite3.Connection, skip_llm: bool = True):
    """Run discovery pipeline across corpus."""

    print("  [discover] Stage 3: Candidate Detection")
    print("  [discover] Step 1: Loading matchers from vocabulary...")

    matchers = load_matchers(conn)
    print(f"  [discover] Loaded {len(matchers)} topic matchers")

    # Step 2: Clear previous discovery results
    conn.execute("DELETE FROM topic_segments")
    conn.execute("DELETE FROM topic_works")
    print("  [discover] Cleared previous discovery results")

    # Step 3: Load all segments with text
    cur = conn.execute(
        "SELECT seg_id, work_id, raw_text FROM segments "
        "WHERE raw_text IS NOT NULL AND raw_text != '' "
        "ORDER BY work_id, position"
    )
    segments = cur.fetchall()
    print(f"  [discover] Scanning {len(segments)} segments...")

    # Track stats
    total_matches = 0
    work_matches = defaultdict(int)  # work_id -> count
    topic_match_counts = defaultdict(int)  # topic_id -> count
    topic_work_matches = defaultdict(lambda: defaultdict(int))  # topic_id -> work_id -> count
    batch = []
    batch_size = 500

    for i, (seg_id, work_id, raw_text) in enumerate(segments):
        hits = scan_text(raw_text, matchers)

        for topic_id, matched_text, match_type, position, context in hits:
            batch.append((topic_id, seg_id, match_type, 1, matched_text, context))
            work_matches[work_id] += 1
            topic_match_counts[topic_id] += 1
            topic_work_matches[topic_id][work_id] += 1
            total_matches += 1

        # Flush batch
        if len(batch) >= batch_size:
            conn.executemany(
                "INSERT OR IGNORE INTO topic_segments "
                "(topic_id, seg_id, match_type, link_confidence, matched_text, context_window) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                batch
            )
            batch = []

        if (i + 1) % 200 == 0:
            print(f"    ... processed {i + 1}/{len(segments)} segments, {total_matches} matches so far")

    # Flush remaining
    if batch:
        conn.executemany(
            "INSERT OR IGNORE INTO topic_segments "
            "(topic_id, seg_id, match_type, link_confidence, matched_text, context_window) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            batch
        )

    print(f"  [discover] Step 4: Creating topic_works aggregations...")

    # Build topic_works from aggregated counts
    for topic_id, works in topic_work_matches.items():
        for work_id, count in works.items():
            if count >= 10:
                relevance = 'central'
            elif count >= 5:
                relevance = 'significant'
            elif count >= 2:
                relevance = 'mentioned'
            else:
                relevance = 'peripheral'

            conn.execute(
                "INSERT OR IGNORE INTO topic_works (topic_id, work_id, relevance, notes) "
                "VALUES (?, ?, ?, ?)",
                (topic_id, work_id, relevance, f"{count} matches")
            )

    conn.commit()

    # Print summary
    print(f"\n  === DISCOVERY RESULTS ===")
    print(f"  Total matches: {total_matches}")
    print(f"\n  Matches per work:")

    # Get work titles
    work_titles = {}
    for row in conn.execute("SELECT work_id, title FROM works"):
        work_titles[row[0]] = row[1]

    for work_id in sorted(work_matches, key=lambda w: work_matches[w], reverse=True):
        title = work_titles.get(work_id, work_id)
        print(f"    {title}: {work_matches[work_id]} matches")

    # Get topic names
    topic_names = {}
    for row in conn.execute("SELECT topic_id, canonical_name FROM topics"):
        topic_names[row[0]] = row[1]

    print(f"\n  Top 20 most-matched terms:")
    sorted_topics = sorted(topic_match_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    for topic_id, count in sorted_topics:
        name = topic_names.get(topic_id, topic_id)
        print(f"    {name}: {count} matches")

    # Pipeline run record
    conn.execute(
        "INSERT INTO pipeline_runs (stage, script_name, records_processed, records_created, notes) "
        "VALUES (?, ?, ?, ?, ?)",
        ("discovery", "discovery_pipeline.py", len(segments), total_matches,
         f"Regex scan: {len(matchers)} matchers, {total_matches} matches across {len(work_matches)} works")
    )
    conn.commit()

    return total_matches


def main():
    """Standalone runner."""
    db_path = project_root / "database" / "pkd_scholar.sqlite"

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")

    print(f"Running discovery pipeline against {db_path}")
    total = run(conn)
    print(f"\nDone. {total} total matches recorded.")

    conn.close()


if __name__ == "__main__":
    main()
