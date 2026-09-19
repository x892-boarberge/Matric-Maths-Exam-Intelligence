"""Extract per-question performance by matching bars to axis labels."""
import pdfplumber
from pathlib import Path
import pandas as pd
import re

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "diagnostic_reports"
OUT = ROOT / "data" / "processed" / "diagnostics"

TARGETS = [
    (2020, 197, "P2"),
    (2021, 188, "P1"),
    (2022, 200, "P1"),
]


def find_pdf(year):
    for pat in [str(year) + "_maths_*.pdf", "*" + str(year) + "*maths*.pdf"]:
        m = list(RAW.glob(pat))
        if m:
            return m[0]
    return None


def extract_page(pdf_path, page_num, paper, year):
    pdf = pdfplumber.open(pdf_path)
    page = pdf.pages[page_num - 1]
    words = page.extract_words()
    pdf.close()

    # Step 1: Find x-axis labels (bare digits at the bottom of the plot)
    axis_words = [w for w in words
                  if re.match(r"^\d+$", w["text"])
                  and 640 < w["top"] < 730
                  and 100 < w["x0"] < 400]
    axis_words.sort(key=lambda w: (round(w["x0"]), w["top"]))

    # Merge multi-digit labels (e.g. "1" + "0" => "10")
    merged = []
    for w in axis_words:
        if merged and abs(w["x0"] - merged[-1]["x"]) < 3:
            merged[-1]["text"] += w["text"]
        else:
            merged.append({"x": round(w["x0"], 1), "text": w["text"]})

    q_axis = []
    for w in merged:
        try:
            n = int(w["text"])
        except ValueError:
            continue
        if 1 <= n <= 20:
            q_axis.append({"q": n, "x": w["x"]})

    # Step 2: Find bar labels in the plot area
    bars = []
    for w in words:
        text = w["text"]
        x = w["x0"]
        y = w["top"]
        if "%" not in text:
            continue
        if x < 110 or x > 400:
            continue
        if y < 350 or y > 640:
            continue
        digits = "".join(c for c in text if c.isdigit())
        if not digits:
            continue
        val = int(digits)
        if val < 0 or val > 100:
            continue
        bars.append({"x": x, "y": y, "raw": text, "value": val})

    # Step 3: Match each bar to nearest axis label with max distance 10
    matched = {}
    for b in bars:
        if not q_axis:
            continue
        nearest = min(q_axis, key=lambda q: abs(q["x"] - b["x"]))
        dist = abs(nearest["x"] - b["x"])
        if dist > 10:
            continue
        qn = nearest["q"]
        if qn not in matched or dist < matched[qn]["dist"]:
            matched[qn] = {"value": b["value"], "raw": b["raw"], "dist": dist}

    rows = []
    for qn in sorted(matched.keys()):
        rows.append({
            "year": year,
            "paper": paper,
            "question_number": qn,
            "avg_performance_pct": matched[qn]["value"],
            "source_page": page_num,
            "raw_label": matched[qn]["raw"],
        })
    return rows, q_axis


def main():
    all_rows = []
    for year, page, paper in TARGETS:
        path = find_pdf(year)
        if not path:
            print(str(year) + ": MISSING PDF")
            continue
        rows, q_axis = extract_page(path, page, paper, year)
        print(str(year) + " " + paper + " page " + str(page) + ": "
              + str(len(q_axis)) + " axis labels, "
              + str(len(rows)) + " bars matched")
        for r in rows:
            print("  Q" + str(r["question_number"]) + ": "
                  + str(r["avg_performance_pct"]) + "%")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    out = OUT / "diagnostic_performance_extended.csv"
    df.to_csv(out, index=False)
    print()
    print("Wrote: " + str(out))
    print("Total rows: " + str(len(df)))


if __name__ == "__main__":
    main()
