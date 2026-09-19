"""Find graph pages in 2023, 2024, 2025 diagnostic PDFs."""
import pdfplumber
from pathlib import Path

RAW = Path("data/raw/diagnostic_reports")

PHRASES = [
    "average performance per question",
    "average marks per question",
    "performance per question",
    "average percentage performance per question",
]


def find_pdf(year):
    for pat in [str(year) + "_maths_*.pdf", "*" + str(year) + "*maths*.pdf"]:
        m = list(RAW.glob(pat))
        if m:
            return m[0]
    return None


def main():
    for year in [2023, 2024, 2025]:
        path = find_pdf(year)
        if not path:
            print(str(year) + ": MISSING PDF")
            continue
        print("=== " + str(year) + " (" + path.name + ") ===")
        pdf = pdfplumber.open(path)
        for i, pg in enumerate(pdf.pages):
            t = (pg.extract_text() or "").lower()
            for ph in PHRASES:
                if ph in t:
                    if "paper 1" in t:
                        print("  P1 graph: page " + str(i + 1) + "  (" + ph + ")")
                    if "paper 2" in t:
                        print("  P2 graph: page " + str(i + 1) + "  (" + ph + ")")
        pdf.close()
        print()


if __name__ == "__main__":
    main()
