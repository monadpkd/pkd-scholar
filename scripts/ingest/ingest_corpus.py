"""
Stage 0: Corpus Intake

Scans corpus/ directory for PDFs, extracts text with PyMuPDF,
assigns stable work IDs, stores metadata and raw text.

Inputs:  corpus/ directory with PDFs organized by source lane
         corpus/lane_a/fiction/   — novels, short stories
         corpus/lane_a/essays/    — PKD essays, speeches
         corpus/lane_a/exegesis/  — Exegesis volumes
         corpus/lane_b/           — contextual psychology sources
         corpus/lane_c/           — secondary scholarship

Outputs: Populated works table + segments table (one segment per page)

Deterministic: Yes (no LLM)
Libraries: PyMuPDF (fitz), pathlib
"""

import re
import sqlite3
from pathlib import Path


def slugify(name: str) -> str:
    """Convert a name to a URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


# Map known filenames to clean titles and mnemonics
KNOWN_WORKS = {
    "book_pkd_ubik": ("Ubik", "UBIK", "novel", 1969),
    "the_valis_trilogy": ("The VALIS Trilogy", "VALISTRI", "novel", 1981),
    "five_great_novels": ("Five Great Novels (incl. Three Stigmata)", "5NOVELS", "novel", 1965),
    "the_exegesis_of_philip_k_dick": ("The Exegesis of Philip K. Dick", "EXEGESIS", "exegesis", 1974),
    "the_android_and_the_human": ("The Android and the Human", "ANDROHUM", "essay", 1972),
    "how_to_build_a_universe": ("How to Build a Universe That Doesn't Fall Apart Two Days Later", "BUILDUNIVERSE", "essay", 1978),
    "cosmogony_and_cosmology": ("Cosmogony and Cosmology", "COSMCOSM", "essay", 1978),
    "schizophrenia_and_the_book_of_changes": ("Schizophrenia and the Book of Changes", "SCHIZBOC", "essay", 1965),
}


def lookup_work(filename: str) -> tuple[str, str, str, int | None]:
    """Look up known work metadata. Returns (title, mnemonic, work_type, year)."""
    slug = slugify(Path(filename).stem)
    # Remove common prefixes
    clean = slug.replace("oceanofpdfcom-", "oceanofpdfcom_")
    clean = re.sub(r'^_+', '', clean)

    normalized = clean.replace("-", "_")
    for key, (title, mnemonic, work_type, year) in KNOWN_WORKS.items():
        if key in normalized:
            return title, mnemonic, work_type, year

    # Fallback
    mnemonic = slugify(Path(filename).stem).upper().replace("-", "")[:8]
    return Path(filename).stem, mnemonic, "unknown", None


def infer_work_type(pdf_path: Path) -> str:
    """Infer work type from subdirectory name."""
    parts = pdf_path.parts
    for part in parts:
        if part == "fiction":
            return "novel"
        elif part == "essays":
            return "essay"
        elif part == "exegesis":
            return "exegesis"
        elif part == "criticism":
            return "criticism"
        elif part == "psychology":
            return "psychology_source"
    return "unknown"


def make_work_id(mnemonic: str, lane: str, year: int | None = None) -> str:
    """Generate stable work ID following pkd-archive namespace.
    Format: PKD-{TYPE}-{YYYY}-{MNEMONIC} or PKD-{TYPE}-{MNEMONIC} if no year.
    """
    type_code = {"A": "WRK", "B": "CTX", "C": "SRC"}[lane]
    if year:
        return f"PKD-{type_code}-{year}-{mnemonic}"
    return f"PKD-{type_code}-{mnemonic}"


def extract_text(pdf_path: Path) -> tuple[list[str], int]:
    """Extract text from PDF using PyMuPDF. Returns (page_texts, page_count)."""
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        return pages, len(pages)
    except Exception as e:
        print(f"  [warn] Failed to extract {pdf_path.name}: {e}")
        return [], 0


def run(conn: sqlite3.Connection, corpus_dir: Path):
    """Scan corpus directory and ingest PDFs."""
    lane_map = {
        "lane_a": "A",
        "lane_b": "B",
        "lane_c": "C",
    }

    if not corpus_dir.exists():
        print(f"  [skip] Corpus directory not found: {corpus_dir}")
        print(f"  [skip] Create {corpus_dir}/lane_a/, lane_b/, lane_c/ and add PDFs")
        return

    processed = 0
    created = 0
    total_pages = 0

    for lane_dir, lane_code in lane_map.items():
        lane_path = corpus_dir / lane_dir
        if not lane_path.exists():
            continue

        for pdf_path in sorted(lane_path.glob("**/*.pdf")):
            title, mnemonic, work_type, year = lookup_work(pdf_path.name)
            work_id = make_work_id(mnemonic, lane_code, year)

            # Use subdirectory to override work_type if lookup returned unknown
            if work_type == "unknown":
                work_type = infer_work_type(pdf_path)

            # Check if already ingested
            existing = conn.execute(
                "SELECT work_id FROM works WHERE work_id = ?", (work_id,)
            ).fetchone()

            if existing:
                processed += 1
                continue

            pages, page_count = extract_text(pdf_path)
            full_text = "\n\n".join(pages)
            status = "extracted" if full_text.strip() else "ocr_needed"
            word_count = len(full_text.split()) if full_text else 0

            # Insert work
            conn.execute(
                "INSERT INTO works (work_id, title, slug, work_type, source_lane, "
                "author, year_published, file_path, page_count, extraction_status, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (work_id, title, slugify(title), work_type, lane_code,
                 "Philip K. Dick", year, str(pdf_path), page_count, status,
                 f"Words: {word_count:,}")
            )

            # Insert one segment per page (raw chunking — Stage 1 will refine)
            for i, page_text in enumerate(pages):
                if not page_text.strip():
                    continue
                seg_id = f"PKD-SEG-{mnemonic}-P{i+1:04d}"
                conn.execute(
                    "INSERT INTO segments (seg_id, work_id, title, segment_type, "
                    "position, page_start, page_end, raw_text, word_count) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (seg_id, work_id, f"{title} — Page {i+1}", "page",
                     i+1, i+1, i+1, page_text, len(page_text.split()))
                )

            created += 1
            processed += 1
            total_pages += page_count
            print(f"  [{lane_code}] {title} → {work_id} ({page_count} pages, {word_count:,} words, {status})")

    conn.commit()
    print(f"  [corpus] Processed {processed}, created {created}, total pages: {total_pages}")
