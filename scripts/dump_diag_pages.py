"""Dump the first pages of a diagnostic report Maths section for inspection."""
import pdfplumber
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "diagnostic_reports"

YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2021
START = int(sys.argv[2]) if len(sys.argv) > 2 else 186
N_PAGES = int(sys.argv[3]) if len(sys.argv) > 3 else 3


def find_pdf(year):
    for pat in [f"{year}_maths_*.pdf", f"*{year}*maths*.pdf"]:
        matches = list(RAW.glob(pat))
        if matches:
            return matches[0]
    return None


def main():
    path = find_pdf(YEAR)
    if not path:
        print("PDF not found for", YEAR)
        return
    print("PDF:", path.name)
    print()
    with pdfplumber.open(path) as pdf:
        for i in range(START - 1, min(START - 1 + N_PAGES, len(pdf.pages))):
            page = pdf.pages[i]
            print("=" * 70)
            print(f"PAGE {i + 1}")
            print("=" * 70)
            text = page.extract_text() or "(no text)"
            print(text[:3000])
            tables = page.extract_tables()
            if tables:
                print()
                print(f"TABLES FOUND: {len(tables)}")
                for ti, t in enumerate(tables):
                    print(f"  --- table {ti} ---")
                    for row in t[:6]:
                        print("   ", row)
            print()


if __name__ == "__main__":
    main()
