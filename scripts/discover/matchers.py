"""
Matchers: compile regex patterns from topics and aliases for text scanning.

Reads all topics and aliases from the database, builds compiled regex patterns
for case-insensitive word-boundary matching.
"""

import re
import sqlite3
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class TopicMatcher:
    topic_id: str
    canonical_name: str
    patterns: list = field(default_factory=list)
    # Each pattern is (compiled_regex, source_text, match_type)
    # match_type: 'exact_text' for canonical, 'alias' for aliases


def escape_for_regex(text: str) -> str:
    """Escape special regex characters but preserve word structure."""
    return re.escape(text)


def build_pattern(term: str) -> re.Pattern:
    """Build a word-boundary regex for a term, case-insensitive."""
    escaped = escape_for_regex(term.strip())
    # Use word boundaries for clean matching
    return re.compile(r'\b' + escaped + r'\b', re.IGNORECASE)


def load_matchers(conn: sqlite3.Connection) -> List[TopicMatcher]:
    """Load all topics and aliases, return compiled matchers."""
    matchers = []

    # Get all topics
    cur = conn.execute(
        "SELECT topic_id, canonical_name FROM topics ORDER BY topic_id"
    )
    topics = cur.fetchall()

    for topic_id, canonical_name in topics:
        matcher = TopicMatcher(topic_id=topic_id, canonical_name=canonical_name)

        # Add canonical name as primary pattern
        try:
            pat = build_pattern(canonical_name)
            matcher.patterns.append((pat, canonical_name, 'exact_text'))
        except re.error:
            pass  # Skip if regex fails

        # Add aliases
        alias_cur = conn.execute(
            "SELECT alias, alias_type FROM topic_aliases WHERE topic_id = ?",
            (topic_id,)
        )
        for alias_text, alias_type in alias_cur:
            try:
                pat = build_pattern(alias_text)
                matcher.patterns.append((pat, alias_text, 'alias'))
            except re.error:
                pass

        if matcher.patterns:
            matchers.append(matcher)

    return matchers


def scan_text(text: str, matchers: List[TopicMatcher]) -> List[Tuple[str, str, str, int, str]]:
    """
    Scan text against all matchers.

    Returns list of (topic_id, matched_text, match_type, position, context_window)
    """
    if not text:
        return []

    results = []
    seen = set()  # (topic_id, position) to deduplicate overlapping patterns

    for matcher in matchers:
        for pattern, source_text, match_type in matcher.patterns:
            for m in pattern.finditer(text):
                key = (matcher.topic_id, m.start())
                if key in seen:
                    continue
                seen.add(key)

                # Extract context window: 150 chars around the match
                ctx_start = max(0, m.start() - 75)
                ctx_end = min(len(text), m.end() + 75)
                context = text[ctx_start:ctx_end]
                # Clean up context (no partial words at edges)
                if ctx_start > 0:
                    first_space = context.find(' ')
                    if first_space > 0 and first_space < 20:
                        context = '...' + context[first_space:]
                if ctx_end < len(text):
                    last_space = context.rfind(' ')
                    if last_space > len(context) - 20:
                        context = context[:last_space] + '...'

                results.append((
                    matcher.topic_id,
                    m.group(),         # actual matched text
                    match_type,
                    m.start(),
                    context
                ))

    return results
