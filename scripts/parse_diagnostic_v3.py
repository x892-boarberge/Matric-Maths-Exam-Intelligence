"""
DBE diagnostic parser v3.

Additions from peer review:
  Layer 1: page_num, is_suggestion flag, quality flags
  Layer 2: "reading" class, cross_topic, notation_subtype
  Layer 5 prep: diagram_assumption flag (derived here, not in analysis)
"""
import re
import pandas as pd
import pymupdf
from pathlib import Path

ROOT = Path(".").resolve()
PDF_DIR = ROOT / "data" / "raw" / "diagnostic_reports"
OUT = ROOT / "data" / "processed" / "diagnostics" / "diagnostic_errors_v3.csv"

PAGE_RANGES = {
    2014: (117, 139), 2015: (150, 174), 2016: (155, 181),
    2017: (161, 184), 2018: (132, 150), 2019: (177, 201),
    2020: (184, 207), 2021: (186, 211), 2022: (198, 220),
    2023: (213, 273), 2024: (219, 287), 2025: (230, 283),
}

TOPIC_MAP = {
    "ALGEBRA": "ALG", "EQUATIONS AND INEQUALITIES": "ALG",
    "SEQUENCES AND SERIES": "SEQ", "PATTERNS": "SEQ", "NUMBER PATTERNS": "SEQ",
    "FUNCTIONS": "FUNC", "EXPONENTIAL": "FUNC", "LOGARITHMIC": "FUNC",
    "HYPERBOLA": "FUNC", "PARABOLA": "FUNC",
    "FINANCE": "FIN", "FINANCIAL MATHEMATICS": "FIN",
    "CALCULUS": "CALC", "DIFFERENTIAL CALCULUS": "CALC",
    "PROBABILITY": "PROB", "TRIGONOMETRY": "TRIG",
    "ANALYTICAL GEOMETRY": "AGEO", "EUCLIDEAN GEOMETRY": "EUCL",
    "DATA HANDLING": "STAT", "STATISTICS": "STAT",
}

MOJIBAKE = [
    ("\u201a\u00c4\u00f2", "'"), ("\u201a\u00c4\u00f4", "'"),
    ("\u201a\u00c4\u00fa", '"'), ("\u201a\u00c4\u00f9", '"'),
    ("\u201a\u00c4\u00ec", "–"), ("\u201a\u00c4\u00ee", "—"),
    ("\u201a\u00c3\u00a0", "à"), ("\u201a\u00c3\u00ad", "-"),
    ("\u00d4\u00c4\u00e6", ">"), ("\u00d4\u00c4\u00ba", "<"),
    ("\u00d4\u00c4\u00a5", "≥"), ("\u00d4\u00c4\u00a4", "≤"),
    ("\u00d4\u00c4\u00b2", "∈"),
    ("\u00e2\u0080\u0098", "'"), ("\u00e2\u0080\u0099", "'"),
    ("\u00e2\u0080\u009c", '"'), ("\u00e2\u0080\u009d", '"'),
    ("\u00e2\u0080\u0093", "–"), ("\u00e2\u0080\u0094", "—"),
    ("\u00e2\u0088\u0092", "-"), ("\u00e2\u0089\u00a0", "≠"),
    ("\u00e2\u0089\u00a4", "≤"), ("\u00e2\u0089\u00a5", "≥"),
    ("\u00e2\u0088\u0088", "∈"),
]

CLASS_PATTERNS = [
    ("reading",      re.compile(r"\bmisread|\bdid\s+not\s+(?:read|notice|understand\s+the\s+question)|\boverlook|\bignored\s+the|\breading\s+for", re.I)),
    ("notation",     re.compile(r"\bnotation|\bsymbol|\bwrote\s+.{0,30}instead\b", re.I)),
    ("presentation", re.compile(r"\bpresentation|\blayout|\bno\s+reason|\bdid\s+not\s+show\s+work|\banswer\s+only\b", re.I)),
    ("conceptual",   re.compile(r"\bno\s+understanding|\bdid\s+not\s+know|\bconcept|\bmisconception|\bunable\s+to\s+understand", re.I)),
    ("arithmetic",   re.compile(r"\barithmetic|\bcalculation\s+error|\bsign\s+error|\bcomput", re.I)),
    ("procedural",   re.compile(r"\bincorrect|\bfailed\s+to|\bsubstitut|\bsimplif|\bfactor|\bexpand|\bforgot", re.I)),
]

