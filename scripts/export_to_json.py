#!/usr/bin/env python3
"""Export PKD Scholar SQLite data to JSON files for the static React site."""

import json
import os
import re
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'pkd_scholar.sqlite')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'site', 'public', 'data')


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def slugify(name):
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug.strip('-')


def export_works_index(conn):
    """Export all works with metadata (no raw_text)."""
    cur = conn.execute("""
        SELECT w.work_id, w.title, w.slug, w.work_type, w.source_lane, w.author,
               w.year_published, w.page_count, w.extraction_status, w.notes,
               COUNT(s.seg_id) as segment_count,
               COALESCE(SUM(s.word_count), 0) as total_word_count
        FROM works w
        LEFT JOIN segments s ON w.work_id = s.work_id
        GROUP BY w.work_id
        ORDER BY w.year_published
    """)
    works = cur.fetchall()

    works_dir = os.path.join(OUTPUT_DIR, 'works')
    ensure_dir(works_dir)

    with open(os.path.join(works_dir, 'index.json'), 'w') as f:
        json.dump(works, f, indent=2)

    print(f"  works/index.json: {len(works)} works")
    return works


def export_work_details(conn, works):
    """Export per-work detail with segment list and topics found."""
    works_dir = os.path.join(OUTPUT_DIR, 'works')

    for work in works:
        cur = conn.execute("""
            SELECT seg_id, title, segment_type, position, page_start, page_end, word_count
            FROM segments
            WHERE work_id = ?
            ORDER BY position
        """, (work['work_id'],))
        segments = cur.fetchall()

        # Get topics found in this work with match counts
        cur = conn.execute("""
            SELECT t.topic_id, t.canonical_name, t.slug, t.topic_family,
                   t.topic_subfamily, tw.relevance,
                   (SELECT COUNT(*) FROM topic_segments ts
                    JOIN segments s ON ts.seg_id = s.seg_id
                    WHERE ts.topic_id = t.topic_id AND s.work_id = ?) as match_count
            FROM topic_works tw
            JOIN topics t ON tw.topic_id = t.topic_id
            WHERE tw.work_id = ?
            ORDER BY match_count DESC
        """, (work['work_id'], work['work_id']))
        topics = cur.fetchall()

        detail = {
            'work_id': work['work_id'],
            'title': work['title'],
            'slug': work['slug'],
            'work_type': work['work_type'],
            'source_lane': work['source_lane'],
            'author': work['author'],
            'year_published': work['year_published'],
            'page_count': work['page_count'],
            'extraction_status': work['extraction_status'],
            'notes': work['notes'],
            'segment_count': work['segment_count'],
            'total_word_count': work['total_word_count'],
            'segments': segments,
            'topics': topics,
        }

        with open(os.path.join(works_dir, f"{work['slug']}.json"), 'w') as f:
            json.dump(detail, f, indent=2)

    print(f"  works/{{slug}}.json: {len(works)} files")


def export_segments(conn):
    """Export individual segments with raw_text."""
    segments_dir = os.path.join(OUTPUT_DIR, 'segments')
    ensure_dir(segments_dir)

    cur = conn.execute("""
        SELECT s.seg_id, s.work_id, s.title, s.segment_type, s.position,
               s.page_start, s.page_end, s.raw_text, s.word_count,
               w.title as work_title, w.slug as work_slug
        FROM segments s
        JOIN works w ON s.work_id = w.work_id
        ORDER BY s.seg_id
    """)
    segments = cur.fetchall()

    # Build prev/next lookup per work
    work_segments = {}
    for seg in segments:
        wid = seg['work_id']
        if wid not in work_segments:
            work_segments[wid] = []
        work_segments[wid].append(seg['seg_id'])

    for seg in segments:
        wid = seg['work_id']
        seg_list = work_segments[wid]
        idx = seg_list.index(seg['seg_id'])
        seg['prev_seg_id'] = seg_list[idx - 1] if idx > 0 else None
        seg['next_seg_id'] = seg_list[idx + 1] if idx < len(seg_list) - 1 else None

        with open(os.path.join(segments_dir, f"{seg['seg_id']}.json"), 'w') as f:
            json.dump(seg, f, indent=2)

    print(f"  segments/{{seg_id}}.json: {len(segments)} files")
    return segments


def export_search_index(conn):
    """Export lightweight search index."""
    cur = conn.execute("""
        SELECT s.seg_id, s.work_id, s.title, SUBSTR(s.raw_text, 1, 200) as preview,
               w.title as work_title, w.slug as work_slug
        FROM segments s
        JOIN works w ON s.work_id = w.work_id
        ORDER BY w.year_published, s.position
    """)
    entries = cur.fetchall()

    with open(os.path.join(OUTPUT_DIR, 'search_index.json'), 'w') as f:
        json.dump(entries, f)

    print(f"  search_index.json: {len(entries)} entries")


