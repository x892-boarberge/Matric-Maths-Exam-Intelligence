from pathlib import Path
import ast

P = Path("scripts/cli_tutor.py")
src = P.read_text(encoding="utf-8-sig")

fixes = [
    ("d  → drill (4 questions, mastery tracked)",
     "d  → drill (5 questions, mastery tracked)"),
    ("d  → drill (4 question, mastery tracked)",
     "d  → drill (5 questions, mastery tracked)"),
]
n = 0
for old, new in fixes:
    if old in src:
        src = src.replace(old, new, 1)
        n += 1

if n:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print(f"CLI fixed ({n} replacements)")
else:
    print("WARN: CLI text not found")