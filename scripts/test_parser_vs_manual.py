"""
Test the parser against the 2023-2025 manual file.
If the parser output matches the manual rows, the parser can be trusted
for 2014-2022.
"""
import re
import pandas as pd
import pymupdf
from pathlib import Path

ROOT = Path(".").resolve()
PDF_DIR = ROOT / "data" / "raw" / "diagnostic_reports"

# Chapter 10 (Maths) start pages from the diagnostic PDFs
PAGE_RANGES = {
    2023: (213, 273),
    2024: (219, 287),
    2025: (230, 283),
}

TOPIC_MAP = {
    "ALGEBRA": "Algebra & Equations",
    "EQUATIONS AND INEQUALITIES": "Algebra & Equations",
    "SEQUENCES AND SERIES": "Sequences & Series",
    "PATTERNS": "Sequences & Series",
    "NUMBER PATTERNS": "Sequences & Series",
    "FUNCTIONS": "Functions & Graphs",
    "FINANCE": "Finance",
    "FINANCIAL MATHEMATICS": "Finance",
    "CALCULUS": "Calculus",
    "DIFFERENTIAL CALCULUS": "Calculus",
    "PROBABILITY": "Probability",
    "TRIGONOMETRY": "Trigonometry",
    "ANALYTICAL GEOMETRY": "Analytical Geometry",
    "EUCLIDEAN GEOMETRY": "Euclidean Geometry",
    "DATA HANDLING": "Statistics",
    "STATISTICS": "Statistics",
}


def clean_text(s):
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def strip_chart_garbage(s):
    s = re.sub(r"(?:\d+%\s*){3,}", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def map_topic(title):
    t = title.upper().strip()
    for key, val in TOPIC_MAP.items():
        if key in t:
            return val
    return "Unknown"


def parse_year(year, start, end):
    pdf = PDF_DIR / f"{year}_maths_diagnostic_part1.pdf"
    doc = pymupdf.open(pdf)
    n = len(doc)
    if end > n:
        end = n
    text = "\n".join(doc[p].get_text("text") for p in range(start - 1, end))

    q_pattern = re.compile(r"QUESTION\s+(\d+)\s*:\s*([A-Z][A-Za-z \-,/]+?)(?:\n|$)")
    matches = list(q_pattern.finditer(text))
    rows = []
    for i, m in enumerate(matches):
        qnum = m.group(1)
        qtitle = m.group(2).strip()
        for stop in ["PERFORMANCE", "COMMON", "GRAPH", "DIAGNOSTIC", "SUGGESTIONS"]:
            idx = qtitle.upper().find(stop)
            if idx > 0:
                qtitle = qtitle[:idx].strip()
        block_start = m.end()
        block_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[block_start:block_end]

        para_pattern = re.compile(r"\(([a-z])\)\s+(.+?)(?=\([a-z]\)\s+|\Z)", re.DOTALL)
        paras = para_pattern.findall(block)
        if not paras:
            continue

        topic = map_topic(qtitle)
        for letter, body in paras:
            body_clean = clean_text(strip_chart_garbage(body))
            if len(body_clean) < 40:
                continue
            rows.append({
                "year": year,
                "question_number": float(qnum),
                "question_title": qtitle.upper()[:80],
                "error_text_raw": body_clean[:2000],
                "topic": topic,
            })
    return rows


def main():
    parser_rows = []
    for year in [2023, 2024, 2025]:
        start, end = PAGE_RANGES[year]
        rows = parse_year(year, start, end)
        print(f"  {year}: parser produced {len(rows)} rows")
        parser_rows.extend(rows)

    parser_df = pd.DataFrame(parser_rows)

    # Load user's manual file
    manual_df = pd.read_csv(
        ROOT / "data" / "processed" / "diagnostics"
        / "diagnostic_errors_v1_backup_2023_2025.csv"
    )

    print()
    print("=" * 60)
    print("COMPARISON — manual vs parser")
    print("=" * 60)
    print()
    print(f"Manual rows (2023-2025):  {len(manual_df)}")
    print(f"Parser rows (2023-2025):  {len(parser_df)}")
    print()
    print("Manual rows per year:")
    print(manual_df.groupby("year").size().to_string())
    print()
    print("Parser rows per year:")
    print(parser_df.groupby("year").size().to_string())
    print()
    print("Manual avg text length:", int(manual_df["error_text_raw"].str.len().mean()))
    print("Parser avg text length:", int(parser_df["error_text_raw"].str.len().mean()))
    print()
    print("Manual topic distribution:")
    print(manual_df["topic"].value_counts().to_string())
    print()
    print("Parser topic distribution:")
    print(parser_df["topic"].value_counts().to_string())
    print()
    print("=" * 60)
    print("SAMPLE MANUAL ROW:")
    print("=" * 60)
    r = manual_df[manual_df["year"] == 2023].iloc[0]
    print(f"  Q{r['question_number']} [{r['topic']}]")
    print(f"  {str(r['error_text_raw'])[:300]}")
    print()
    print("=" * 60)
    print("SAMPLE PARSER ROW:")
    print("=" * 60)
    if len(parser_df) > 0:
        r = parser_df[parser_df["year"] == 2023].iloc[0]
        print(f"  Q{r['question_number']} [{r['topic']}]")
        print(f"  {str(r['error_text_raw'])[:300]}")
    else:
        print("  No parser rows for 2023")


if __name__ == "__main__":
    main()