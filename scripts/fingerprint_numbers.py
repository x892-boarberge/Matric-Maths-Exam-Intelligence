"""
Examiner fingerprint — number frequency, distribution, randomness,
optimisation, and decimal conventions.

Scans every OCR'd exam page across all 12 years.
"""
import re
import json
from pathlib import Path
from collections import Counter, defaultdict
from math import sqrt

PAGES_DIR = Path("data/processed/diagrams/pages")
OUT_DIR = Path("data/processed/fingerprint")
OUT_DIR.mkdir(parents=True, exist_ok=True)

NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
DECIMAL_ASK_RE = re.compile(
    r"(TWO decimal places|correct to TWO|correct to \d+ decimal|"
    r"TWO decimals|two decimal places|exact form|leave.*surd|"
    r"leave.*simplified surd|round.*TWO)",
    re.IGNORECASE,
)

# --- Load papers ---
by_paper = defaultdict(list)   # paper_stem -> list of numbers
by_paper_raw = defaultdict(list)  # paper_stem -> raw text
paper_years = {}

for txt in sorted(PAGES_DIR.glob("*_exam_maths_*.txt")):
    stem = txt.stem
    # 2023_nov_p1_exam_maths_p5 -> 2023_nov_p1_exam_maths
    paper = stem.rsplit("_p", 1)[0]
    year = paper.split("_")[0]
    paper_years[paper] = year

    text = txt.read_text(encoding="utf-8", errors="ignore")
    by_paper_raw[paper].append(text)

    # Extract numbers from lines that contain words (question-like lines)
    for line in text.splitlines():
        line = line.strip()
        # Skip header/footer/page numbers
        alpha_count = sum(1 for c in line if c.isalpha())
        if alpha_count < 5:
            continue
        # Skip copyright/year markers
        if re.search(r"copyright|please turn|dbe/november|nsc", line, re.IGNORECASE):
            continue
        for m in NUMBER_RE.finditer(line):
            by_paper[paper].append(m.group(0))

print(f"Papers loaded: {len(by_paper)}")
print()

# --- Aggregate all numbers ---
all_numbers = []
for paper, nums in by_paper.items():
    all_numbers.extend(nums)

print(f"Total numbers extracted: {len(all_numbers)}")
print()

# --- Frequency ---
freq = Counter(all_numbers)

# --- Magnitude distribution ---
def magnitude_bucket(n):
    try:
        v = abs(float(n))
    except ValueError:
        return "other"
    if v == 0:
        return "zero"
    if v < 1:
        return "fraction < 1"
    if v <= 10:
        return "1-10"
    if v <= 20:
        return "11-20"
    if v <= 50:
        return "21-50"
    if v <= 100:
        return "51-100"
    if v <= 1000:
        return "101-1000"
    return ">1000"

mag_dist = Counter(magnitude_bucket(n) for n in all_numbers)

# --- Sign distribution ---
sign_dist = Counter("negative" if n.startswith("-") else "positive" for n in all_numbers)

# --- Decimal distribution ---
decimal_count = sum(1 for n in all_numbers if "." in n)
integer_count = len(all_numbers) - decimal_count

# --- "Nice number" tests ---
# % that are 1-10
small_int_count = sum(1 for n in all_numbers if "." not in n and 1 <= abs(int(n)) <= 10 if n.lstrip("-").isdigit())
# % that are perfect squares
perfect_sq = 0
for n in all_numbers:
    if "." not in n and n.lstrip("-").isdigit():
        v = int(n)
        if v > 0 and int(sqrt(v)) ** 2 == v:
            perfect_sq += 1

# --- Divisibility test ---
# Count pairs of consecutive integers in the same question where one divides the other
# (this is complex; approximated by looking at question text)

# --- Chi-squared vs uniform ---
# If uniform over 1-100, expected ~1% each. Compare to observed concentration.
int_counts = Counter(int(n) for n in all_numbers if "." not in n and 1 <= int(n) <= 50 if n.lstrip("-").isdigit())
total_small = sum(int_counts.values()) or 1
# Top 10 most frequent small ints
top_10 = int_counts.most_common(10)
top_10_share = sum(c for _, c in top_10) / total_small if total_small else 0
# If uniform over 1-50, top 10 would hold 10/50 = 20% of the numbers
uniform_top_10 = 10 / 50
concentration_ratio = top_10_share / uniform_top_10 if uniform_top_10 else 0

