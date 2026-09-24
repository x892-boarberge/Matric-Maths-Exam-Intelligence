"""
Phase 1.5: render exam PDF pages to PNG and build a question->page map.

Outputs:
  data/processed/diagrams/pages/<stem>_p<N>.png       (page images)
  data/processed/diagrams/question_page_map.json      ({stem: {"Q8": 5, ...}})
"""
import json
import re
from pathlib import Path

import pymupdf


ROOT = Path(__file__).resolve().parents[1]
EXAM_DIR = ROOT / "data" / "raw" / "exams"
OUT_DIR = ROOT / "data" / "processed" / "diagrams"
PAGES_DIR = OUT_DIR / "pages"
MAP_PATH = OUT_DIR / "question_page_map.json"

DPI = 120
ZOOM = DPI / 72.0
MATRIX = pymupdf.Matrix(ZOOM, ZOOM)

QUESTION_RE = re.compile(r"QUESTION\s+(\d+)", re.IGNORECASE)
# Also look for the first subquestion number on each page
SUBQ_RE = re.compile(r"^\s*(\d+)\.(\d+)", re.MULTILINE)


def process_pdf(pdf_path: Path):
    stem = pdf_path.stem
    doc = pymupdf.open(pdf_path)
    n_pages = len(doc)
    print(f"  {stem}: {n_pages} pages")

    q_to_page = {}          # {"8": 5, ...}
    page_texts = {}         # {page_num: text}

    for i, page in enumerate(doc):
        pnum = i + 1

        # --- render to PNG ---
        png_path = PAGES_DIR / f"{stem}_p{pnum}.png"
        if not png_path.exists():
            pix = page.get_pixmap(matrix=MATRIX, alpha=False)
            pix.save(str(png_path))

        # --- extract text ---
        text = page.get_text("text")
        page_texts[pnum] = text

        # --- find QUESTION N markers on this page ---
        for m in QUESTION_RE.finditer(text):
            qnum = m.group(1)
            # First occurrence wins (start of question)
            if qnum not in q_to_page:
                q_to_page[qnum] = pnum

    return {"n_pages": n_pages, "q_to_page": q_to_page}


def main():
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    EXAM_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(EXAM_DIR.glob("*_exam_maths.pdf"))
    print(f"Found {len(pdfs)} exam PDFs")
    print("=" * 60)

    full_map = {}
    for pdf in pdfs:
        try:
            result = process_pdf(pdf)
            full_map[pdf.stem] = result["q_to_page"]
        except Exception as e:
            print(f"  FAILED {pdf.name}: {e}")

    MAP_PATH.write_text(
        json.dumps(full_map, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print("=" * 60)
    print(f"Wrote map: {MAP_PATH}")
    print(f"Total page images: {len(list(PAGES_DIR.glob('*.png')))}")
    print(f"Papers mapped: {len(full_map)}")
    # Show one sample
    if full_map:
        sample_stem = sorted(full_map.keys())[0]
        print(f"\nSample: {sample_stem}")
        for q in sorted(full_map[sample_stem].keys(), key=lambda x: int(x))[:12]:
            print(f"  Q{q} -> page {full_map[sample_stem][q]}")


if __name__ == "__main__":
    main()
