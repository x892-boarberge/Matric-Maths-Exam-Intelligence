"""
Marks + sequencing fingerprint.
Reads all 2014-2025 mapped questions, extracts:
  - marks per question
  - sub-questions per question
  - individual sub-question mark values
  - distribution patterns per topic
"""
import re
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd

MAP_DIR = Path("data/processed/mapped")
OUT_DIR = Path("data/processed/fingerprint")
OUT_DIR.mkdir(parents=True, exist_ok=True)

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
        if "topic_v2" not in df.columns:
            continue
        for _, r in df.iterrows():
            year = r.get("year")
            paper = str(r.get("paper", "") or "").strip()
            qnum = str(r.get("question_number", "") or "").strip()
            subq = str(r.get("subquestion", "") or "").strip()
            topic = str(r.get("topic_v2", "") or "").strip()
            try:
                marks = float(r.get("marks"))
            except (ValueError, TypeError):
                marks = None
            if not topic or topic.lower() in ("nan", "none", ""):
                continue
            if not qnum:
                continue
            # Clean qnum (remove .0)
            qnum = qnum.split(".")[0]
            rows.append({
                "year": year,
                "paper": paper,
                "question_number": qnum,
                "subquestion": subq,
                "marks": marks,
                "topic": topic,
            })

print(f"Total subquestion rows: {len(rows)}")
print()

# --- Group by question ---
by_question = defaultdict(list)
for r in rows:
    key = (r["year"], r["paper"], r["question_number"], r["topic"])
    by_question[key].append(r)

print(f"Total questions: {len(by_question)}")
print()

# --- Aggregate per question ---
question_stats = []
for (year, paper, qnum, topic), subs in by_question.items():
    marks_list = [s["marks"] for s in subs if s["marks"] is not None]
    total_marks = sum(m for m in marks_list if m == m) if marks_list else 0  # m == m filters NaN
    n_subs = len(subs)
    question_stats.append({
        "year": year, "paper": paper, "question_number": qnum, "topic": topic,
        "n_subquestions": n_subs,
        "total_marks": total_marks,
        "marks_per_sub": marks_list,
    })

# --- Per-topic aggregates ---
by_topic = defaultdict(lambda: {
    "question_count": 0,
    "sub_count": 0,
    "total_marks": 0,
    "sub_marks": [],
    "questions_marks": [],
})

for q in question_stats:
    t = by_topic[q["topic"]]
    t["question_count"] += 1
    t["sub_count"] += q["n_subquestions"]
    if q["total_marks"] == q["total_marks"]:
        t["total_marks"] += q["total_marks"]
    t["sub_marks"].extend(q["marks_per_sub"])
    t["questions_marks"].append(q["total_marks"])

# --- Report ---
lines = []
lines.append("# Fingerprint — marks & sequencing")
lines.append("")
lines.append(f"**Questions:** {len(question_stats)}")
lines.append(f"**Sub-questions:** {len(rows)}")
lines.append("")

# Per-topic summary
lines.append("## Per-topic summary")
lines.append("")
lines.append("| Topic | Questions | Sub-Qs/Question | Marks/Question | Marks/Sub-Q | Most common sub-mark |")
lines.append("|---|---|---|---|---|---|")
for topic in sorted(by_topic.keys()):
    t = by_topic[topic]
    qc = t["question_count"] or 1
    sc = t["sub_count"] or 1
    avg_subs = t["sub_count"] / qc
    avg_marks = t["total_marks"] / qc
    avg_sub_mark = sum(t["sub_marks"]) / len(t["sub_marks"]) if t["sub_marks"] else 0
    mc = Counter(t["sub_marks"]).most_common(1)
    most_common = f"{mc[0][0]}" if mc else "-"
    lines.append(
        f"| {topic} | {t['question_count']} | {avg_subs:.1f} | "
        f"{avg_marks:.1f} | {avg_sub_mark:.1f} | {most_common} |"
    )
lines.append("")

# Marks distribution
lines.append("## Overall — sub-question mark distribution")
lines.append("")
all_sub_marks = [m for t in by_topic.values() for m in t["sub_marks"]]
mc_all = Counter(all_sub_marks)
lines.append("| Marks | Count | % |")
lines.append("|---|---|---|")
total = sum(mc_all.values()) or 1
for mark, c in sorted(mc_all.items()):
    lines.append(f"| {mark} | {c} | {100*c/total:.1f}% |")
lines.append("")

# Sub-questions per question distribution
lines.append("## Overall — sub-questions per question")
lines.append("")
subs_per_q = [q["n_subquestions"] for q in question_stats]
mc_q = Counter(subs_per_q)
lines.append("| Sub-Qs | Count | % |")
lines.append("|---|---|---|")
for n, c in sorted(mc_q.items()):
    lines.append(f"| {n} | {c} | {100*c/len(question_stats):.1f}% |")
lines.append("")

# Marks per question distribution
lines.append("## Overall — total marks per question")
lines.append("")
marks_per_q = [q["total_marks"] for q in question_stats]
mc_m = Counter(marks_per_q)
lines.append("| Total marks | Count |")
lines.append("|---|---|")
for m, c in sorted(mc_m.items()):
    lines.append(f"| {m} | {c} |")
lines.append("")

# Per-topic detail
lines.append("## Per-topic detail")
lines.append("")
for topic in sorted(by_topic.keys()):
    t = by_topic[topic]
    lines.append(f"### {topic}")
    lines.append(f"- Questions: {t['question_count']}")
    lines.append(f"- Sub-questions: {t['sub_count']}")
    tm = t['total_marks']
    if tm != tm:
        tm = 0
    lines.append(f"- Marks: {int(tm)}")
    mc = Counter(t["sub_marks"]).most_common(5)
    lines.append(f"- Common sub-marks: " + ", ".join(f"{m}×{c}" for m, c in mc))
    lines.append("")

# Write
(OUT_DIR / "marks_sequencing_report.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[:80]))
print()
print(f"Full report: {OUT_DIR / 'marks_sequencing_report.md'}")