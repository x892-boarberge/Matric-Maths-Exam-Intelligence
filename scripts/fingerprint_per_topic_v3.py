"""
Per-topic fingerprint v3 — OCR source, fraction-aware.
"""
import re
import json
from pathlib import Path
from collections import Counter, defaultdict
from math import sqrt

import pandas as pd

PAGES_DIR = Path("data/processed/diagrams/pages")
MAP_DIR = Path("data/processed/mapped")
OUT_DIR = Path("data/processed/fingerprint")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FRACTION_RE = r"(-?\d+\s*/\s*-?\d+)"
NUMBER_RE = r"(-?\d+(?:\.\d+)?)"
TOKEN_RE = re.compile(f"{FRACTION_RE}|{NUMBER_RE}")
Q_HEAD_RE = re.compile(r"QUESTION\s+(\d+)\b", re.IGNORECASE)
MARKS_RE = re.compile(r"\(\d+\)")
# Subquestion references: 1.1, 6.3, 11.2, 11.12, Q1.1, Q11.3 — filter these
SUBQ_LINE_START_RE = re.compile(r"^\s*\d+(\.\d+){1,3}\s", re.MULTILINE)
SUBQ_INLINE_RE = re.compile(r"\bQ\s?\d+(\.\d+){1,3}\b")
# Subquestion ranges like "1.1 to 1.3" or "Q1.1.1-1.1.4"
SUBQ_RANGE_RE = re.compile(r"\b\d+(\.\d+){1,3}\s*[-–]\s*\d+(\.\d+){1,3}\b")

# Build topic lookup: (year, paper, qnum) -> topic
topic_lookup = {}
for year_dir in sorted(MAP_DIR.glob("20*")):
    if not year_dir.is_dir():
        continue
    for f in year_dir.glob("question_topic_map_*_v2.csv"):
        try:
            df = pd.read_csv(f)
        except Exception:
            continue
        if "topic_v2" not in df.columns or "question_number" not in df.columns:
            continue
        for _, r in df.iterrows():
            year = str(int(r["year"])) if not pd.isna(r.get("year")) else ""
            paper = str(r.get("paper", "") or "").strip()
            qnum = str(r.get("question_number", "")).split(".")[0].strip()
            topic = str(r.get("topic_v2", "") or "").strip()
            if not topic or topic.lower() in ("nan", "none", ""):
                continue
            topic_lookup[(year, paper, qnum)] = topic

print(f"Topic lookup: {len(topic_lookup)} entries")

# Load OCR pages grouped by paper
paper_pages = defaultdict(list)
for txt in sorted(PAGES_DIR.glob("*_exam_maths_p*.txt")):
    stem = txt.stem
    paper = stem.rsplit("_p", 1)[0]
    try:
        page_num = int(stem.rsplit("_p", 1)[1])
    except ValueError:
        continue
    content = txt.read_text(encoding="utf-8", errors="ignore")
    paper_pages[paper].append((page_num, content))

for paper in paper_pages:
    paper_pages[paper].sort()

print(f"Papers: {len(paper_pages)}")

def parse_fraction(tok):
    parts = re.sub(r"\s+", "", tok).split("/")
    if len(parts) != 2:
        return None
    try:
        n, d = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    if d == 0:
        return None
    if 1900 <= abs(d) <= 2100:
        return None
    if 1900 <= abs(n) <= 2100 and abs(d) <= 12:
        return None
    return f"{n}/{d}"

by_topic = defaultdict(lambda: {"ints": [], "decimals": [], "fractions": []})

