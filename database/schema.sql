-- pkd-scholar unified schema
-- Three-lane evidence architecture for PKD fiction studies
-- Adapted from QueryPat (t3dy/QueryPat)

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ============================================================
-- CORE CORPUS TABLES
-- ============================================================

-- Works: novels, stories, essays, Exegesis sections, secondary sources
-- ID format follows pkd-archive namespace: PKD-{TYPE}-{YYYY}-{MNEMONIC}
-- Types: WRK (work), INT (interview), LTR (letter), etc.
CREATE TABLE works (
    work_id         TEXT PRIMARY KEY,           -- PKD-WRK-1969-UBIK, PKD-WRK-1968-DADOES, PKD-SRC-1989-SUTIN
    title           TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    work_type       TEXT NOT NULL,              -- novel, short_story, essay, interview, exegesis, letter, criticism, biography, psychology_source
    source_lane     TEXT NOT NULL,              -- A (primary), B (contextual), C (secondary)
    author          TEXT DEFAULT 'Philip K. Dick',
    year_published  INTEGER,
    year_written    INTEGER,
    collection      TEXT,                       -- e.g., "The Collected Stories Vol. 2"
    publisher       TEXT,
    page_count      INTEGER,
    file_path       TEXT,                       -- path to source PDF
    extraction_status TEXT DEFAULT 'pending',   -- pending, extracted, ocr_needed, ocr_done, failed
    notes           TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_works_type ON works(work_type);
CREATE INDEX idx_works_lane ON works(source_lane);

-- Work segments: chapters, scenes, date-blocks, sections
CREATE TABLE segments (
    seg_id          TEXT PRIMARY KEY,           -- PKD-SEG-UBIK-CH03, PKD-SEG-EXEG-197403-001
    work_id         TEXT NOT NULL REFERENCES works(work_id),
    title           TEXT,
    segment_type    TEXT NOT NULL,              -- chapter, scene, date_block, section, paragraph_cluster
    position        INTEGER,                   -- order within work
    page_start      INTEGER,
    page_end        INTEGER,
    char_offset_start INTEGER,
    char_offset_end INTEGER,
    raw_text        TEXT,
    word_count      INTEGER,
    date_start      TEXT,                      -- ISO partial: "1974", "1974-03"
    date_end        TEXT,
    date_display    TEXT,                      -- human-readable
    date_confidence TEXT,                      -- exact, approximate, circa, inferred, unknown
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_segments_work ON segments(work_id);
CREATE INDEX idx_segments_type ON segments(segment_type);

-- ============================================================
-- TOPIC & VOCABULARY TABLES
-- ============================================================

-- Topics: psychology topics, AI/robot topics, thematic categories
-- Psychology topics canonical source: monadpkd/pkd-archive psychology/pkd_psychology_topics.json
-- ID format: PKD-PSY-{MNEMONIC} for psychology, PKD-AIT-{MNEMONIC} for AI themes
CREATE TABLE topics (
    topic_id        TEXT PRIMARY KEY,           -- PKD-PSY-PARANOIA, PKD-AIT-ECONGATEKEEPER
    canonical_name  TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    topic_family    TEXT NOT NULL,              -- psychology, ai_automation, capitalism, metaphysics, epistemology
    topic_subfamily TEXT,                       -- clinical, psychoanalytic, jungian, existential, neuropsych, anti_psychiatric, pkd_specific
    definition      TEXT,                       -- scholarly definition (plain English)
    pkd_relevance   TEXT,                       -- why this matters in PKD
    status          TEXT DEFAULT 'provisional', -- provisional, accepted, contested, rejected
    review_state    TEXT DEFAULT 'unreviewed',  -- unreviewed, machine_drafted, human_reviewed, publication_ready
    confidence      TEXT DEFAULT 'medium',      -- high, medium, low
    priority        INTEGER DEFAULT 0,          -- build order priority (1 = first wave)
    notes           TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_topics_family ON topics(topic_family);
CREATE INDEX idx_topics_status ON topics(status);
CREATE INDEX idx_topics_priority ON topics(priority);

-- Topic aliases: variant labels, synonyms
CREATE TABLE topic_aliases (
    alias_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id        TEXT NOT NULL REFERENCES topics(topic_id),
    alias           TEXT NOT NULL,
    alias_type      TEXT DEFAULT 'synonym',     -- synonym, variant, abbreviation, related_term
    UNIQUE(topic_id, alias)
);

-- Topic relationships
CREATE TABLE topic_links (
    link_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_a         TEXT NOT NULL REFERENCES topics(topic_id),
    topic_b         TEXT NOT NULL REFERENCES topics(topic_id),
    link_type       TEXT NOT NULL,              -- related, parent_child, synonym, contrast, overlaps
    notes           TEXT,
    UNIQUE(topic_a, topic_b, link_type)
);

-- ============================================================
-- EVIDENCE TABLES (Three-Lane Architecture)
-- ============================================================

-- Claims: traceable assertions connecting topics to evidence
CREATE TABLE claims (
    claim_id        TEXT PRIMARY KEY,           -- PKD-CLM-PARANOIA-UBIK-001
    topic_id        TEXT NOT NULL REFERENCES topics(topic_id),
    claim_text      TEXT NOT NULL,              -- the assertion
    claim_type      TEXT NOT NULL,              -- definition, symptom_description, causal_theory, treatment_model, allegorical_use, self_report, critique, comparison, unresolved
    source_lane     TEXT NOT NULL,              -- A, B, C
    source_mode     TEXT NOT NULL,              -- fiction, exegesis, letter, interview, criticism
    psych_mode      TEXT,                       -- clinical, psychoanalytic, jungian, existential, neuropsych, anti_psychiatric, mystical, popular_psych, metaphorical
    ai_mode         TEXT,                       -- economic_gatekeeper, diagnostic_authority, psychological_regulator, surveillance, reality_infrastructure, predictive_bureaucracy, production_automation, machine_sovereign
    speaker_type    TEXT,                       -- author, character, narrator, critic
    stance          TEXT,                       -- endorsed, dramatized, mentioned, questioned, contradicted
    confidence      TEXT DEFAULT 'medium',      -- high, medium, low
    seg_id          TEXT REFERENCES segments(seg_id),
    work_id         TEXT REFERENCES works(work_id),
    page_ref        TEXT,                       -- "p. 47" or "pp. 112-115"
    notes           TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_claims_topic ON claims(topic_id);
CREATE INDEX idx_claims_lane ON claims(source_lane);
CREATE INDEX idx_claims_work ON claims(work_id);

-- Evidence packets: assembled per-topic bundles
CREATE TABLE evidence_packets (
    packet_id       TEXT PRIMARY KEY,           -- PKD-EVP-PARANOIA-001
    topic_id        TEXT NOT NULL REFERENCES topics(topic_id),
    packet_type     TEXT NOT NULL,              -- fiction_evidence, exegesis_evidence, secondary_evidence, contradiction, chronology
    title           TEXT,
    summary         TEXT,
    lane            TEXT NOT NULL,              -- A, B, C, cross_lane
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_packets_topic ON evidence_packets(topic_id);

-- Evidence excerpts: individual passages within packets
CREATE TABLE evidence_excerpts (
    excerpt_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    packet_id       TEXT NOT NULL REFERENCES evidence_packets(packet_id),
    seg_id          TEXT REFERENCES segments(seg_id),
    work_id         TEXT REFERENCES works(work_id),
    excerpt_type    TEXT NOT NULL,              -- paraphrase, brief_quote, page_reference, summary
    text            TEXT NOT NULL,              -- the paraphrase or brief quote
    original_page   TEXT,                       -- page/chunk reference
    char_start      INTEGER,
    char_end        INTEGER,
    context_note    TEXT,                       -- editorial context
    fair_use_check  TEXT DEFAULT 'unchecked'    -- unchecked, passed, flagged, revised
);

-- Contradiction lists (first-class, per Ted's spec)
CREATE TABLE contradictions (
    contradiction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id        TEXT NOT NULL REFERENCES topics(topic_id),
    claim_a_id      TEXT REFERENCES claims(claim_id),
    claim_b_id      TEXT REFERENCES claims(claim_id),
    description     TEXT NOT NULL,              -- what the contradiction is
    tension_type    TEXT,                       -- temporal_shift, genre_difference, self_revision, interpretive_dispute
    notes           TEXT
);

-- ============================================================
-- PERSONS & SCHOOLS
-- ============================================================

-- Persons: real people + fictional characters
-- Follows pkd-archive: PKD-PER-{MNEMONIC} for real people, PKD-CHR-{MNEMONIC} for characters
CREATE TABLE persons (
    person_id       TEXT PRIMARY KEY,           -- PKD-PER-JUNG, PKD-CHR-DECKARD
    canonical_name  TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    person_type     TEXT NOT NULL,              -- historical, fictional_character, scholar, biographer, critic
    source_work     TEXT,                       -- for fictional characters
    description     TEXT,
    relevance       TEXT,                       -- why they matter for PKD studies
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Schools of thought
CREATE TABLE schools (
    school_id       TEXT PRIMARY KEY,           -- PKD-SCH-JUNGIAN, PKD-SCH-ANTIPSYCH
    canonical_name  TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    domain          TEXT NOT NULL,              -- psychology, philosophy, theology, political_economy, cybernetics
    description     TEXT,
    key_figures     TEXT,                       -- comma-separated person_ids
    pkd_connection  TEXT                        -- how Dick engaged with this school
);

-- ============================================================
-- MACHINE ROLE TABLES (AI/Robot Study)
-- ============================================================

-- Machine roles detected in fiction
CREATE TABLE machine_roles (
    role_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    seg_id          TEXT NOT NULL REFERENCES segments(seg_id),
    work_id         TEXT NOT NULL REFERENCES works(work_id),
    machine_type    TEXT NOT NULL,              -- economic_gatekeeper, diagnostic_authority, psychological_regulator, surveillance, reality_infrastructure, predictive_bureaucracy, production_automation, machine_sovereign
    human_response  TEXT,                       -- compliance, circumvention, sabotage, identity_manipulation, black_market, philosophical_revelation
    description     TEXT,
    page_ref        TEXT,
    confidence      TEXT DEFAULT 'medium'
);

CREATE INDEX idx_machine_roles_work ON machine_roles(work_id);
CREATE INDEX idx_machine_roles_type ON machine_roles(machine_type);

-- ============================================================
-- CROSS-LINK TABLES
-- ============================================================

-- Topic ↔ Segment links
CREATE TABLE topic_segments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id        TEXT NOT NULL REFERENCES topics(topic_id),
    seg_id          TEXT NOT NULL REFERENCES segments(seg_id),
    match_type      TEXT NOT NULL,              -- exact_text, alias, fuzzy, conceptual, llm_tagged
    link_confidence INTEGER DEFAULT 3,          -- 1=strongest, 5=weakest
    matched_text    TEXT,                       -- the actual phrase found
    context_window  TEXT,                       -- surrounding text
    UNIQUE(topic_id, seg_id, match_type)
);

-- Topic ↔ Work links (aggregated)
CREATE TABLE topic_works (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id        TEXT NOT NULL REFERENCES topics(topic_id),
    work_id         TEXT NOT NULL REFERENCES works(work_id),
    relevance       TEXT DEFAULT 'mentioned',   -- central, significant, mentioned, peripheral
    notes           TEXT,
    UNIQUE(topic_id, work_id)
);

-- Topic ↔ Person links
CREATE TABLE topic_persons (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id        TEXT NOT NULL REFERENCES topics(topic_id),
    person_id       TEXT NOT NULL REFERENCES persons(person_id),
    relationship    TEXT,                       -- theorist, character_embodying, biographer_discussing, critic_analyzing
    UNIQUE(topic_id, person_id)
);

-- Topic ↔ School links
CREATE TABLE topic_schools (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id        TEXT NOT NULL REFERENCES topics(topic_id),
    school_id       TEXT NOT NULL REFERENCES schools(school_id),
    relationship    TEXT,                       -- originates_from, critiques, adapts, dramatizes
    UNIQUE(topic_id, school_id)
);

-- ============================================================
-- DICTIONARY ENTRIES (Lane D — Synthesis)
-- ============================================================

CREATE TABLE dictionary_entries (
    entry_id        TEXT PRIMARY KEY,           -- PKD-ENT-PARANOIA
    topic_id        TEXT NOT NULL UNIQUE REFERENCES topics(topic_id),
    definition      TEXT,                       -- scholarly definition
    pkd_relevance   TEXT,                       -- why this matters
    in_the_fiction   TEXT,                      -- Lane A evidence prose
    in_the_exegesis  TEXT,                      -- Lane A (Exegesis) evidence prose
    intellectual_background TEXT,               -- Lane B context prose
    scholarly_debate TEXT,                      -- Lane C commentary prose
    chronology      TEXT,                       -- temporal development
    key_passages    TEXT,                       -- curated passage list (JSON array)
    competing_interpretations TEXT,             -- contradiction summary
    related_entries TEXT,                       -- JSON array of topic_ids
    related_works   TEXT,                       -- JSON array of work_ids
    related_persons TEXT,                       -- JSON array of person_ids
    related_schools TEXT,                       -- JSON array of school_ids
    editorial_notes TEXT,
    open_questions  TEXT,
    status          TEXT DEFAULT 'draft',       -- draft, review, stable, contested
    word_count      INTEGER,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- ============================================================
-- AUDIT & PROVENANCE
-- ============================================================

CREATE TABLE pipeline_runs (
    run_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    stage           TEXT NOT NULL,
    script_name     TEXT NOT NULL,
    started_at      TEXT DEFAULT (datetime('now')),
    completed_at    TEXT,
    records_processed INTEGER,
    records_created INTEGER,
    records_updated INTEGER,
    errors          INTEGER DEFAULT 0,
    notes           TEXT
);
