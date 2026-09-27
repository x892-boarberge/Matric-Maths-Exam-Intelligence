"""Wire presentation_matcher into drill.py — notes appear after the verdict."""
from pathlib import Path
import ast

P = Path("src/tutor/drill.py")
src = P.read_text(encoding="utf-8-sig")

# Import
if "from .presentation_matcher import check_presentation, format_note" not in src:
    old_imp = "from .template_router import route_template"
    new_imp = ("from .template_router import route_template\n"
               "from .presentation_matcher import check_presentation, format_note")
    if old_imp in src:
        src = src.replace(old_imp, new_imp, 1)
        print("Added presentation_matcher import")
    else:
        print("WARN: import anchor not found")

# 1. After MATCH — add presentation notes
old_match = '''            if result.kind == MatchKind.MATCH:
                correct_count += 1
                print()
                print(f"  ✓ Correct.  ({correct_count} correct this drill)")
                break'''

new_match = '''            if result.kind == MatchKind.MATCH:
                correct_count += 1
                print()
                print(f"  ✓ Correct.  ({correct_count} correct this drill)")
                # Presentation coaching — non-blocking, after the verdict
                try:
                    notes = check_presentation(
                        [s.raw_text for s in submission.steps],
                        topic=anchor.topic_v2,
                    )
                    for n in notes:
                        print(format_note(n))
                except Exception:
                    pass
                break'''

if old_match in src:
    src = src.replace(old_match, new_match, 1)
    print("Wired notes into MATCH path")
else:
    print("WARN: match anchor not found")

# 2. After a wrong answer (before sibling) — add presentation notes
old_wrong = '''            # ---- Wrong — diagnose warmly, show sibling, retry ----
            kind = diagnose_wrong(learner_text, drill_problem.expected_answer)
            _speak_diagnosis(kind or "unknown", None)'''

new_wrong = '''            # ---- Wrong — diagnose warmly, show sibling, retry ----
            kind = diagnose_wrong(learner_text, drill_problem.expected_answer)
            _speak_diagnosis(kind or "unknown", None)

            # Presentation coaching — non-blocking
            try:
                notes = check_presentation(
                    [s.raw_text for s in submission.steps],
                    topic=anchor.topic_v2,
                )
                for n in notes:
                    print(format_note(n))
            except Exception:
                pass'''

if old_wrong in src:
    src = src.replace(old_wrong, new_wrong, 1)
    print("Wired notes into WRONG path")
else:
    print("WARN: wrong anchor not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)