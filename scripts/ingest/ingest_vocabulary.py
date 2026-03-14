"""
Stage 2: Vocabulary Bootstrapping

Loads controlled vocabulary into topics and topic_aliases tables.
Creates the canonical term set that the discovery pipeline matches against.

Sources:
  - AI themes: vocabulary/ai_themes.json (local to this repo)
  - Psychology themes: monadpkd/pkd-archive → psychology/pkd_psychology_topics.json
    (canonical source — DO NOT duplicate here)

Inputs:  vocabulary/ai_themes.json + pkd-archive psychology topics
Outputs: topics and topic_aliases tables populated

Deterministic: Yes
"""

import json
import sqlite3
from pathlib import Path


def slugify(name: str) -> str:
    import re
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug.strip('-')


def load_psychology_topics(conn: sqlite3.Connection, vocab_dir: Path):
    """Load psychology vocabulary from pkd-archive (canonical source).

    Looks for a local cache at vocabulary/cache/pkd_psychology_topics.json.
    If not found, fetches from GitHub via gh CLI.
    """
    cache_path = vocab_dir / "cache" / "pkd_psychology_topics.json"

    if cache_path.exists():
        data = json.loads(cache_path.read_text())
    else:
        import subprocess
        print("  [psych] Fetching psychology topics from pkd-archive...")
        result = subprocess.run(
            ["gh", "api", "repos/monadpkd/pkd-archive/contents/psychology/pkd_psychology_topics.json",
             "--jq", ".content"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  [skip] Could not fetch psychology topics from pkd-archive: {result.stderr}")
            return 0
        import base64
        content = base64.b64decode(result.stdout.strip()).decode("utf-8")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(content)
        data = json.loads(content)

    created = 0
    priority_set = set(data.get("first_wave_20", []))

    for subfamily, topics in data.get("topic_families", {}).items():
        for topic in topics:
            # Handle both string entries and dict entries
            if isinstance(topic, str):
                term = topic
            elif isinstance(topic, dict):
                term = topic.get("canonical_name", topic.get("name", ""))
            else:
                continue

            slug = slugify(term)
            mnemonic = slug.upper().replace("-", "")[:12]
            topic_id = f"PKD-PSY-{mnemonic}"

            existing = conn.execute(
                "SELECT topic_id FROM topics WHERE topic_id = ?", (topic_id,)
            ).fetchone()
            if existing:
                continue

            priority = 1 if slug in priority_set or term in priority_set else 0

            conn.execute(
                "INSERT INTO topics (topic_id, canonical_name, slug, topic_family, "
                "topic_subfamily, status, priority) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (topic_id, term, slug, "psychology", subfamily,
                 "provisional", priority)
            )
            created += 1

    return created


def load_ai_topics(conn: sqlite3.Connection, vocab_dir: Path):
    """Load AI/automation vocabulary into topics table."""
    path = vocab_dir / "ai_themes.json"
    if not path.exists():
        print(f"  [skip] {path} not found")
        return 0

    data = json.loads(path.read_text())
    created = 0

    # Load machine role categories as topics
    for role in data.get("machine_role_categories", []):
        mnemonic = role["id"].upper().replace("_", "")[:12]
        topic_id = f"PKD-AIT-{mnemonic}"
        existing = conn.execute(
            "SELECT topic_id FROM topics WHERE topic_id = ?", (topic_id,)
        ).fetchone()
        if existing:
            continue

        conn.execute(
            "INSERT INTO topics (topic_id, canonical_name, slug, topic_family, "
            "definition, status) VALUES (?, ?, ?, ?, ?, ?)",
            (topic_id, role["label"], role["id"], "ai_automation",
             role["description"], "provisional")
        )
        created += 1

    # Load controlled vocabulary terms as aliases for broader topics
    for category, terms in data.get("controlled_vocabulary", {}).items():
        for term in terms:
            slug = slugify(term)
            mnemonic = slug.upper().replace("-", "")[:12]
            topic_id = f"PKD-AIT-{mnemonic}"

            existing = conn.execute(
                "SELECT topic_id FROM topics WHERE topic_id = ?", (topic_id,)
            ).fetchone()
            if existing:
                continue

            conn.execute(
                "INSERT INTO topics (topic_id, canonical_name, slug, topic_family, "
                "topic_subfamily, status) VALUES (?, ?, ?, ?, ?, ?)",
                (topic_id, term, slug, "ai_automation", category, "provisional")
            )
            created += 1

    return created


def run(conn: sqlite3.Connection, vocab_dir: Path):
    """Load all vocabulary files."""
    psych_count = load_psychology_topics(conn, vocab_dir)
    ai_count = load_ai_topics(conn, vocab_dir)
    conn.commit()
    print(f"  [vocabulary] Created {psych_count} psychology topics, {ai_count} AI topics")
