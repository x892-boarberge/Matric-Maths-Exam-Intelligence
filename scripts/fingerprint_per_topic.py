"""
Per-topic fingerprint.
Reads mapped question CSVs (2014-2025), extracts numbers per topic,
runs the same tests — concentration, perfect squares, decimals.
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

# Numbers we care about (exclude subquestion refs like 1.1, 6.1)
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
SUBQ_REF_RE = re.compile(r"^\s*\d+(?:\.\d+){1,3}\s*")   # strip leading 1.1.1
SUBQ_INLINE_RE = re.compile(r"\bQ?\d+\.\d+(?:\.\d+)?\b")   # strip inline Q1.1.2

# --- Load all mapped questions ---
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
                "paper": r.get("paper"),
                "topic": topic,
                "text": text,
            })

print(f"Total questions loaded: {len(rows)}")
print()

# --- Per-topic number extraction ---
by_topic = defaultdict(list)

for r in rows:
    text = r["text"]
    # Strip leading subquestion ref
    text = SUBQ_REF_RE.sub("", text)
    # Strip inline subquestion refs (Q1.1.2)
    text = SUBQ_INLINE_RE.sub("", text)
    # Remove (marks) markers like (3)
    text = re.sub(r"\(\d+\)", "", text)
    # Remove numbers in words like "TwO"
    for m in NUMBER_RE.finditer(text):
        num_str = m.group(0)
        # Skip if this number is immediately followed by more digits (part of another num)
        by_topic[r["topic"]].append({
            "num": num_str,
            "year": r["year"],
        })

print(f"Topics found: {sorted(by_topic.keys())}")
print()

# --- Helper functions ---
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

def fraction_like(n):
    """Detect decimals like 0.5, 0.25, 0.125 (nice fractions)."""
    if "." not in n:
        return False
    try:
        v = abs(float(n))
        if v == 0 or v >= 1:
            return False
        # 0.5, 0.25, 0.75, 0.125, 0.333...
        for d in [2, 3, 4, 5, 6, 8, 10, 20, 25, 50, 100]:
            if abs(v * d - round(v * d)) < 0.0001 and round(v * d) != 0:
                return True
        return False
    except ValueError:
        return False

def top_n_concentration(nums_list, n=10):
    """Concentration ratio: share held by top n vs uniform expectation."""
    small_ints = [int(x) for x in nums_list if is_small_int(x)]
    if not small_ints:
        return 0.0, 0.0
    c = Counter(small_ints)
    total = sum(c.values())
    top = c.most_common(n)
    top_share = sum(v for _, v in top) / total
    uniform_share = n / 50  # over 1-50
    ratio = top_share / uniform_share if uniform_share else 0
    return top_share, ratio

# --- Build report ---
lines = []
lines.append("# Per-topic fingerprint")
lines.append("")
lines.append(f"**Questions:** {len(rows)}")
lines.append(f"**Topics:** {len(by_topic)}")
lines.append("")

# Table of topics
lines.append("## Summary table")
lines.append("")
lines.append("| Topic | Numbers | 1-10 % | Perfect squares % | Fractions <1 % | Concentration |")
lines.append("|---|---|---|---|---|---|")
for topic in sorted(by_topic.keys()):
    items = by_topic[topic]
    nums = [i["num"] for i in items]
    n = len(nums) or 1
    small = sum(1 for x in nums if is_small_int(x))
    sq = sum(1 for x in nums if is_perfect_square(x))
    frac = sum(1 for x in nums if fraction_like(x))
    _, ratio = top_n_concentration(nums)
    lines.append(
        f"| {topic} | {len(nums)} | {100*small/n:.1f}% | "
        f"{100*sq/n:.1f}% | {100*frac/n:.1f}% | {ratio:.2f}x |"
    )
lines.append("")

# Per-topic detail
for topic in sorted(by_topic.keys()):
    items = by_topic[topic]
    nums = [i["num"] for i in items]
    c = Counter(nums)
    lines.append(f"## {topic}")
    lines.append("")
    lines.append(f"**Total numbers:** {len(nums)}")
    lines.append("")
    lines.append("**Top 10 most frequent:**")
    lines.append("")
    lines.append("| Rank | Number | Count |")
    lines.append("|---|---|---|")
    for i, (num, count) in enumerate(c.most_common(10), 1):
        lines.append(f"| {i} | {num} | {count} |")
    lines.append("")
    # Sample text
    sample = items[0]["year"] if items else ""
    lines.append(f"_Sample from {sample}_")
    lines.append("")

# Write
(OUT_DIR / "per_topic_report.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[:80]))
print()
print(f"Full report: {OUT_DIR / 'per_topic_report.md'}")