for paper, pages in paper_pages.items():
    full_text = "\n".join(t for _, t in pages)
    parts = paper.split("_")
    if len(parts) < 3:
        continue
    year = parts[0]
    paper_code = parts[2].upper()

    q_matches = list(Q_HEAD_RE.finditer(full_text))
    if not q_matches:
        continue

    for i, m in enumerate(q_matches):
        qnum = m.group(1)
        start = m.end()
        end = q_matches[i + 1].start() if i + 1 < len(q_matches) else len(full_text)
        block = full_text[start:end]
        # Convert SA comma-decimals to point-decimals
        # R58 230,94 → 58230.94 ; 0,26 → 0.26
        # Pattern: digits + comma + digits (where comma is between digits)
        block = re.sub(r"(?<=\d),(?=\d)", ".", block)
        # Remove space thousands separators inside money: 58 230 → 58230
        block = re.sub(r"(?<=\d)\s(?=\d{3}\b)", "", block)

        block = MARKS_RE.sub(" ", block)
        block = SUBQ_LINE_START_RE.sub(" ", block)
        block = SUBQ_INLINE_RE.sub(" ", block)
        block = SUBQ_RANGE_RE.sub(" ", block)
        block = re.sub(r"Copyright reserved.*", " ", block)
        block = re.sub(r"Please turn over.*", " ", block)
        block = re.sub(r"DBE/November\s+\d+", " ", block, flags=re.IGNORECASE)

        topic = topic_lookup.get((year, paper_code, qnum))
        if not topic:
            continue

        for tm in TOKEN_RE.finditer(block):
            frac = tm.group(1)
            num = tm.group(2)
            if frac:
                tok = parse_fraction(frac)
                if tok:
                    by_topic[topic]["fractions"].append(tok)
            elif num:
                if "." in num:
                    by_topic[topic]["decimals"].append(num)
                else:
                    by_topic[topic]["ints"].append(num)

print(f"Topics: {sorted(by_topic.keys())}")
print()

def is_small_int(n):
    if "." in n:
        return False
    try:
        v = abs(int(n))
        return 1 <= v <= 10
    except ValueError:
        return False

def is_perfect_square(n):
    if "." in n:
        return False
    try:
        v = abs(int(n))
        if v <= 0:
            return False
        return int(sqrt(v)) ** 2 == v
    except ValueError:
        return False

def concentration(nums, n=10):
    small = [int(x) for x in nums if is_small_int(x)]
    if not small:
        return 0.0, 0.0
    c = Counter(small)
    total = sum(c.values())
    top = c.most_common(n)
    top_share = sum(v for _, v in top) / total
    ratio = top_share / (n / 50)
    return top_share, ratio

lines = []
lines.append("# Per-topic fingerprint v3")
lines.append("")
lines.append("## Summary table")
lines.append("")
lines.append("| Topic | Ints | Decimals | Fractions | 1-10 % | Sq % | Fraction % | Concentr. |")
lines.append("|---|---|---|---|---|---|---|---|")
for topic in sorted(by_topic.keys()):
    t = by_topic[topic]
    ints, decs, frs = t["ints"], t["decimals"], t["fractions"]
    total = len(ints) + len(decs) + len(frs) or 1
    small = sum(1 for x in ints if is_small_int(x))
    sq = sum(1 for x in ints if is_perfect_square(x))
    _, ratio = concentration(ints)
    lines.append(
        f"| {topic} | {len(ints)} | {len(decs)} | {len(frs)} | "
        f"{100*small/len(ints) if ints else 0:.1f}% | "
        f"{100*sq/len(ints) if ints else 0:.1f}% | "
        f"{100*len(frs)/total:.1f}% | {ratio:.2f}x |"
    )
lines.append("")

for topic in sorted(by_topic.keys()):
    t = by_topic[topic]
    lines.append(f"## {topic}")
    lines.append(f"- Ints: {len(t['ints'])} | Decimals: {len(t['decimals'])} | Fractions: {len(t['fractions'])}")
    lines.append("")
    if t["fractions"]:
        fc = Counter(t["fractions"])
        lines.append("**Top fractions:**")
        for fr, c in fc.most_common(8):
            lines.append(f"- {fr} ({c})")
        lines.append("")
    if t["decimals"]:
        dc = Counter(t["decimals"])
        lines.append("**Top decimals:**")
        for d, c in dc.most_common(8):
            lines.append(f"- {d} ({c})")
        lines.append("")
    ic = Counter(t["ints"])
    lines.append("**Top ints:**")
    for v, c in ic.most_common(5):
        lines.append(f"- {v} ({c})")
    lines.append("")

report_path = OUT_DIR / "per_topic_report_v3.md"
report_path.write_text("\n".join(lines), encoding="utf-8")

# Print summary
for l in lines:
    print(l)
print()
print(f"Wrote {report_path}")