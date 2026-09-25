import pymupdf
from pathlib import Path

PDF_DIR = Path("data/raw/diagnostic_reports")

SAMPLES = {
    2015: 161,
    2018: 142,
    2019: 180,
}

for year, p in SAMPLES.items():
    pdf = PDF_DIR / f"{year}_maths_diagnostic_part1.pdf"
    doc = pymupdf.open(pdf)
    print(f"=== {year} — page {p} (first 2000 chars) ===")
    text = doc[p-1].get_text("text")
    print(text[:2000])
    print()
    print("=" * 70)
    print()