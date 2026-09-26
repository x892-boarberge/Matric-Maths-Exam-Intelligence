"""Fix: handle NaN in total_marks."""
from pathlib import Path
import ast

P = Path("scripts/fingerprint_marks.py")
src = P.read_text(encoding="utf-8-sig")

old = '''    total_marks = sum(marks_list) if marks_list else 0'''

new = '''    total_marks = sum(m for m in marks_list if m == m) if marks_list else 0  # m == m filters NaN'''

if old in src:
    src = src.replace(old, new, 1)
    print("Fixed NaN in total_marks")
else:
    print("WARN: anchor not found")

# Also guard the report line
old2 = '''    lines.append(f"- Marks: {int(t['total_marks'])}")'''
new2 = '''    tm = t['total_marks']
    if tm != tm:
        tm = 0
    lines.append(f"- Marks: {int(tm)}")'''

if old2 in src:
    src = src.replace(old2, new2, 1)
    print("Fixed NaN in report line")

# And the per-topic aggregate
old3 = '''    t["total_marks"] += q["total_marks"]'''
new3 = '''    if q["total_marks"] == q["total_marks"]:
        t["total_marks"] += q["total_marks"]'''

if old3 in src:
    src = src.replace(old3, new3, 1)
    print("Fixed NaN in per-topic aggregate")

ast.parse(src)
P.write_text(src, encoding="utf-8")
print("Syntax OK")