# --- Decimal place text search ---
dec_asks = Counter()
for paper, texts in by_paper_raw.items():
    full_text = "\n".join(texts)
    for m in DECIMAL_ASK_RE.finditer(full_text):
        dec_asks[m.group(1).lower()] += 1

# --- Build report ---
lines = []
lines.append("# Examiner fingerprint — numbers")
lines.append("")
lines.append(f"**Papers scanned:** {len(by_paper)}")
lines.append(f"**Total numbers:** {len(all_numbers)}")
lines.append(f"**Unique numbers:** {len(freq)}")
lines.append("")

lines.append("## 1. Top 30 most frequent numbers")
lines.append("")
lines.append("| Rank | Number | Count |")
lines.append("|---|---|---|")
for i, (num, count) in enumerate(freq.most_common(30), 1):
    lines.append(f"| {i} | {num} | {count} |")
lines.append("")

lines.append("## 2. Magnitude distribution")
lines.append("")
lines.append("| Bucket | Count | % |")
lines.append("|---|---|---|")
total = len(all_numbers)
for bucket in ["zero", "fraction < 1", "1-10", "11-20", "21-50", "51-100", "101-1000", ">1000", "other"]:
    c = mag_dist.get(bucket, 0)
    lines.append(f"| {bucket} | {c} | {100*c/total:.1f}% |")
lines.append("")

lines.append("## 3. Sign distribution")
lines.append("")
lines.append("| Sign | Count | % |")
lines.append("|---|---|---|")
for sign, c in sign_dist.items():
    lines.append(f"| {sign} | {c} | {100*c/total:.1f}% |")
lines.append("")

lines.append("## 4. Decimal distribution")
lines.append("")
lines.append(f"- Integers: {integer_count} ({100*integer_count/total:.1f}%)")
lines.append(f"- Decimals: {decimal_count} ({100*decimal_count/total:.1f}%)")
lines.append("")

lines.append("## 5. Optimisation tests")
lines.append("")
lines.append(f"- **Small integer (1–10):** {small_int_count} ({100*small_int_count/total:.1f}%)")
lines.append(f"- **Perfect squares:** {perfect_sq} ({100*perfect_sq/total:.1f}%)")
lines.append(f"- **Top 10 integers hold {100*top_10_share:.1f}% of small-integer mass**")
lines.append(f"- **Uniform expectation:** 20.0%")
lines.append(f"- **Concentration ratio:** {concentration_ratio:.2f}x — {'OPTIMISED' if concentration_ratio > 1.5 else 'near-random'}")
lines.append("")

lines.append("## 6. Decimal conventions in question text")
lines.append("")
lines.append("| Phrase | Occurrences |")
lines.append("|---|---|")
for phrase, count in dec_asks.most_common():
    lines.append(f"| {phrase} | {count} |")
lines.append("")

# --- Write files ---
(OUT_DIR / "numbers_report.md").write_text("\n".join(lines), encoding="utf-8")

# JSON dump for the machine
data = {
    "total_numbers": len(all_numbers),
    "unique_numbers": len(freq),
    "top_100": freq.most_common(100),
    "magnitude_distribution": dict(mag_dist),
    "sign_distribution": dict(sign_dist),
    "integer_count": integer_count,
    "decimal_count": decimal_count,
    "small_int_count": small_int_count,
    "perfect_squares": perfect_sq,
    "concentration_ratio": concentration_ratio,
    "decimal_asks": dict(dec_asks),
}
(OUT_DIR / "numbers_fingerprint.json").write_text(
    json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
)

print("\n".join(lines))
print()
print(f"Wrote {OUT_DIR / 'numbers_report.md'}")
print(f"Wrote {OUT_DIR / 'numbers_fingerprint.json'}")