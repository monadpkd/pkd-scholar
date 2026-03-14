"""
Stage 2: Vocabulary Bootstrapping

Loads controlled vocabulary into topics and topic_aliases tables.
Creates the canonical term set that the discovery pipeline matches against.

Sources:
  - AI themes: vocabulary/ai_themes.json (local to this repo)
  - Psychology themes: monadpkd/pkd-archive (skipped for now — loaded when available)

Inputs:  vocabulary/ai_themes.json + pkd-archive psychology topics
Outputs: topics and topic_aliases tables populated

Deterministic: Yes
"""

import json
import re
import sqlite3
from pathlib import Path


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug.strip('-')


def make_mnemonic(text: str, max_len: int = 12) -> str:
    """Create a short uppercase mnemonic from text."""
    return slugify(text).upper().replace("-", "")[:max_len]


def insert_topic(conn, topic_id, canonical_name, slug, topic_family,
                 topic_subfamily=None, definition=None, pkd_relevance=None,
                 status='provisional'):
    """Insert a topic, skip if already exists. Returns True if created."""
    existing = conn.execute(
        "SELECT topic_id FROM topics WHERE topic_id = ?", (topic_id,)
    ).fetchone()
    if existing:
        return False

    # Check for slug collision
    slug_row = conn.execute(
        "SELECT topic_id FROM topics WHERE slug = ?", (slug,)
    ).fetchone()
    if slug_row:
        # Append a suffix
        slug = slug + "-" + topic_id.split("-")[-1].lower()[:4]

    conn.execute(
        "INSERT INTO topics (topic_id, canonical_name, slug, topic_family, "
        "topic_subfamily, definition, pkd_relevance, status) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (topic_id, canonical_name, slug, topic_family,
         topic_subfamily, definition, pkd_relevance, status)
    )
    return True


def insert_alias(conn, topic_id, alias_text, alias_type='synonym'):
    """Insert a topic alias, skip if already exists."""
    existing = conn.execute(
        "SELECT alias_id FROM topic_aliases WHERE topic_id = ? AND alias = ?",
        (topic_id, alias_text)
    ).fetchone()
    if existing:
        return False
    conn.execute(
        "INSERT INTO topic_aliases (topic_id, alias, alias_type) VALUES (?, ?, ?)",
        (topic_id, alias_text, alias_type)
    )
    return True


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
            if isinstance(topic, str):
                term = topic
            elif isinstance(topic, dict):
                term = topic.get("canonical_name", topic.get("name", ""))
            else:
                continue

            slug = slugify(term)
            mnemonic = make_mnemonic(term)
            topic_id = f"PKD-PSY-{mnemonic}"

            priority = 1 if slug in priority_set or term in priority_set else 0

            if insert_topic(conn, topic_id, term, slug, "psychology",
                            topic_subfamily=subfamily):
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
    aliases_created = 0

    # 1. Load machine role categories as topics
    for role in data.get("machine_role_categories", []):
        mnemonic = make_mnemonic(role["id"])
        topic_id = f"PKD-AIT-{mnemonic}"
        slug = role["id"].replace("_", "-")

        if insert_topic(conn, topic_id, role["label"], slug, "ai_automation",
                        topic_subfamily="machine_role",
                        definition=role["description"]):
            created += 1

        # Add examples as aliases
        for example in role.get("examples", []):
            if insert_alias(conn, topic_id, example, "related_term"):
                aliases_created += 1

    # 2. Load human response categories as topics
    for response in data.get("human_response_categories", []):
        mnemonic = make_mnemonic(response["id"])
        topic_id = f"PKD-AIT-{mnemonic}"
        slug = response["id"].replace("_", "-")

        if insert_topic(conn, topic_id, response["label"], slug, "ai_automation",
                        topic_subfamily="human_response"):
            created += 1

    # 3. Load controlled vocabulary terms as individual topics
    for category, terms in data.get("controlled_vocabulary", {}).items():
        for term in terms:
            slug = slugify(term)
            mnemonic = make_mnemonic(term)
            topic_id = f"PKD-AIT-{mnemonic}"

            if insert_topic(conn, topic_id, term, slug, "ai_automation",
                            topic_subfamily=category):
                created += 1

            # Also add the term as an alias of itself for matching purposes
            # (the canonical_name is the primary match, aliases catch variants)

    print(f"  [ai] Created {created} topics, {aliases_created} aliases")
    return created


def load_common_terms(conn: sqlite3.Connection, vocab_dir: Path):
    """Load supplementary common PKD terms from pkd_common_terms.json."""
    path = vocab_dir / "pkd_common_terms.json"
    if not path.exists():
        print(f"  [skip] {path} not found")
        return 0

    data = json.loads(path.read_text())
    created = 0

    for group_key, group in data.get("terms", {}).items():
        family = group.get("family", "ai_automation")
        subfamily = group.get("subfamily", group_key)

        for term in group.get("terms", []):
            slug = slugify(term)
            mnemonic = make_mnemonic(term)
            topic_id = f"PKD-AIT-{mnemonic}" if family == "ai_automation" else f"PKD-PSY-{mnemonic}" if family == "psychology" else f"PKD-MET-{mnemonic}"

            if insert_topic(conn, topic_id, term, slug, family,
                            topic_subfamily=subfamily):
                created += 1

    print(f"  [common] Created {created} supplementary topics")
    return created


def run(conn: sqlite3.Connection, vocab_dir: Path):
    """Load all vocabulary files."""
    psych_count = load_psychology_topics(conn, vocab_dir)
    ai_count = load_ai_topics(conn, vocab_dir)
    common_count = load_common_terms(conn, vocab_dir)
    conn.commit()
    print(f"  [vocabulary] Created {psych_count} psychology + {ai_count} AI + {common_count} common topics")
    return psych_count + ai_count + common_count


def main():
    """Standalone runner for vocabulary ingest."""
    import sys
    project_root = Path(__file__).resolve().parent.parent.parent
    db_path = project_root / "database" / "pkd_scholar.sqlite"
    vocab_dir = project_root / "vocabulary"

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")

    print(f"Loading vocabulary from {vocab_dir}")
    print(f"Database: {db_path}")

    total = run(conn, vocab_dir)

    # Print summary
    cur = conn.execute("SELECT COUNT(*) FROM topics")
    topic_count = cur.fetchone()[0]
    cur = conn.execute("SELECT COUNT(*) FROM topic_aliases")
    alias_count = cur.fetchone()[0]

    cur = conn.execute(
        "SELECT topic_family, topic_subfamily, COUNT(*) as cnt "
        "FROM topics GROUP BY topic_family, topic_subfamily ORDER BY topic_family, cnt DESC"
    )
    print(f"\nTotal topics in DB: {topic_count}")
    print(f"Total aliases in DB: {alias_count}")
    print("\nBreakdown:")
    for row in cur:
        print(f"  {row[0]}/{row[1] or '(none)'}: {row[2]}")

    conn.close()


if __name__ == "__main__":
    main()
