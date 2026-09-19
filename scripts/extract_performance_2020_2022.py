"""Extract average performance per question for 2020, 2021, 2022.

Graph pages:
  2020 P2 page 197
  2021 P1 page 188
  2022 P1 page 200
Add more as identified.
"""
import pdfplumber
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "diagnostic_reports"
OUT = ROOT / "data" / "processed" / "diagnostics"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
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


def extract_page(pdf_path, page_num, paper, year):
    pdf = pdfplumber.open(pdf_path)
    page = pdf.pages[page_num - 1]
    words = page.extract_words()
    pdf.close()

    # Bar labels: percentages in the plot area (x > 110, y between 350 and 750)
    bars = []
    for w in words:
        text = w["text"]
        x = w["x0"]
        y = w["top"]
        if "%" not in text:
            continue
        if x < 110 or x > 400:
            continue
        if y < 350 or y > 780:
            continue
        # Extract numeric value
        digits = "".join(c for c in text if c.isdigit())
        if not digits:
            continue
        val = int(digits)
        if val < 0 or val > 100:
            continue
        bars.append({"x": round(x, 1), "y": round(y, 1),
                     "raw": text, "value": val})

    # Sort by x, take first N (question count)
    bars.sort(key=lambda b: b["x"])

    # Deduplicate consecutive near-identical x (from multi-digit OCR)
    seen = []
    for b in bars:
        if seen and abs(b["x"] - seen[-1]["x"]) < 5:
            # Same bar, keep the one with cleaner raw text
            if len(b["raw"]) < len(seen[-1]["raw"]):
                seen[-1] = b
            continue
        seen.append(b)

    # Assign to questions 1..N
    rows = []
    for i, b in enumerate(seen, start=1):
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
    for year, page, paper in TARGETS:
        path = find_pdf(year)
        if not path:
            print(f"{year}: MISSING PDF")
            continue
        rows = extract_page(path, page, paper, year)
        print(f"{year} {paper} page {page}: {len(rows)} questions extracted")
        for r in rows:
            print(f"  Q{r['question_number']:2d}: {r['avg_performance_pct']}%  ({r['raw_label']})")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    out = OUT / "diagnostic_performance_extended.csv"
    df.to_csv(out, index=False)
    print()
    print("Wrote:", out)
    print("Total rows:", len(df))


if __name__ == "__main__":
    main()
