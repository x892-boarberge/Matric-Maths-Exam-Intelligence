"""Fix: serve the anchor question first, then variations."""
from pathlib import Path
import ast

P = Path("src/tutor/drill.py")
src = P.read_text(encoding="utf-8-sig")

# Replace the main loop structure
old = '''    cycle = pool.copy()
    random.shuffle(cycle)
    cycle_idx = 0
    shown_keys = set()

    correct_count = 0
    total_count = 0

    for q_num in range(1, VARIATIONS_PER_TEMPLATE + 1):
        if cycle_idx >= len(cycle):
            cycle_idx = 0
            random.shuffle(cycle)
        analogue = cycle[cycle_idx]
        cycle_idx += 1
        shown_keys.add(analogue_library.analogue_key(analogue))

        drill_problem = _analogue_to_problem(analogue, template_id, anchor.skill_id)

        print()
        print("-" * 60)
        print(f"  Problem: {drill_problem.prompt}")
        print("-" * 60)'''

new = '''    cycle = pool.copy()
    random.shuffle(cycle)
    cycle_idx = 0
    shown_keys = set()

    correct_count = 0
    total_count = 0

    # Build the question sequence: anchor first, then variations
    question_sequence = []
    # Q1: the anchor itself
    anchor_has_answer = bool(anchor.expected_answer and anchor.expected_answer.strip())
    if anchor_has_answer:
        question_sequence.append({
            "type": "anchor",
            "problem": anchor,
            "label": "the original question you picked",
        })

    # Then fill with variations
    variations_needed = VARIATIONS_PER_TEMPLATE - len(question_sequence)
    for _ in range(variations_needed):
        if cycle_idx >= len(cycle):
            cycle_idx = 0
            random.shuffle(cycle)
        analogue = cycle[cycle_idx]
        cycle_idx += 1
        shown_keys.add(analogue_library.analogue_key(analogue))
        question_sequence.append({
            "type": "variation",
            "problem": _analogue_to_problem(analogue, template_id, anchor.skill_id),
            "label": "a variation",
        })

    for q_num, q_item in enumerate(question_sequence, 1):
        drill_problem = q_item["problem"]

        print()
        print("-" * 60)
        print(f"  Problem: {drill_problem.prompt}")
        if q_item["type"] == "anchor":
            print(f"  (This is {q_item['label']}.)")
        print("-" * 60)'''

if old in src:
    src = src.replace(old, new, 1)
    print("Fixed: anchor served first, then variations")
else:
    print("WARN: main loop anchor not found")
    idx = src.find("cycle = pool.copy()")
    if idx > 0:
        print(repr(src[idx:idx+800]))

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)