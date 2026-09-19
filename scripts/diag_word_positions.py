"""Extract words with positions from a specific page."""
import pdfplumber
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "diagnostic_reports"

YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2021
PAGE = int(sys.argv[2]) if len(sys.argv) > 2 else 188


def find_pdf(year):
    for pat in [f"{year}_maths_*.pdf", f"*{year}*maths*.pdf"]:
        m = list(RAW.glob(pat))
        if m:
            return m[0]
    return None


def main():
    path = find_pdf(YEAR)
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[PAGE - 1]
        words = page.extract_words()
        print(f"Page {PAGE}, {len(words)} words")
        print()
        for w in words:
            if "%" in w["text"] or w["text"].isdigit():
                print(f"  x={w['x0']:6.1f}  y={w['top']:6.1f}  text={w['text']!r}")


if __name__ == "__main__":
    main()