def export_stats(conn):
    """Export aggregate stats."""
    stats = {}

    cur = conn.execute("SELECT COUNT(*) as count FROM works")
    stats['total_works'] = cur.fetchone()['count']

    cur = conn.execute("SELECT COUNT(*) as count FROM segments")
    stats['total_segments'] = cur.fetchone()['count']

    cur = conn.execute("SELECT COALESCE(SUM(word_count), 0) as total FROM segments")
    stats['total_words'] = cur.fetchone()['total']

    cur = conn.execute("SELECT COUNT(*) as count FROM topics")
    stats['total_topics'] = cur.fetchone()['count']

    cur = conn.execute("SELECT COUNT(*) as count FROM topic_segments")
    stats['total_topic_matches'] = cur.fetchone()['count']

    cur = conn.execute("""
        SELECT extraction_status, COUNT(*) as count
        FROM works
        GROUP BY extraction_status
    """)
    stats['extraction_status'] = {row['extraction_status']: row['count'] for row in cur.fetchall()}

    cur = conn.execute("""
        SELECT work_type, COUNT(*) as count
        FROM works
        GROUP BY work_type
    """)
    stats['work_types'] = {row['work_type']: row['count'] for row in cur.fetchall()}

    cur = conn.execute("""
        SELECT segment_type, COUNT(*) as count
        FROM segments
        GROUP BY segment_type
    """)
    stats['segment_types'] = {row['segment_type']: row['count'] for row in cur.fetchall()}

    # Top 15 topics for dashboard
    cur = conn.execute("""
        SELECT t.topic_id, t.canonical_name, t.slug, t.topic_family, t.topic_subfamily,
               COUNT(ts.id) as match_count
        FROM topics t
        JOIN topic_segments ts ON t.topic_id = ts.topic_id
        GROUP BY t.topic_id
        ORDER BY match_count DESC
        LIMIT 15
    """)
    stats['top_topics'] = cur.fetchall()

    with open(os.path.join(OUTPUT_DIR, 'stats.json'), 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"  stats.json: {stats['total_works']} works, {stats['total_segments']} segments, {stats['total_words']:,} words, {stats['total_topics']} topics")


def export_topics_index(conn):
    """Export all topics with match counts."""
    topics_dir = os.path.join(OUTPUT_DIR, 'topics')
    ensure_dir(topics_dir)

    cur = conn.execute("""
        SELECT t.topic_id, t.canonical_name, t.slug, t.topic_family,
               t.topic_subfamily, t.definition, t.pkd_relevance, t.status,
               COUNT(ts.id) as match_count
        FROM topics t
        LEFT JOIN topic_segments ts ON t.topic_id = ts.topic_id
        GROUP BY t.topic_id
        ORDER BY match_count DESC
    """)
    topics = cur.fetchall()

    with open(os.path.join(topics_dir, 'index.json'), 'w') as f:
        json.dump(topics, f, indent=2)

    print(f"  topics/index.json: {len(topics)} topics")
    return topics


def export_topic_details(conn, topics):
    """Export per-topic detail with matched segments and works."""
    topics_dir = os.path.join(OUTPUT_DIR, 'topics')

    for topic in topics:
        topic_id = topic['topic_id']
        slug = topic['slug']

        # Get matched segments with context windows (limit to top 100 for size)
        cur = conn.execute("""
            SELECT ts.seg_id, ts.match_type, ts.matched_text, ts.context_window,
                   s.title as seg_title, s.segment_type, s.position,
                   s.page_start, s.page_end,
                   w.title as work_title, w.slug as work_slug, w.work_id
            FROM topic_segments ts
            JOIN segments s ON ts.seg_id = s.seg_id
            JOIN works w ON s.work_id = w.work_id
            WHERE ts.topic_id = ?
            ORDER BY w.year_published, s.position
            LIMIT 100
        """, (topic_id,))
        matched_segments = cur.fetchall()

        # Get matched works with counts
        cur = conn.execute("""
            SELECT w.work_id, w.title, w.slug, w.year_published,
                   tw.relevance,
                   (SELECT COUNT(*) FROM topic_segments ts2
                    JOIN segments s2 ON ts2.seg_id = s2.seg_id
                    WHERE ts2.topic_id = ? AND s2.work_id = w.work_id) as match_count
            FROM topic_works tw
            JOIN works w ON tw.work_id = w.work_id
            WHERE tw.topic_id = ?
            ORDER BY match_count DESC
        """, (topic_id, topic_id))
        matched_works = cur.fetchall()

        # Get aliases
        cur = conn.execute("""
            SELECT alias, alias_type FROM topic_aliases WHERE topic_id = ?
        """, (topic_id,))
        aliases = cur.fetchall()

        detail = {
            'topic_id': topic['topic_id'],
            'canonical_name': topic['canonical_name'],
            'slug': topic['slug'],
            'topic_family': topic['topic_family'],
            'topic_subfamily': topic['topic_subfamily'],
            'definition': topic['definition'],
            'pkd_relevance': topic['pkd_relevance'],
            'status': topic['status'],
            'match_count': topic['match_count'],
            'aliases': aliases,
            'matched_works': matched_works,
            'matched_segments': matched_segments,
        }

        with open(os.path.join(topics_dir, f"{slug}.json"), 'w') as f:
            json.dump(detail, f, indent=2)

    print(f"  topics/{{slug}}.json: {len(topics)} files")


def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        sys.exit(1)

    ensure_dir(OUTPUT_DIR)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory

    print("Exporting PKD Scholar data to JSON...")
    works = export_works_index(conn)
    export_work_details(conn, works)
    export_segments(conn)
    export_search_index(conn)
    export_stats(conn)
    topics = export_topics_index(conn)
    export_topic_details(conn, topics)

    conn.close()
    print("Done.")


if __name__ == '__main__':
    main()
