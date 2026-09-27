"""Cap presentation notes: 1 on correct, 2 on wrong."""
from pathlib import Path
import ast

P = Path("src/tutor/drill.py")
src = P.read_text(encoding="utf-8-sig")

# In MATCH path
old_match = '''                try:
                    notes = check_presentation(
                        [s.raw_text for s in submission.steps],
                        topic=anchor.topic_v2,
                    )
                    for n in notes:
                        print(format_note(n))
                except Exception:
                    pass
                break'''

new_match = '''                try:
                    notes = check_presentation(
                        [s.raw_text for s in submission.steps],
                        topic=anchor.topic_v2,
                        max_notes=1,
                    )
                    for n in notes:
                        print(format_note(n))
                except Exception:
                    pass
                break'''

if old_match in src:
    src = src.replace(old_match, new_match, 1)
    print("Capped MATCH notes at 1")

# In WRONG path
old_wrong = '''            try:
                notes = check_presentation(
                    [s.raw_text for s in submission.steps],
                    topic=anchor.topic_v2,
                )
                for n in notes:
                    print(format_note(n))
            except Exception:
                pass'''

new_wrong = '''            try:
                notes = check_presentation(
                    [s.raw_text for s in submission.steps],
                    topic=anchor.topic_v2,
                    max_notes=2,
                )
                for n in notes:
                    print(format_note(n))
            except Exception:
                pass'''

if old_wrong in src:
    src = src.replace(old_wrong, new_wrong, 1)
    print("Kept WRONG notes at 2")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)