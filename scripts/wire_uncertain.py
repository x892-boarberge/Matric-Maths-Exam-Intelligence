"""Wire UNCERTAIN → ask learner in drill.py."""
from pathlib import Path
import ast

P = Path("src/tutor/drill.py")
src = P.read_text(encoding="utf-8-sig")

# Import MatchKind
old_import = "from .math_grader import equivalent, diagnose_wrong"
new_import = "from .math_grader import equivalent, diagnose_wrong, grade, MatchKind"
if old_import in src and "MatchKind" not in src.split("from .math_grader import")[1][:100]:
    src = src.replace(old_import, new_import, 1)
    print("Added MatchKind import")
else:
    print("Import already present or anchor missing")

# Replace the "equivalent()" call with a proper grade() call
old = '''            # ---- Practice grader (math equivalence, not format) ----
            if equivalent(learner_text, drill_problem.expected_answer):
                correct_count += 1
                print()
                print(f"  ✓ Correct.  ({correct_count} correct this drill)")
                break

            # ---- Wrong — diagnose warmly, show sibling, retry ----
            kind = diagnose_wrong(learner_text, drill_problem.expected_answer)
            _speak_diagnosis(kind or "unknown", None)'''

new = '''            # ---- Practice grader (math equivalence, not format) ----
            result = grade(learner_text, drill_problem.expected_answer)

            if result.kind == MatchKind.MATCH:
                correct_count += 1
                print()
                print(f"  ✓ Correct.  ({correct_count} correct this drill)")
                break

            if result.kind == MatchKind.UNCERTAIN:
                # Do not mark wrong — ask the learner to confirm
                print()
                print("  I want to make sure I read your answer correctly.")
                print(f"    You wrote: {learner_text[:100]}")
                print(f"    I think you mean: {drill_problem.expected_answer[:100]}")
                confirm = input("  Is that what you meant? [Y/n/skip]: ").strip().lower()
                if confirm in ("", "y", "yes"):
                    correct_count += 1
                    print()
                    print(f"  ✓ Correct.  ({correct_count} correct this drill)")
                    break
                if confirm in ("s", "skip"):
                    print()
                    print("  Let's move on.")
                    break
                # else fall through to "wrong" path
                print()
                print("  Let's try again.")

            # ---- Wrong — diagnose warmly, show sibling, retry ----
            kind = diagnose_wrong(learner_text, drill_problem.expected_answer)
            _speak_diagnosis(kind or "unknown", None)'''

if old in src:
    src = src.replace(old, new, 1)
    print("Wired UNCERTAIN → ask learner")
else:
    print("WARN: grader block anchor not found")
    idx = src.find("# ---- Practice grader")
    if idx > 0:
        print(repr(src[idx:idx+600]))

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)