"""
Diagram frequency fingerprint.
Reads OCR'd exam pages, splits by question, classifies figure types,
groups by topic.
"""
import re
import json
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd

PAGES_DIR = Path("data/processed/diagrams/pages")
MAP_DIR = Path("data/processed/mapped")
OUT_DIR = Path("data/processed/fingerprint")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Figure type patterns (order matters — most specific first) ---
FIGURE_PATTERNS = [
    ("ogive",       r"\bogive\b|cumulative frequency curve"),
    ("histogram",   r"\bhistogram\b"),
    ("box_plot",    r"box[- ]and[- ]whisker|box plot|\bboxplot\b"),
    ("scatter",     r"scatter\s+plot|scatter\s+diagram"),
    ("venn",        r"\bvenn\b"),
    ("tree_diagram", r"tree\s+diagram"),
    ("number_line", r"number\s+line"),
    ("cylinder",    r"\bcylinder\b|\bcylindrical\b"),
    ("rectangular", r"rectangular\s+(backdrop|sheet|box|prism)|rectangular\s+block"),
    ("3d_trig",     r"vertical\s+pole|right[- ]angled\s+triangle.*horizontal|"
                    r"horizontal\s+base|foot\s+of.*pole|angle\s+of\s+elevation|"
                    r"\b3d\b|three[- ]dimensional"),
    ("parabola",    r"\bparabola\b|shape\s+of\s+f|turning\s+point\s+of\s+f"),
    ("hyperbola",   r"\bhyperbola\b|\basymptote"),
    ("exponential", r"exponential\s+(graph|function)|f\(x\)\s*=\s*\d+\^x|logarithmic"),
    ("log_graph",   r"logarithmic|log\s+graph|log_"),
    ("trig_graph",  r"(sin|cos|tan)\s+x.*(sketch|graph|draw)|"
                    r"amplitude|period.*graph|graph\s+of.*(sin|cos|tan)|"
                    r"f\(x\)\s*=\s*(sin|cos|tan)"),
    ("circle_geom", r"\bcircle\b.*(centre|center|tangent|chord|cyclic|diameter|"
                    r"radius|arc|semicircle)|cyclic\s+quad|concyclic"),
    ("triangle_geom", r"\btriangle\s+[A-Z]{2,}|△|isosceles|equilateral"),
    ("quadrilateral", r"\bquadrilateral\b|parallelogram|rhombus|trapezium|kite"),
    ("graph_general", r"\bsketch\b|on\s+the\s+grid|on\s+the\s+set\s+of\s+axes|"
                      r"in\s+the\s+answer\s+book|drawn\s+to\s+scale"),
]

# --- Per-question scan ---
Q_HEAD_RE = re.compile(r"QUESTION\s+(\d+)\b", re.IGNORECASE)
DIAGRAM_RE = re.compile(r"\bdiagram\b|\bfigure\b|\bsketch\b|\bgraph\b", re.IGNORECASE)
NOT_TO_SCALE_RE = re.compile(r"not\s+(drawn\s+to|necessarily\s+drawn\s+to)\s+scale", re.IGNORECASE)

# Topic lookup
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

# Group pages by paper
paper_pages = defaultdict(list)
for txt in sorted(PAGES_DIR.glob("*_exam_maths_p*.txt")):
    stem = txt.stem
    paper = stem.rsplit("_p", 1)[0]
    try:
        pn = int(stem.rsplit("_p", 1)[1])
    except ValueError:
        continue
    content = txt.read_text(encoding="utf-8", errors="ignore")
    paper_pages[paper].append((pn, content))

for p in paper_pages:
    paper_pages[p].sort()

print(f"Papers: {len(paper_pages)}")
print()

# Scan
figures_by_topic = defaultdict(Counter)     # topic -> figure -> count
diagram_by_topic = defaultdict(int)         # topic -> # questions with diagram
q_total_by_topic = Counter()                # topic -> # questions
figures_by_year = defaultdict(Counter)      # year -> figure -> count
not_to_scale_by_topic = Counter()

