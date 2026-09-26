"""
Phrase fingerprint.
Extracts command verbs and instruction phrases from all 12 years of OCR'd papers.
"""
import re
import json
from pathlib import Path
from collections import Counter, defaultdict

PAGES_DIR = Path("data/processed/diagrams/pages")
MAP_DIR = Path("data/processed/mapped")
OUT_DIR = Path("data/processed/fingerprint")
OUT_DIR.mkdir(parents=True, exist_ok=True)

import pandas as pd

# --- Command verbs (root forms) ---
COMMAND_VERBS = [
    "Calculate", "Determine", "Solve", "Show that", "Prove", "Write down",
    "Sketch", "Draw", "Hence", "Deduce", "Evaluate", "Simplify",
    "Factorise", "Expand", "Interpret", "Describe", "Compare",
    "Explain", "State", "Give reasons", "Show", "Find", "Complete",
    "Use the", "Verify", "Justify", "Give", "Comment on", "Discuss",
]

# --- Instruction phrases (multi-word) ---
INSTRUCTION_PHRASES = [
    "correct to TWO decimal places",
    "correct to two decimal places",
    "round off answers to TWO decimal places",
    "round off answers to two decimal places",
    "leave your answer in surd form",
    "leave your answer in simplified surd form",
    "without using a calculator",
    "show that",
    "hence, or otherwise",
    "hence or otherwise",
    "refer to the diagram",
    "not drawn to scale",
    "diagrams are not necessarily drawn to scale",
    "answer only",
    "give reasons",
    "provide reasons",
    "in the ANSWER BOOK",
    "on the set of axes",
    "on the grid",
    "you may use an approved scientific calculator",
    "if necessary, round off",
    "if necessary round off",
]

# --- Topic lookup ---
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

print(f"Topic lookup: {len(topic_lookup)}")
print()

# --- Group paper text ---
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
print()

# --- Extract phrases per topic ---
verb_by_topic = defaultdict(Counter)
instr_by_topic = defaultdict(Counter)
verb_by_year = defaultdict(Counter)
instr_by_year = defaultdict(Counter)

Q_HEAD_RE = re.compile(r"QUESTION\s+(\d+)\b", re.IGNORECASE)

for paper, pages in paper_pages.items():
    full_text = "\n".join(t for _, t in pages)
    parts = paper.split("_")
    if len(parts) < 3:
        continue
    year = parts[0]
    paper_code = parts[2].upper()

    # Split into questions
    q_matches = list(Q_HEAD_RE.finditer(full_text))
    if not q_matches:
        continue

    for i, m in enumerate(q_matches):
        qnum = m.group(1)
        start = m.end()
        end = q_matches[i + 1].start() if i + 1 < len(q_matches) else len(full_text)
        block = full_text[start:end]
        topic = topic_lookup.get((year, paper_code, qnum))

        # Count command verbs (case-insensitive)
        for verb in COMMAND_VERBS:
            # Word-boundary match
            pat = re.compile(r"\b" + re.escape(verb) + r"\b", re.IGNORECASE)
            n = len(pat.findall(block))
            if n > 0:
                if topic:
                    verb_by_topic[topic][verb] += n
                verb_by_year[year][verb] += n

        # Count instruction phrases
        low = block.lower()
        for phrase in INSTRUCTION_PHRASES:
            n = low.count(phrase.lower())
            if n > 0:
                if topic:
                    instr_by_topic[topic][phrase] += n
                instr_by_year[year][phrase] += n

# --- Report ---
lines = []
lines.append("# Fingerprint — examiner's language")
lines.append("")

lines.append("## Overall — most-used command verbs")
lines.append("")
total_verbs = Counter()
for year_counter in verb_by_year.values():
    total_verbs.update(year_counter)
lines.append("| Rank | Verb | Count |")
lines.append("|---|---|---|")
for i, (verb, c) in enumerate(total_verbs.most_common(30), 1):
    lines.append(f"| {i} | {verb} | {c} |")
lines.append("")

lines.append("## Overall — instruction phrases")
lines.append("")
total_instr = Counter()
for yc in instr_by_year.values():
    total_instr.update(yc)
lines.append("| Rank | Phrase | Count |")
lines.append("|---|---|---|")
for i, (phrase, c) in enumerate(total_instr.most_common(20), 1):
    lines.append(f"| {i} | {phrase} | {c} |")
lines.append("")

lines.append("## Per-topic command verbs (top 8 per topic)")
lines.append("")
for topic in sorted(verb_by_topic.keys()):
    lines.append(f"### {topic}")
    lines.append("")
    lines.append("| Verb | Count |")
    lines.append("|---|---|")
    for verb, c in verb_by_topic[topic].most_common(8):
        lines.append(f"| {verb} | {c} |")
    lines.append("")

lines.append("## Per-topic instruction phrases (top 5 per topic)")
lines.append("")
for topic in sorted(instr_by_topic.keys()):
    lines.append(f"### {topic}")
    lines.append("")
    lines.append("| Phrase | Count |")
    lines.append("|---|---|")
    for phrase, c in instr_by_topic[topic].most_common(5):
        lines.append(f"| {phrase} | {c} |")
    lines.append("")

# Write
(OUT_DIR / "phrases_report.md").write_text("\n".join(lines), encoding="utf-8")

# JSON dump
data = {
    "command_verbs_overall": dict(total_verbs.most_common(50)),
    "instruction_phrases_overall": dict(total_instr.most_common(30)),
    "verbs_by_topic": {t: dict(c.most_common(15)) for t, c in verb_by_topic.items()},
    "instructions_by_topic": {t: dict(c.most_common(10)) for t, c in instr_by_topic.items()},
    "verbs_by_year": {y: dict(c) for y, c in verb_by_year.items()},
}
(OUT_DIR / "phrases_fingerprint.json").write_text(
    json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
)

print("\n".join(lines[:100]))
print()
print(f"Report: {OUT_DIR / 'phrases_report.md'}")