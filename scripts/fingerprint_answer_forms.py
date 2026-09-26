"""
Answer form fingerprint.
Reads memo answers, classifies each expected answer by form,
groups by topic.
"""
import re
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd

MEMO_DIR = Path("data/processed/memo_answers")
OUT_DIR = Path("data/processed/fingerprint")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def classify_answer(ans):
    """Return list of form tags for one answer string."""
    if not isinstance(ans, str) or not ans.strip():
        return ["empty"]
    a = ans.strip()
    tags = []

    # Monetary
    if re.search(r"R\s*\d", a):
        tags.append("monetary")

    # Coordinate pair (2; 3) or (x; y)
    if re.search(r"\(\s*-?\d+(?:[.,]\d+)?\s*;\s*-?\d+(?:[.,]\d+)?\s*\)", a):
        tags.append("coordinate")
    # Named point + coordinate
    if re.search(r"[A-Z]\s*\(\s*-?\d+(?:[.,]\d+)?\s*;", a):
        tags.append("coordinate")

    # Surd
    if re.search(r"sqrt|√|\broot\b", a, re.IGNORECASE):
        tags.append("surd")
    # Rational exponent form: 2^(1/2), (1/2)^21
    if re.search(r"\^\s*\(?\s*-?\d+\s*/\s*\d+\s*\)?", a):
        tags.append("exponential")

    # Fraction a/b (either explicit fraction or a/b form)
    if re.search(r"-?\d+\s*/\s*-?\d+", a):
        tags.append("fraction")

    # Decimal (with point or comma)
    if re.search(r"-?\d+[.,]\d+", a):
        tags.append("decimal")

    # Integer (only digits, or "x = N")
    if re.search(r"^\s*[a-zA-Z]?\s*=?\s*-?\d+\s*$", a):
        tags.append("integer")

    # Interval / inequality
    if re.search(r"<\s*x\s*<|x\s*[<>]|<=\s*x|>=\s*x|x\s*<=|x\s*>=", a):
        tags.append("inequality")
    if re.search(r"\[\s*-?\d|\]\s*or\s*\[|\(-inf|\(-∞", a):
        tags.append("interval")

    # Prose proof result
    if re.search(
        r"\bis a\b|\bproved\b|is a diameter|is perpendicular|is parallel|"
        r"is similar|is a tangent|cyclic|concyclic|similar|tangent",
        a, re.IGNORECASE,
    ):
        tags.append("proof_prose")

    # Expression in x, n, T_n, etc.
    if re.search(r"[a-zA-Z]\s*[\^=]|T_n|f\(|y\s*=", a):
        tags.append("expression")

    if not tags:
        tags.append("other")

    return tags


# --- Load all memo answer files ---
rows = []
for f in sorted(MEMO_DIR.glob("memo_answers_*_P*.csv")):
    try:
        df = pd.read_csv(f)
    except Exception:
        continue
    for _, r in df.iterrows():
        ans = str(r.get("expected_answer", "") or "")
        skill = str(r.get("skill_id", "") or "")
        # Derive topic from skill_id prefix
        topic = ""
        if skill.startswith("algebra."):
            topic = "ALG"
        elif skill.startswith("sequences."):
            topic = "SEQ"
        elif skill.startswith("functions."):
            topic = "FUNC"
        elif skill.startswith("finance."):
            topic = "FIN"
        elif skill.startswith("calculus."):
            topic = "CALC"
        elif skill.startswith("probability."):
            topic = "PROB"
        elif skill.startswith("trig."):
            topic = "TRIG"
        elif skill.startswith("analytical_geom."):
            topic = "AGEO"
        elif skill.startswith("euclidean."):
            topic = "EUCL"
        elif skill.startswith("stats."):
            topic = "STAT"
        if not topic:
            continue
        rows.append({
            "year": r.get("year"),
            "paper": r.get("paper"),
            "skill_id": skill,
            "topic": topic,
            "answer": ans,
        })

print(f"Total memo answers: {len(rows)}")
print()

# --- Classify all ---
for r in rows:
    r["forms"] = classify_answer(r["answer"])

# --- Per-topic breakdown ---
by_topic = defaultdict(Counter)
total_by_topic = Counter()

for r in rows:
    total_by_topic[r["topic"]] += 1
    for tag in set(r["forms"]):
        by_topic[r["topic"]][tag] += 1

# --- Report ---
lines = []
lines.append("# Fingerprint — answer forms")
lines.append("")
lines.append(f"**Total memo answers classified:** {len(rows)}")
lines.append(f"**Topics:** {len(total_by_topic)}")
lines.append("")

# Summary
lines.append("## Answer form distribution per topic")
lines.append("")

all_forms = set()
for c in by_topic.values():
    all_forms.update(c.keys())
all_forms = sorted(all_forms)

header = "| Topic | Total | " + " | ".join(all_forms) + " |"
sep = "|---|---|" + "|".join(["---"] * len(all_forms)) + "|"
lines.append(header)
lines.append(sep)

for topic in sorted(total_by_topic.keys()):
    n = total_by_topic[topic]
    row = [f"| {topic} | {n} "]
    for form in all_forms:
        pct = 100 * by_topic[topic].get(form, 0) / n if n else 0
        row.append(f"| {pct:.0f}% ")
    row.append("|")
    lines.append("".join(row))
lines.append("")

# Overall
overall = Counter()
for c in by_topic.values():
    overall.update(c)
n_total = len(rows) or 1
lines.append("## Overall (all topics)")
lines.append("")
lines.append("| Form | Count | % |")
lines.append("|---|---|---|")
for form, c in overall.most_common():
    lines.append(f"| {form} | {c} | {100*c/n_total:.1f}% |")
lines.append("")

# Sample answers per topic per dominant form
lines.append("## Sample answers per topic (dominant form)")
lines.append("")
for topic in sorted(by_topic.keys()):
    forms = by_topic[topic]
    if not forms:
        continue
    top_form, _ = forms.most_common(1)[0]
    samples = [r["answer"] for r in rows
               if r["topic"] == topic and top_form in r["forms"]][:5]
    lines.append(f"### {topic} — dominant form: **{top_form}**")
    lines.append("")
    for s in samples:
        lines.append(f"- `{s}`")
    lines.append("")

# Write
(OUT_DIR / "answer_forms_report.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
print()
print(f"Report: {OUT_DIR / 'answer_forms_report.md'}")