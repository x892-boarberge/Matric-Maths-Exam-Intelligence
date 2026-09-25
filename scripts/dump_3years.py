import pymupdf
from pathlib import Path

PDF_DIR = Path("data/raw/diagnostic_reports")

# User's earlier ranges
RANGES = {
    2015: (150, 174),
    2018: (132, 150),
    2019: (177, 201),
}

for year, (start, end) in RANGES.items():
    pdf = PDF_DIR / f"{year}_maths_diagnostic_part1.pdf"
    doc = pymupdf.open(pdf)
    print(f"=== {year} ({len(doc)} pages) — user range {start}-{end} ===")
    print()
    # Dump pages around range
    for p in range(max(1, start-2), min(end+3, len(doc)+1)):
        text = doc[p-1].get_text("text")
        first = text.strip().split("\n")[0][:80] if text.strip() else "(EMPTY)"
        print(f"  page {p}: {len(text):>5} chars | {first}")
    print()
    # Search whole doc for MATHEMATICS
    maths_pages = []
    question_pages = []
    for i in range(len(doc)):
        text = doc[i].get_text("text")
        if "MATHEMATICS" in text.upper():
            maths_pages.append(i+1)
        if "QUESTION 1" in text.upper() and "ALGEBRA" in text.upper():
            question_pages.append(i+1)
    print(f"  Pages containing 'MATHEMATICS': {maths_pages[:10]}")
    print(f"  Pages containing 'QUESTION 1 + ALGEBRA': {question_pages[:10]}")
    print()