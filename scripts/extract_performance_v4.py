"""Extract performance bars by sorting on x position."""
import pdfplumber
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "diagnostic_reports"
OUT = ROOT / "data" / "processed" / "diagnostics"

TARGETS = [
    (2020, 197, "P2", 11),
    (2021, 188, "P1", 12),
    (2022, 200, "P1", 12),
]


def find_pdf(year):
    for pat in [str(year) + "_maths_*.pdf", "*" + str(year) + "*maths*.pdf"]:
        m = list(RAW.glob(pat))
        if m:
            return m[0]
    return None


def extract_page(pdf_path, page_num, paper, year, n_questions):
    pdf = pdfplumber.open(pdf_path)
    page = pdf.pages[page_num - 1]
    words = page.extract_words()
    pdf.close()

    # Collect any % label in the plot area (x >= 115 to exclude y-axis)
    bars = []
    for w in words:
        text = w["text"]
        x = w["x0"]
        y = w["top"]
        if "%" not in text:
            continue
        if x < 115 or x > 400:
            continue
        if y < 350 or y > 650:
            continue
        digits = "".join(c for c in text if c.isdigit())
        if not digits:
            continue
        val = int(digits)
        if val < 0 or val > 100:
            continue
        bars.append({"x": x, "value": val, "raw": text})

    # Sort by x
    bars.sort(key=lambda b: b["x"])

    # Deduplicate near-identical x positions
    final = []
    for b in bars:
        if final and abs(b["x"] - final[-1]["x"]) < 8:
            if len(b["raw"]) < len(final[-1]["raw"]):
                final[-1] = b
            continue
        final.append(b)

    # Take first n_questions bars
    final = final[:n_questions]

    rows = []
    for i, b in enumerate(final, start=1):
        rows.append({
            "year": year,
            "paper": paper,
            "question_number": i,
            "avg_performance_pct": b["value"],
            "source_page": page_num,
            "raw_label": b["raw"],
        })
    return rows


def main():
    all_rows = []
    for year, page, paper, n in TARGETS:
        path = find_pdf(year)
        if not path:
            print(str(year) + ": MISSING PDF")
            continue
        rows = extract_page(path, page, paper, year, n)
        print(str(year) + " " + paper + " page " + str(page) + ": " + str(len(rows)) + " of " + str(n))
        for r in rows:
            print("  Q" + str(r["question_number"]) + ": " + str(r["avg_performance_pct"]) + "%")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    out = OUT / "diagnostic_performance_extended.csv"
    df.to_csv(out, index=False)
    print()
    print("Wrote: " + str(out))
    print("Total rows: " + str(len(df)))


if __name__ == "__main__":
    main()
