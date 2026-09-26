"""
Per-topic fingerprint v2 — fraction-aware.

Detects:
  - a/b as a single fraction token (not two ints)
  - -a/b, a/-b
  - rejects subquestion refs (1.1, Q1.1.2)
  - rejects date-like patterns (11/2025)
  - classifies each token: int / decimal / fraction
"""
import re
import json
from pathlib import Path
from collections import Counter, defaultdict
from math import sqrt

import pandas as pd

MAP_DIR = Path("data/processed/mapped")
OUT_DIR = Path("data/processed/fingerprint")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Combined token regex: fraction FIRST, then number ---
# Fraction: optional sign + digits + '/' + optional sign + digits
FRACTION_RE = r"(-?\d+\s*/\s*-?\d+)"
# Number: optional sign + digits + optional decimal
NUMBER_RE = r"(-?\d+(?:\.\d+)?)"
TOKEN_RE = re.compile(f"{FRACTION_RE}|{NUMBER_RE}")

SUBQ_REF_RE = re.compile(r"^\s*\d+(?:\.\d+){1,3}\s*")
SUBQ_INLINE_RE = re.compile(r"\bQ?\d+\.\d+(?:\.\d+)?\b")
MARKS_RE = re.compile(r"\(\d+\)")
# Date-like: 11/2025, 2025/11
DATE_LIKE_RE = re.compile(r"\b(?:0?[1-9]|1[0-2])\s*/\s*20\d{2}\b|\b20\d{2}\s*/\s*(?:0?[1-9]|1[0-2])\b")

def classify_fraction(s):
    """Return (num_str, is_fraction) for a matched fraction token."""
    s = s.replace(" ", "")
    # Reject date-like
    if DATE_LIKE_RE.match(s):
        return None, False
    parts = s.split("/")
    if len(parts) != 2:
        return None, False
    try:
        num = int(parts[0])
        den = int(parts[1])
    except ValueError:
        return None, False
    if den == 0:
        return None, False
    # Skip obvious dates
    if den >= 1900 and den <= 2100:
        return None, False
    if num >= 1900 and num <= 2100 and abs(den) <= 12:
        return None, False
    return f"{num}/{den}", True


def is_nice_fraction(n, d):
    """Fraction where d is 2,3,4,5,6,8,10,12,15,20,25,50,100."""
    for nice in [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 50, 100]:
        if d == nice:
            return True
    return False


def parse_fraction_token(tok):
    """Split a/b into (num, den)."""
    parts = tok.split("/")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


# --- Load mapped questions ---
rows = []
for year_dir in sorted(MAP_DIR.glob("20*")):
    if not year_dir.is_dir():
        continue
    for f in year_dir.glob("question_topic_map_*_v2.csv"):
        try:
            df = pd.read_csv(f)
        except Exception:
            continue
        if "topic_v2" not in df.columns or "question_text" not in df.columns:
            continue
        for _, r in df.iterrows():
            text = str(r.get("question_text", "") or "")
            topic = str(r.get("topic_v2", "") or "").strip()
            if not topic or topic.lower() in ("nan", "none", ""):
                continue
            rows.append({
                "year": r.get("year"),
                "topic": topic,
                "text": text,
            })

print(f"Total questions loaded: {len(rows)}")
print()

# --- Per-topic token extraction ---
by_topic = defaultdict(lambda: {"ints": [], "decimals": [], "fractions": []})

for r in rows:
    text = r["text"]
    # Clean noise
    text = SUBQ_REF_RE.sub("", text)
    text = SUBQ_INLINE_RE.sub("", text)
    text = MARKS_RE.sub("", text)

    for m in TOKEN_RE.finditer(text):
        frac = m.group(1)
        num = m.group(2)
        if frac:
            tok, is_f = classify_fraction(frac)
            if is_f and tok:
                by_topic[r["topic"]]["fractions"].append(tok)
        elif num:
            if "." in num:
                by_topic[r["topic"]]["decimals"].append(num)
            else:
                by_topic[r["topic"]]["ints"].append(num)

print(f"Topics found: {sorted(by_topic.keys())}")
print()

# --- Tests ---
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

# --- Report ---
lines = []
lines.append("# Per-topic fingerprint v2 — fraction-aware")
lines.append("")
lines.append(f"**Questions:** {len(rows)}")
lines.append("")

# Summary
lines.append("## Summary table")
lines.append("")
lines.append("| Topic | Ints | Decimals | Fractions | 1-10 % | Sq % | Fraction % | Concentr. |")
lines.append("|---|---|---|---|---|---|---|---|")
for topic in sorted(by_topic.keys()):
    t = by_topic[topic]
    ints = t["ints"]
    decs = t["decimals"]
    frs = t["fractions"]
    total = len(ints) + len(decs) + len(frs) or 1
    small = sum(1 for x in ints if is_small_int(x))
    sq = sum(1 for x in ints if is_perfect_square(x))
    # Concentration based on all integer tokens
    _, ratio = concentration(ints)
    lines.append(
        f"| {topic} | {len(ints)} | {len(decs)} | {len(frs)} | "
        f"{100*small/len(ints) if ints else 0:.1f}% | "
        f"{100*sq/len(ints) if ints else 0:.1f}% | "
        f"{100*len(frs)/total:.1f}% | {ratio:.2f}x |"
    )
lines.append("")

# Per-topic detail
for topic in sorted(by_topic.keys()):
    t = by_topic[topic]
    lines.append(f"## {topic}")
    lines.append("")
    lines.append(f"- Integers: {len(t['ints'])}")
    lines.append(f"- Decimals: {len(t['decimals'])}")
    lines.append(f"- Fractions (a/b form): {len(t['fractions'])}")
    lines.append("")
    if t["fractions"]:
        fc = Counter(t["fractions"])
        lines.append("**Top fractions:**")
        lines.append("")
        lines.append("| Rank | Fraction | Count |")
        lines.append("|---|---|---|")
        for i, (fr, cnt) in enumerate(fc.most_common(10), 1):
            lines.append(f"| {i} | {fr} | {cnt} |")
        lines.append("")
    ic = Counter(t["ints"])
    lines.append("**Top 5 integers:**")
    lines.append("")
    lines.append("| Rank | Int | Count |")
    lines.append("|---|---|---|")
    for i, (v, cnt) in enumerate(ic.most_common(5), 1):
        lines.append(f"| {i} | {v} | {cnt} |")
    lines.append("")

(OUT_DIR / "per_topic_report_v2.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[:70]))
print()
print(f"Full report: {OUT_DIR / 'per_topic_report_v2.md'}")