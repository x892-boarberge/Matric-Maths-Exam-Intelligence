"""Extract per-question performance with proper question-axis matching."""
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

    # Find question-axis labels: Q1, Q2, ... Q12
    q_labels = []
    for w in words:
        m = re.match(r"^Q(\d+)$", w["text"])
        if m:
            q_labels.append({
                "q": int(m.group(1)),
                "x": round(w["x0"], 1),
                "y": round(w["top"], 1),
            })

    # Find y-axis x-position (the leftmost % labels)
    y_axis_x = None
    for w in words:
        if "%" in w["text"] and w["x0"] < 120:
            if y_axis_x is None or w["x0"] < y_axis_x:
                y_axis_x = w["x0"]

    # Find bar labels: % values in the plot area, not at y-axis x
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
        # Skip if this is the y-axis column
        if y_axis_x is not None and abs(x - y_axis_x) < 5:
            continue
        digits = "".join(c for c in text if c.isdigit())
        if not digits:
            continue
        val = int(digits)
        if val < 0 or val > 100:
            continue
        bars.append({"x": x, "y": y, "raw": text, "value": val})

    # Match each bar to the nearest question label by x
    matched = {}
    for b in bars:
        if not q_labels:
            continue
        nearest = min(q_labels, key=lambda q: abs(q["x"] - b["x"]))
        dist = abs(nearest["x"] - b["x"])
        if dist > 15:  # too far from any question
            continue
        qn = nearest["q"]
        # If already assigned, keep the closer one
        if qn in matched:
            if dist < matched[qn]["dist"]:
                matched[qn] = {"value": b["value"], "raw": b["raw"], "dist": dist}
        else:
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
    return rows, q_labels


def main():
    all_rows = []
    for year, page, paper in TARGETS:
        path = find_pdf(year)
        if not path:
            print(str(year) + ": MISSING PDF")
            continue
        rows, q_labels = extract_page(path, page, paper, year)
        print(str(year) + " " + paper + " page " + str(page) + ": " + str(len(q_labels)) + " axis labels, " + str(len(rows)) + " matched")
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
