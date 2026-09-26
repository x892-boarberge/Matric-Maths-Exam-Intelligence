"""
Marks + sequencing fingerprint v2.
Source: question_structure.csv (has marks) joined with mapped CSVs (has topic).
"""
import re
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd

ROOT = Path(".")
STRUCT_PATH = ROOT / "data" / "processed" / "questions" / "question_structure.csv"
MAP_DIR = ROOT / "data" / "processed" / "mapped"
OUT_DIR = ROOT / "data" / "processed" / "fingerprint"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Load structure ---
if not STRUCT_PATH.exists():
    print(f"Not found: {STRUCT_PATH}")
    raise SystemExit(1)

struct = pd.read_csv(STRUCT_PATH)
print(f"Structure rows: {len(struct)}")
print(f"Structure columns: {list(struct.columns)}")

# Normalise keys
def norm(v):
    if pd.isna(v):
        return ""
    return str(v).replace(".0", "").strip()

struct["_q"] = struct["question_number"].apply(norm)
struct["_s"] = struct["subquestion"].apply(norm)

# --- Load topic map: (year, paper, qnum, subq) -> topic ---
topic_rows = []
for year_dir in sorted(MAP_DIR.glob("20*")):
    if not year_dir.is_dir():
        continue
    for f in year_dir.glob("question_topic_map_*_v2.csv"):
        try:
            df = pd.read_csv(f)
        except Exception:
            continue
        if "topic_v2" not in df.columns:
            continue
        for _, r in df.iterrows():
            topic = str(r.get("topic_v2", "") or "").strip()
            if not topic or topic.lower() in ("nan", "none", ""):
                continue
            topic_rows.append({
                "year": r.get("year"),
                "paper": str(r.get("paper", "") or "").strip(),
                "q": norm(r.get("question_number")),
                "s": norm(r.get("subquestion")),
                "topic": topic,
            })

topics = pd.DataFrame(topic_rows)
print(f"Topic rows: {len(topics)}")

# --- Join ---
struct["year"] = struct["year"].astype(str)
topics["year"] = topics["year"].astype(str)

merged = struct.merge(
    topics,
    left_on=["year", "paper", "_q", "_s"],
    right_on=["year", "paper", "q", "s"],
    how="left",
)
print(f"Merged rows: {len(merged)}")
print(f"With topic: {merged['topic'].notna().sum()}")
print()

# --- Clean marks ---
def to_float(v):
    if pd.isna(v):
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None

merged["marks_f"] = merged["marks"].apply(to_float)
print(f"Rows with marks: {merged['marks_f'].notna().sum()}")
print()

# --- Aggregate per question ---
questions = defaultdict(lambda: {"subs": 0, "marks_total": 0.0, "sub_marks": [], "topic": ""})

for _, r in merged.iterrows():
    topic = r.get("topic", "")
    if pd.isna(topic) or not topic:
        continue
    key = (str(r["year"]), str(r["paper"]), str(r["_q"]))
    q = questions[key]
    q["topic"] = topic
    q["subs"] += 1
    m = r["marks_f"]
    if m is not None and m == m:
        q["marks_total"] += m
        q["sub_marks"].append(m)

# --- Per topic ---
by_topic = defaultdict(lambda: {
    "q_count": 0, "sub_count": 0, "marks_total": 0.0,
    "sub_marks": [], "question_marks": [],
})

for key, q in questions.items():
    t = by_topic[q["topic"]]
    t["q_count"] += 1
    t["sub_count"] += q["subs"]
    t["marks_total"] += q["marks_total"]
    t["sub_marks"].extend(q["sub_marks"])
    t["question_marks"].append(q["marks_total"])

# --- Report ---
lines = []
lines.append("# Fingerprint — marks & sequencing v2")
lines.append("")
lines.append(f"**Questions:** {len(questions)}")
lines.append(f"**Sub-questions:** {sum(q['subs'] for q in questions.values())}")
lines.append("")

lines.append("## Per-topic summary")
lines.append("")
lines.append("| Topic | Questions | Sub-Qs/Q | Marks/Q | Marks/Sub-Q | Most common sub-mark |")
lines.append("|---|---|---|---|---|---|")
for topic in sorted(by_topic.keys()):
    t = by_topic[topic]
    qc = t["q_count"] or 1
    avg_subs = t["sub_count"] / qc
    avg_marks = t["marks_total"] / qc
    avg_sub_mark = sum(t["sub_marks"]) / len(t["sub_marks"]) if t["sub_marks"] else 0
    mc = Counter(t["sub_marks"]).most_common(1)
    most_common = f"{mc[0][0]:.0f} ({mc[0][1]}x)" if mc else "-"
    lines.append(
        f"| {topic} | {t['q_count']} | {avg_subs:.1f} | "
        f"{avg_marks:.1f} | {avg_sub_mark:.1f} | {most_common} |"
    )
lines.append("")

# Overall sub-mark distribution
all_sub_marks = [m for t in by_topic.values() for m in t["sub_marks"]]
mc_all = Counter(all_sub_marks)
lines.append("## Overall sub-question mark distribution")
lines.append("")
lines.append("| Marks | Count | % |")
lines.append("|---|---|---|")
total = sum(mc_all.values()) or 1
for mark, c in sorted(mc_all.items()):
    lines.append(f"| {int(mark)} | {c} | {100*c/total:.1f}% |")
lines.append("")

# Subs per question
subs_per_q = [q["subs"] for q in questions.values()]
mc_q = Counter(subs_per_q)
lines.append("## Sub-questions per question")
lines.append("")
lines.append("| Sub-Qs | Count | % |")
lines.append("|---|---|---|")
for n, c in sorted(mc_q.items()):
    lines.append(f"| {n} | {c} | {100*c/len(questions):.1f}% |")
lines.append("")

# Marks per question
marks_per_q = [q["marks_total"] for q in questions.values()]
mc_m = Counter(marks_per_q)
lines.append("## Total marks per question")
lines.append("")
lines.append("| Total marks | Count |")
lines.append("|---|---|")
for m, c in sorted(mc_m.items()):
    lines.append(f"| {int(m)} | {c} |")
lines.append("")

# Per-topic detail
lines.append("## Per-topic detail")
lines.append("")
for topic in sorted(by_topic.keys()):
    t = by_topic[topic]
    lines.append(f"### {topic}")
    lines.append(f"- Questions: {t['q_count']}")
    lines.append(f"- Sub-questions: {t['sub_count']}")
    lines.append(f"- Total marks: {int(t['marks_total'])}")
    mc = Counter(t["sub_marks"]).most_common(5)
    lines.append("- Common sub-marks: " + ", ".join(f"{int(m)}×{c}" for m, c in mc))
    lines.append("")

(OUT_DIR / "marks_sequencing_report.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[:80]))
print()
print(f"Report: {OUT_DIR / 'marks_sequencing_report.md'}")