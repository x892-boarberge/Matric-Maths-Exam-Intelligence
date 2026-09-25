"""DBE diagnostic parser v7. Fixes 2015 tab-headings, 2018 short range, 2019 over-split."""
import re
import pandas as pd
import pymupdf
from pathlib import Path

ROOT = Path(".").resolve()
PDF_DIR = ROOT / "data" / "raw" / "diagnostic_reports"
OUT = ROOT / "data" / "processed" / "diagnostics" / "diagnostic_errors_v7.csv"

# 2018 range widened; 2015 kept; 2019 kept
PAGE_RANGES = {
    2014: (117, 139), 2015: (155, 176), 2016: (155, 181),
    2017: (161, 184), 2018: (139, 170), 2019: (177, 210),
    2020: (184, 207), 2021: (186, 211), 2022: (198, 220),
    2023: (213, 273), 2024: (219, 287), 2025: (230, 283),
}

TOPIC_MAP = {
    "ALGEBRA": "ALG", "EQUATIONS AND INEQUALITIES": "ALG",
    "SEQUENCES": "SEQ", "SEQUENCES AND SERIES": "SEQ",
    "PATTERNS": "SEQ", "NUMBER PATTERNS": "SEQ",
    "FUNCTIONS": "FUNC", "EXPONENTIAL": "FUNC", "LOGARITHMIC": "FUNC",
    "HYPERBOLA": "FUNC", "PARABOLA": "FUNC",
    "FINANCE": "FIN", "FINANCIAL MATHEMATICS": "FIN",
    "CALCULUS": "CALC", "DIFFERENTIAL CALCULUS": "CALC",
    "PROBABILITY": "PROB", "TRIGONOMETRY": "TRIG",
    "ANALYTICAL GEOMETRY": "AGEO", "EUCLIDEAN GEOMETRY": "EUCL",
    "DATA HANDLING": "STAT", "STATISTICS": "STAT",
    "MEASUREMENT": "MEAS", "COUNTING PRINCIPLE": "PROB",
    "COUNTING PRINCIPLES": "PROB",
}

MOJIBAKE = [
    ("\u201a\u00c4\u00f2", "'"), ("\u201a\u00c4\u00f4", "'"),
    ("\u201a\u00c4\u00fa", '"'), ("\u201a\u00c4\u00f9", '"'),
    ("\u201a\u00c4\u00ec", "\u2013"), ("\u201a\u00c4\u00ee", "\u2014"),
    ("\u201a\u00c3\u00a0", "\u00e0"), ("\u201a\u00c3\u00ad", "-"),
    ("\u00d4\u00c4\u00e6", ">"), ("\u00d4\u00c4\u00ba", "<"),
    ("\u00d4\u00c4\u00a5", "\u2265"), ("\u00d4\u00c4\u00a4", "\u2264"),
    ("\u00d4\u00c4\u00b2", "\u2208"),
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
    r"look(?:ed|ing)\s+(?:at|like)|\bdiagram\b", re.I,
)
CROSS_TOPIC_RE = re.compile(
    r"paper\s+2.{0,40}paper\s+1|paper\s+1.{0,40}paper\s+2|"
    r"integration\s+of|integrat(?:e|ing|ed)\s+with", re.I,
)
NOTATION_SUBTYPE_PATTERNS = [
    ("inequality", re.compile(r"\binequalit|\band\b.{0,10}\bor\b|\breversed\s+inequalit", re.I)),
    ("function",   re.compile(r"\bdomain|\brange|f\s*'\s*\(|f\(x\)|asymptote", re.I)),
    ("geometry",   re.compile(r"\bangle|\breason|\bstatement|\bhat\b|\u2220", re.I)),
    ("interval",   re.compile(r"\binterval|\bset\s+notation|\bopen\s+interval", re.I)),
]

SUBQ_REF_RE = re.compile(r"\bQ(\d+(?:\.\d+){1,3})\b")
ERRORS_HEAD_RE = re.compile(r"common\s+errors?\s+and\s+misconceptions?", re.I)
SUGG_HEAD_RE = re.compile(r"suggestions?\s+for\s+improvement", re.I)

# Heading regexes — added tab-tolerant option
Q_HEAD_REGEXES = [
    re.compile(r"QUESTION\s+(\d+)\s*:\s*([^\n]+)"),                 # colon
    re.compile(r"QUESTION\s+(\d+)[\s\t]+([A-Z][A-Z\s\-()]+)(?=\n)"), # tab or space, uppercase topic
    re.compile(r"QUESTION\s+(\d+)\s{2,}([A-Z][^\n]+)"),             # two+ spaces
]

PAPER_HEAD_RE = re.compile(r"PERFORMANCE\s+IN\s+EACH\s+QUESTION\s+IN\s+PAPER\s+([12])", re.I)
NEXT_CHAPTER_RE = re.compile(r"CHAPTER\s+1[1-9]|PHYSICAL\s+SCIENCES|ACCOUNTING|LIFE\s+SCIENCES|ECONOMICS", re.I)


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
    return s.strip(), raw_len, len(s.strip())


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


def find_question_headings(text):
    for rx in Q_HEAD_REGEXES:
        matches = list(rx.finditer(text))
        if len(matches) >= 3:
            return matches
    return []


# 2019 paragraph splitter — tightened: requires sentence-end + longer min
PARA_START_RE = re.compile(
    r"(?<=\.\s)(?=(?:In\s+Q\d|In\s+answering|Many\s+candidates|Some\s+candidates|"
    r"Most\s+candidates|A\s+few\s+candidates|Writing\s+down|The\s+majority|"
    r"Very\s+few|Others\s+|\bOthers\b|Candidates\s+))",
    re.I,
)

