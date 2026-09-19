"""For each year, find the page with 'Average performance per question'."""
import pdfplumber
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "diagnostic_reports"

YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]


def find_pdf(year):
    for pat in [f"{year}_maths_*.pdf", f"*{year}*maths*.pdf"]:
        m = list(RAW.glob(pat))
        if m:
            return m[0]
    return None


def main():
    print(f"{'Year':6s} {'Pages':6s} {'Graph pages':40s} {'Summary'}")
    print("-" * 90)
    for year in YEARS:
        path = find_pdf(year)
        if not path:
            print(f"{year:6d} {'?':6s} {'MISSING PDF':40s}")
            continue
        pdf = pdfplumber.open(path)
        n = len(pdf.pages)
        hits = []
        for i, pg in enumerate(pdf.pages):
            t = pg.extract_text() or ""
            if "Average performance per question" in t:
                hits.append(i + 1)
        summary = "2021-style" if hits else "NONE FOUND"
        pages_str = ",".join(str(h) for h in hits) if hits else "(no match)"
        print(f"{year:6d} {n:6d} {pages_str:40s} {summary}")
        pdf.close()


if __name__ == "__main__":
    main()