# Per-question records for JSON dump
questions_with_figures = []

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

        topic = topic_lookup.get((year, paper_code, qnum))
        if not topic:
            continue

        q_total_by_topic[topic] += 1

        # Does this block reference a diagram at all?
        has_diagram = bool(DIAGRAM_RE.search(block))
        if has_diagram:
            diagram_by_topic[topic] += 1

        if NOT_TO_SCALE_RE.search(block):
            not_to_scale_by_topic[topic] += 1

        # Classify figure types
        found_figs = []
        for fig_name, pat in FIGURE_PATTERNS:
            if re.search(pat, block, re.IGNORECASE):
                figures_by_topic[topic][fig_name] += 1
                figures_by_year[year][fig_name] += 1
                found_figs.append(fig_name)

        if found_figs:
            questions_with_figures.append({
                "year": year,
                "paper": paper_code,
                "question_number": qnum,
                "topic": topic,
                "figures": found_figs,
            })

print(f"Questions with figures: {len(questions_with_figures)}")
print()

# --- Report ---
lines = []
lines.append("# Fingerprint — diagram frequency")
lines.append("")
lines.append(f"**Total questions scanned:** {sum(q_total_by_topic.values())}")
lines.append(f"**Questions with figures:** {len(questions_with_figures)}")
lines.append("")

lines.append("## % of questions mentioning a diagram, per topic")
lines.append("")
lines.append("| Topic | Questions | With diagram | % | Not to scale |")
lines.append("|---|---|---|---|---|")
for topic in sorted(q_total_by_topic.keys()):
    total = q_total_by_topic[topic]
    with_diag = diagram_by_topic[topic]
    pct = 100 * with_diag / total if total else 0
    nts = not_to_scale_by_topic[topic]
    lines.append(f"| {topic} | {total} | {with_diag} | {pct:.0f}% | {nts} |")
lines.append("")

lines.append("## Figure type frequency per topic")
lines.append("")
all_figs = sorted({fig for c in figures_by_topic.values() for fig in c.keys()})
header = "| Topic | " + " | ".join(all_figs) + " |"
sep = "|---|" + "|".join(["---"] * len(all_figs)) + "|"
lines.append(header)
lines.append(sep)
for topic in sorted(figures_by_topic.keys()):
    row = [f"| {topic} "]
    for fig in all_figs:
        row.append(f"| {figures_by_topic[topic].get(fig, 0)} ")
    row.append("|")
    lines.append("".join(row))
lines.append("")

lines.append("## Figure frequency by year")
lines.append("")
all_years = sorted(figures_by_year.keys())
header = "| Year | " + " | ".join(all_figs) + " |"
sep = "|---|" + "|".join(["---"] * len(all_figs)) + "|"
lines.append(header)
lines.append(sep)
for year in all_years:
    row = [f"| {year} "]
    for fig in all_figs:
        row.append(f"| {figures_by_year[year].get(fig, 0)} ")
    row.append("|")
    lines.append("".join(row))
lines.append("")

lines.append("## Overall frequency")
lines.append("")
overall = Counter()
for c in figures_by_topic.values():
    overall.update(c)
lines.append("| Figure | Total |")
lines.append("|---|---|")
for fig, c in overall.most_common():
    lines.append(f"| {fig} | {c} |")
lines.append("")

(OUT_DIR / "diagram_report.md").write_text("\n".join(lines), encoding="utf-8")

data = {
    "diagram_pct_by_topic": {t: {
        "total": q_total_by_topic[t],
        "with_diagram": diagram_by_topic[t],
    } for t in q_total_by_topic},
    "figures_by_topic": {t: dict(c) for t, c in figures_by_topic.items()},
    "figures_by_year": {y: dict(c) for y, c in figures_by_year.items()},
    "questions_with_figures": questions_with_figures,
}
(OUT_DIR / "diagram_fingerprint.json").write_text(
    json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
)

print("\n".join(lines[:80]))
print()
print(f"Report: {OUT_DIR / 'diagram_report.md'}")