DIAGRAM_ASSUME_RE = re.compile(
    r"assum(?:ed|ing|ption)|without\s+(?:first\s+)?prov(?:ing|ed)|"
    r"look(?:ed|ing)\s+(?:at|like)|\bdiagram\b",
    re.I,
)
CROSS_TOPIC_RE = re.compile(
    r"paper\s+2.{0,40}paper\s+1|paper\s+1.{0,40}paper\s+2|"
    r"integration\s+of|integrat(?:e|ing|ed)\s+with",
    re.I,
)
NOTATION_SUBTYPE_PATTERNS = [
    ("inequality", re.compile(r"\binequalit|\band\b.{0,10}\bor\b|\breversed\s+inequalit", re.I)),
    ("function",   re.compile(r"\bdomain|\brange|f\s*'\s*\(|f\(x\)|asymptote", re.I)),
    ("geometry",   re.compile(r"\bangle|\breason|\bstatement|\bhat\b|∠", re.I)),
    ("interval",   re.compile(r"\binterval|\bset\s+notation|\bopen\s+interval", re.I)),
]

SUBQ_REF_RE = re.compile(r"\bQ(\d+(?:\.\d+){1,3})\b")
ERRORS_HEAD_RE = re.compile(r"common\s+errors?\s+and\s+misconceptions?", re.I)
SUGG_HEAD_RE = re.compile(r"suggestions?\s+for\s+improvement", re.I)
Q_HEAD_RE = re.compile(r"QUESTION\s+(\d+)\s*:\s*([A-Z][A-Za-z \-,/()]+?)(?=\n|[A-Z]{2,})")


def fix_mojibake(s):
    for bad, good in MOJIBAKE:
        s = s.replace(bad, good)
    s = re.sub(r"[\u00c0-\u00c5][\u00a0-\u00bf]+", " ", s)
    return s


