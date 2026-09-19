"""Dump percentages from a specific page for layout verification."""
import pdfplumber
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "diagnostic_reports"

PAGES = [
    (2014, 119, "P1"),
    (2015, 172, "P2"),
    (2016, 157, "P1"),
    (2017, 163, "P1"),
    (2018, 141, "P1"),
    (2019, 179, "P1"),
    (2020, 197, "P2"),
    (2021, 188, "P1"),
    (2022, 200, "P1"),
]


def find_pdf(year):
    for pat in [f"{year}_maths_*.pdf", f"*{year}*maths*.pdf"]:
        m = list(RAW.glob(pat))
        if m:
            return m[0]
    return None


def main():
    for year, page_num, paper in PAGES:
        path = find_pdf(year)
        if not path:
            print(f"\n=== {year} {paper} page {page_num} — MISSING PDF ===\n")
            continue
        try:
            pdf = pdfplumber.open(path)
            page = pdf.pages[page_num - 1]
            words = page.extract_words()
            pcts = [(round(w["x0"], 1), round(w["top"], 1), w["text"])
                    for w in words if "%" in w["text"]]
            print(f"\n=== {year} {paper} page {page_num} — {len(pcts)} percentages ===")
            for x, y, txt in pcts[:25]:
                print(f"  x={x:6.1f}  y={y:6.1f}  text={txt!r}")
            pdf.close()
        except Exception as e:
            print(f"\n=== {year} {paper} page {page_num} — ERROR: {e} ===\n")


if __name__ == "__main__":
    main()