def split_paras_2019(block):
    block = re.sub(r"\([a-z]\)\s*\n?", " ", block)
    block = re.sub(r"[ \t]+", " ", block)
    parts = PARA_START_RE.split(block)
    out = []
    for raw in parts:
        cleaned, raw_len, clean_len = clean(raw)
        if len(cleaned) < 100:  # raised from 50 to prevent fragment splitting
            continue
        out.append(("?", cleaned, raw_len, clean_len))
    return out


def split_paras(block, year):
    if year == 2015:
        pat = re.compile(r"(?:^|\n)\s*(\d+)\.\s*\n(.+?)(?=\n\s*\d+\.\s*\n|\Z)", re.DOTALL)
        return [(n, *clean(r)) for n, r in pat.findall(block)]
    if year == 2018:
        pat = re.compile(r"(?:^|\n)\s*([a-z])\.\s+(.+?)(?=\n\s*[a-z]\.\s+|\Z)", re.DOTALL)
        return [(l, *clean(r)) for l, r in pat.findall(block)]
    if year == 2019:
        return split_paras_2019(block)
    pat = re.compile(r"\(([a-z])\)\s+(.+?)(?=\([a-z]\)\s+|\Z)", re.DOTALL)
    return [(l, *clean(r)) for l, r in pat.findall(block)]


def extract_maths_window(text):
    paper_heads = list(PAPER_HEAD_RE.finditer(text))
    if len(paper_heads) < 2:
        return [(1, text)]
    p1_start = paper_heads[0].end()
    p2_marker = paper_heads[1]
    p2_start = p2_marker.end()
    next_chapter = NEXT_CHAPTER_RE.search(text, p2_start)
    p2_end = next_chapter.start() if next_chapter else len(text)
    return [(1, text[p1_start:p2_marker.start()]), (2, text[p2_start:p2_end])]


def parse_section(year, paper_num, section_text):
    q_matches = find_question_headings(section_text)
    rows = []
    for i, m in enumerate(q_matches):
        qnum = int(m.group(1))
        qtitle = m.group(2).strip()
        for stop in ["PERFORMANCE", "COMMON", "GRAPH", "DIAGNOSTIC", "SUGGESTIONS"]:
            idx = qtitle.upper().find(stop)
            if idx > 0:
                qtitle = qtitle[:idx].strip()
        qtitle = qtitle.rstrip(" .:-")

        block_start = m.end()
        block_end = q_matches[i + 1].start() if i + 1 < len(q_matches) else len(section_text)
        block = section_text[block_start:block_end]

        err_head = ERRORS_HEAD_RE.search(block)
        if not err_head:
            continue
        sugg_head = SUGG_HEAD_RE.search(block, err_head.end())
        err_body = block[err_head.end(): sugg_head.start() if sugg_head else len(block)]
        sugg_body = block[sugg_head.end():] if sugg_head else ""

        topic = map_topic(qtitle)

        for letter, body, raw_len, clean_len in split_paras(err_body, year):
            if len(body) < 50:
                continue
            sub_refs = sorted(set(SUBQ_REF_RE.findall(body)))
            err_cls = classify(body)
            rows.append({
                "year": year, "paper": f"P{paper_num}",
                "question_number": qnum, "question_title": qtitle.upper()[:80],
                "topic": topic,
                "subquestion_ref": ";".join(sub_refs) if sub_refs else None,
                "error_text": body[:2000], "error_class": err_cls,
                "cross_topic": bool(CROSS_TOPIC_RE.search(body)),
                "diagram_assumption": bool(DIAGRAM_ASSUME_RE.search(body)),
                "notation_subtype": notation_subtype(body) if err_cls == "notation" else None,
                "source_section": "errors", "source": "DBE diagnostic",
                "raw_char_count": raw_len, "cleaned_char_count": clean_len,
                "mojibake_cleaned": raw_len != clean_len,
            })
        for letter, body, raw_len, clean_len in split_paras(sugg_body, year):
            if len(body) < 50:
                continue
            rows.append({
                "year": year, "paper": f"P{paper_num}",
                "question_number": qnum, "question_title": qtitle.upper()[:80],
                "topic": topic, "subquestion_ref": None,
                "error_text": None, "error_class": None,
                "cross_topic": None, "diagram_assumption": None, "notation_subtype": None,
                "source_section": "suggestions", "suggestion_text": body[:1500],
                "source": "DBE diagnostic",
                "raw_char_count": raw_len, "cleaned_char_count": clean_len,
                "mojibake_cleaned": raw_len != clean_len,
            })
    return rows


def parse_year(year, start, end):
    pdf = PDF_DIR / f"{year}_maths_diagnostic_part1.pdf"
    if not pdf.exists():
        return []
    doc = pymupdf.open(pdf)
    end = min(end, len(doc))
    text = "\n".join(doc[p].get_text("text") for p in range(start - 1, end))
    rows = []
    for paper_num, section in extract_maths_window(text):
        rows.extend(parse_section(year, paper_num, section))
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
    print("Topic distribution:")
    print(errs["topic"].value_counts().to_string())
    print()
    print("Topic × year matrix (spot check 2015/2018/2019):")
    pivot = errs[errs["year"].isin([2015, 2018, 2019])].groupby(["year", "topic"]).size().unstack(fill_value=0)
    print(pivot.to_string())


if __name__ == "__main__":
    main()