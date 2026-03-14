"""
Stage 0: Corpus Intake

Scans corpus/ directory for PDFs, extracts text with PyMuPDF,
assigns stable work IDs, stores metadata and raw text.

Inputs:  corpus/ directory with PDFs organized by source lane
         corpus/lane_a/  — primary fiction, Exegesis, interviews
         corpus/lane_b/  — contextual psychology sources
         corpus/lane_c/  — secondary scholarship

Outputs: Populated works and segments tables

Deterministic: Yes (no LLM)
Libraries: PyMuPDF (fitz), pathlib
"""

import sqlite3
from pathlib import Path


def slugify(name: str) -> str:
    """Convert a name to a URL-safe slug."""
    import re
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def make_work_id(filename: str, lane: str) -> str:
    """Generate stable work ID following pkd-archive namespace.
    Format: PKD-{TYPE}-{YYYY}-{MNEMONIC}
    """
    type_code = {"A": "WRK", "B": "CTX", "C": "SRC"}[lane]
    mnemonic = slugify(Path(filename).stem).upper().replace("-", "")[:8]
    return f"PKD-{type_code}-{mnemonic}"


def extract_text(pdf_path: Path) -> tuple[str, int]:
    """Extract text from PDF using PyMuPDF. Returns (text, page_count)."""
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        return "\n\n".join(pages), len(pages)
    except Exception as e:
        print(f"  [warn] Failed to extract {pdf_path.name}: {e}")
        return "", 0


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

    for lane_dir, lane_code in lane_map.items():
        lane_path = corpus_dir / lane_dir
        if not lane_path.exists():
            continue

        for pdf_path in sorted(lane_path.glob("**/*.pdf")):
            work_id = make_work_id(pdf_path.stem, lane_code)

            # Check if already ingested
            existing = conn.execute(
                "SELECT work_id FROM works WHERE work_id = ?", (work_id,)
            ).fetchone()

            if existing:
                processed += 1
                continue

            text, page_count = extract_text(pdf_path)
            status = "extracted" if text else "ocr_needed"

            conn.execute(
                "INSERT INTO works (work_id, title, slug, work_type, source_lane, "
                "file_path, page_count, extraction_status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (work_id, pdf_path.stem, slugify(pdf_path.stem),
                 "unknown", lane_code, str(pdf_path), page_count, status)
            )
            created += 1
            processed += 1
            print(f"  [{lane_code}] {pdf_path.stem} → {work_id} ({page_count} pages, {status})")

    conn.commit()
    print(f"  [corpus] Processed {processed}, created {created}")