def clean(s):
    raw_len = len(s)
    s = fix_mojibake(s)
    s = re.sub(r"(?:\d+%\s*){3,}", " ", s)
    s = re.sub(r"[\r\n\t]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = s.strip()
    return s, raw_len, len(s)


def classify(text):
    for name, pat in CLASS_PATTERNS:
        if pat.search(text):
            return name
    return "general"


def notation_subtype(text):
    for name, pat in NOTATION_SUBTYPE_PATTERNS:
        if pat.search(text):
            return name
    return None


def map_topic(title):
    t = title.upper()
    for key, val in TOPIC_MAP.items():
        if key in t:
            return val
    return "UNMAPPED"


def split_paras(block):
    pat = re.compile(r"\(([a-z])\)\s+(.+?)(?=\([a-z]\)\s+|\Z)", re.DOTALL)
    out = []
    for letter, raw in pat.findall(block):
        cleaned, raw_len, clean_len = clean(raw)
        out.append((letter, cleaned, raw_len, clean_len))
    return out


def parse_year(year, start, end):
    pdf = PDF_DIR / f"{year}_maths_diagnostic_part1.pdf"
    if not pdf.exists():
        return []

    doc = pymupdf.open(pdf)
    end = min(end, len(doc))

    # Build text with page markers so we can track provenance
    chunks = []
    for p in range(start - 1, end):
        chunks.append((p + 1, doc[p].get_text("text")))
    text = "\n".join(t for _, t in chunks)

    offsets = []
    cursor = 0
    for pnum, t in chunks:
        offsets.append((cursor, cursor + len(t) + 1, pnum))
        cursor += len(t) + 1

    def page_of(pos):
        for a, b, p in offsets:
            if a <= pos < b:
                return p
        return None

    q_matches = list(Q_HEAD_RE.finditer(text))
    rows = []
    for i, m in enumerate(q_matches):
        qnum = int(m.group(1))
        qtitle = m.group(2).strip()
        for stop in ["PERFORMANCE", "COMMON", "GRAPH", "DIAGNOSTIC", "SUGGESTIONS", "PAPER"]:
            idx = qtitle.upper().find(stop)
            if idx > 0:
                qtitle = qtitle[:idx].strip()

        block_start = m.end()
        block_end = q_matches[i + 1].start() if i + 1 < len(q_matches) else len(text)
        block = text[block_start:block_end]
        page_num = page_of(m.start())

        err_head = ERRORS_HEAD_RE.search(block)
        if not err_head:
            continue
        sugg_head = SUGG_HEAD_RE.search(block, err_head.end())
        err_body = block[err_head.end(): sugg_head.start() if sugg_head else len(block)]
        sugg_body = block[sugg_head.end():] if sugg_head else ""

        topic = map_topic(qtitle)

        # Errors
        for letter, body, raw_len, clean_len in split_paras(err_body):
            if len(body) < 50:
                continue
            sub_refs = sorted(set(SUBQ_REF_RE.findall(body)))
            err_cls = classify(body)
            rows.append({
                "year": year,
                "paper": None,
                "question_number": qnum,
                "question_title": qtitle.upper()[:80],
                "topic": topic,
                "subquestion_ref": ";".join(sub_refs) if sub_refs else None,
                "error_text": body[:2000],
                "error_class": err_cls,
                "cross_topic": bool(CROSS_TOPIC_RE.search(body)),
                "diagram_assumption": bool(DIAGRAM_ASSUME_RE.search(body)),
                "notation_subtype": notation_subtype(body) if err_cls == "notation" else None,
                "source_section": "errors",
                "is_suggestion": False,
                "source": "DBE diagnostic",
                "page_num": page_num,
                "raw_char_count": raw_len,
                "cleaned_char_count": clean_len,
                "mojibake_cleaned": raw_len != clean_len,
            })

        # Suggestions (separate, no pairing)
        for letter, body, raw_len, clean_len in split_paras(sugg_body):
            if len(body) < 50:
                continue
            rows.append({
                "year": year,
                "paper": None,
                "question_number": qnum,
                "question_title": qtitle.upper()[:80],
                "topic": topic,
                "subquestion_ref": None,
                "error_text": None,
                "error_class": None,
                "cross_topic": None,
                "diagram_assumption": None,
                "notation_subtype": None,
                "source_section": "suggestions",
                "is_suggestion": True,
                "suggestion_text": body[:1500],
                "source": "DBE diagnostic",
                "page_num": page_num,
                "raw_char_count": raw_len,
                "cleaned_char_count": clean_len,
                "mojibake_cleaned": raw_len != clean_len,
            })
    return rows


def main():
    all_rows = []
    for year in sorted(PAGE_RANGES.keys()):
        start, end = PAGE_RANGES[year]
        rows = parse_year(year, start, end)
        n_err = sum(1 for r in rows if r["source_section"] == "errors")
        n_sug = sum(1 for r in rows if r["source_section"] == "suggestions")
        print(f"  {year}: {n_err} errors, {n_sug} suggestions")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8")

    errs = df[df["source_section"] == "errors"]
    print()
    print("=" * 60)
    print(f"Wrote {len(df)} rows ({len(errs)} errors, {len(df) - len(errs)} suggestions)")
    print()
    print("Errors per year:")
    print(errs.groupby("year").size().to_string())
    print()
    print("Topic distribution (errors):")
    print(errs["topic"].value_counts().to_string())
    print()
    print("Error class distribution:")
    print(errs["error_class"].value_counts().to_string())
    print()
    print(f"Cross-topic errors:       {int(errs['cross_topic'].sum())}")
    print(f"Diagram-assumption errors: {int(errs['diagram_assumption'].sum())}")
    print(f"Mojibake-cleaned rows:     {int(errs['mojibake_cleaned'].sum())}")
    print()
    print("=" * 60)
    print("SAMPLE ERROR (2023, cleaned):")
    print("=" * 60)
    s = errs[errs["year"] == 2023].iloc[0]
    print(f"Q{s['question_number']} [{s['topic']}] ref={s['subquestion_ref']} page={s['page_num']}")
    print(f"CLASS: {s['error_class']}  CROSS_TOPIC: {s['cross_topic']}  DIAGRAM_ASSUME: {s['diagram_assumption']}")
    print(f"TEXT: {str(s['error_text'])[:400]}")


if __name__ == "__main__":
    main()