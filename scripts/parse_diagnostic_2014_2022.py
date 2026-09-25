"""
Parse DBE diagnostic reports 2014-2022 (Maths pages only) into
structured error rows matching the existing 2023-2025 schema.
"""
import re
import pandas as pd
import pymupdf
from pathlib import Path

ROOT = Path(".").resolve()
PDF_DIR = ROOT / "data" / "raw" / "diagnostic_reports"
OUT = ROOT / "data" / "processed" / "diagnostics" / "diagnostic_errors_2014_2022.csv"

PAGE_RANGES = {
    2014: (117, 139),
    2015: (150, 174),
    2016: (155, 181),
    2017: (161, 184),
    2018: (132, 150),
    2019: (177, 201),
    2020: (184, 207),
    2021: (186, 211),
    2022: (198, 220),
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

OCR_FIXES = [
    (r"\b\u00bfrst\b", "first"),
    (r"\u00bfrst", "first"),
    (r"re\u00c0ect", "reflect"),
    (r"\u00c0", "fl"),
    (r"\u00bf", "fi"),
    (r"Re\u00c0", "Refl"),
]


def clean_text(s):
    for pat, rep in OCR_FIXES:
        s = re.sub(pat, rep, s)
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


def severity_from_text(s):
    low = s.lower()
    if any(w in low for w in ["very disappointing", "severe", "shortcoming", "extremely poor"]):
        return "severe_language"
    return "moderate_language"


def parse_year(year, start, end):
    pdf = PDF_DIR / f"{year}_maths_diagnostic_part1.pdf"
    if not pdf.exists():
        print(f"  MISSING {pdf.name}")
        return []
    doc = pymupdf.open(pdf)
    n = len(doc)
    if end > n:
        print(f"  WARNING: {year} range {start}-{end} exceeds {n} pages, clipping")
        end = n

    pages = []
    for p in range(start - 1, end):
        pages.append(doc[p].get_text("text"))
    text = "\n".join(pages)

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
                "error_text_summary": None,
                "source": "DBE diagnostic",
                "qualitative_severity": severity_from_text(body_clean),
                "topic": topic,
            })
    return rows


def main():
    all_rows = []
    for year in sorted(PAGE_RANGES.keys()):
        start, end = PAGE_RANGES[year]
        rows = parse_year(year, start, end)
        print(f"  {year}: {len(rows)} error rows")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8")
    print()
    print(f"Wrote {len(df)} rows to {OUT}")
    print()
    print("Topic distribution:")
    print(df["topic"].value_counts().to_string())
    print()
    print("Sample rows:")
    for _, r in df.head(3).iterrows():
        print(f"  {r['year']} Q{r['question_number']} [{r['topic']}]: {str(r['error_text_raw'])[:140]}...")


if __name__ == "__main__":
    main()