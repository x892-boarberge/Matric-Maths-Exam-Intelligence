"""Find graph pages across all years, using multiple phrase variants."""
import pdfplumber
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "diagnostic_reports"

YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]

PHRASES = [
    "average performance per question",
    "average marks per question",
    "marks per question expressed",
    "performance per question",
]


def find_pdf(year):
    for pat in [f"{year}_maths_*.pdf", f"*{year}*maths*.pdf"]:
        m = list(RAW.glob(pat))
        if m:
            return m[0]
    return None


def main():
    print(f"{'Year':6s} {'P1 page':10s} {'P2 page':10s} {'Variant'}")
    print("-" * 70)
    for year in YEARS:
        path = find_pdf(year)
        if not path:
            print(f"{year:6d} {'MISSING':10s}")
            continue
        pdf = pdfplumber.open(path)
        p1_page = None
        p2_page = None
        variant = ""
        for i, pg in enumerate(pdf.pages):
            t = (pg.extract_text() or "").lower()
            for ph in PHRASES:
                if ph in t:
                    if "paper 1" in t and p1_page is None:
                        p1_page = i + 1
                    if "paper 2" in t and p2_page is None:
                        p2_page = i + 1
                    if not variant:
                        variant = ph
        print(f"{year:6d} {str(p1_page or '?'):10s} {str(p2_page or '?'):10s} {variant}")
        pdf.close()


if __name__ == "__main__":
    main()
