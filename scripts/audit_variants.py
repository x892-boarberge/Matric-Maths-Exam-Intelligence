"""Audit every topic's variants — show samples, flag thin pools."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tutor.analogue_library import SKILL_TO_TEMPLATE, POOL

# Group skills by topic
TOPIC_PREFIX = {
    "algebra.": "ALG",
    "sequences.": "SEQ",
    "functions.": "FUNC",
    "finance.": "FIN",
    "calculus.": "CALC",
    "probability.": "PROB",
    "trig.": "TRIG",
    "euclidean.": "EUCL",
    "analytical_geom.": "AGEO",
    "stats.": "STAT",
}

# Build topic -> list of (skill, template) pairs
by_topic = {}
for skill, tmpl in SKILL_TO_TEMPLATE.items():
    for prefix, code in TOPIC_PREFIX.items():
        if skill.startswith(prefix):
            by_topic.setdefault(code, []).append((skill, tmpl))
            break

order = ["ALG", "SEQ", "FUNC", "FIN", "CALC", "PROB", "STAT", "TRIG", "AGEO", "EUCL"]

print("=" * 78)
print("  Variant audit — every topic")
print("=" * 78)

for topic in order:
    if topic not in by_topic:
        continue
    print()
    print(f"### {topic}")
    print("-" * 78)
    # Collect distinct templates under this topic
    templates_seen = set()
    for skill, tmpl in by_topic[topic]:
        if tmpl in templates_seen:
            continue
        templates_seen.add(tmpl)
        pool = POOL.get(tmpl, [])
        n = len(pool)
        # Flag
        if n == 0:
            flag = "❌ EMPTY"
        elif n < 5:
            flag = "⚠️  WRITTEN"
        elif n < 20:
            flag = "⚠️  THIN"
        else:
            flag = "✅"
        print(f"  {flag}  {tmpl:38s}  {n:3d} variants")
        # Show 2 samples
        for v in pool[:2]:
            problem = v.get("problem", "")[:70]
            print(f"        → {problem}")
    print()

# Summary
print("=" * 78)
print("  Summary")
print("=" * 78)

all_templates = set(SKILL_TO_TEMPLATE.values())
by_size = {"empty": [], "written": [], "thin": [], "good": []}
for t in sorted(all_templates):
    n = len(POOL.get(t, []))
    if n == 0:
        by_size["empty"].append(t)
    elif n < 5:
        by_size["written"].append((t, n))
    elif n < 20:
        by_size["thin"].append((t, n))
    else:
        by_size["good"].append((t, n))

print(f"  Good (20+):     {len(by_size['good'])}")
print(f"  Thin (5-19):    {len(by_size['thin'])}")
print(f"  Written (<5):   {len(by_size['written'])}")
print(f"  Empty (0):      {len(by_size['empty'])}")
print()

if by_size["empty"]:
    print("  EMPTY templates — need a generator:")
    for t in by_size["empty"]:
        print(f"    - {t}")
    print()

if by_size["written"]:
    print("  WRITTEN templates — hand-authored, only a few entries:")
    for t, n in by_size["written"]:
        print(f"    - {t:40s} ({n})")
    print()

if by_size["thin"]:
    print("  THIN templates — under 20 variants:")
    for t, n in by_size["thin"]:
        print(f"    - {t:40s} ({n})")