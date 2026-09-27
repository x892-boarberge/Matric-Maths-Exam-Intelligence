"""Add free will: skip, end-sitting, more-help. Graceful, not authoritarian."""
from pathlib import Path
import ast

P = Path("src/tutor/drill.py")
src = P.read_text(encoding="utf-8-sig")

# ---- 1. Extend _collect_working with free-will commands ----
old = '''        low = s.lower()
        if low in ("q", "quit", "exit"):
            return None
        if low in ("help", "answer", "hint"):
            return "HELP"
        if low in ("done", "submit"):
            if not steps:
                print("    (type at least one line, 'help', or 'q' to quit)")
                continue
            return WorkingSubmission(
                steps=[WorkingStep(index=i + 1, raw_text=t) for i, t in enumerate(steps)],
                source="typed",
                final_answer=steps[-1],
            )'''

new = '''        low = s.lower()
        # Free will: the learner controls the pace
        if low in ("q", "quit", "exit"):
            return None
        if low in ("next", "skip", "n"):
            return "NEXT"
        if low in ("end", "stop", "enough"):
            return "END"
        if low in ("help", "answer", "hint"):
            return "HELP"
        if low in ("more", "another"):
            return "MORE"
        if low in ("done", "submit"):
            if not steps:
                print("    (type at least one line, 'help', or 'q' to quit)")
                continue
            return WorkingSubmission(
                steps=[WorkingStep(index=i + 1, raw_text=t) for i, t in enumerate(steps)],
                source="typed",
                final_answer=steps[-1],
            )'''

if old in src:
    src = src.replace(old, new, 1)
    print("Added free-will commands: next / end / more")
else:
    print("WARN: collector anchor not found")

# ---- 2. Update the prompt line to show the options ----
old2 = '''    print("  Show your working. Type 'done' when finished, 'help', or 'q' to quit.")'''
new2 = '''    print("  Show your working. 'done' to submit, 'help' for a worked example,")
    print("  'next' to move on, 'end' to finish the sitting, 'q' to quit.")'''

if old2 in src:
    src = src.replace(old2, new2, 1)
    print("Updated prompt with options")
else:
    print("WARN: prompt anchor not found")

# ---- 3. Handle NEXT / END / MORE in the main attempt loop ----
old3 = '''            if submission is None:
                _close_early(questions_correct, i - 1)
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": total_attempts, "exit_reason": "quit"}

            if submission == "HELP":
                # Learner asked for help — show sibling, do NOT save attempt
                _show_sibling(pool, shown_sibling_keys)
                print()
                print("  Try the question again when ready.")
                continue'''

new3 = '''            if submission is None:
                _close_early(questions_correct, i - 1)
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": total_attempts, "exit_reason": "quit"}

            if submission == "END":
                print()
                print("  Good. Free will beats force. Ending the sitting here.")
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": total_attempts, "exit_reason": "learner_end"}

            if submission == "NEXT":
                # Learner chose to move on — count it as attempted, not correct
                print()
                print("  Moving on to the next question. You can come back to this")
                print("  pattern any time. That's what practice is for.")
                break  # exit the attempt loop, advance to next question

            if submission == "HELP" or submission == "MORE":
                # Show a worked example from the same template, then retry
                _show_sibling(pool, shown_sibling_keys)
                print()
                print("  Try the question again when ready — or type 'next' to move on.")
                continue'''

if old3 in src:
    src = src.replace(old3, new3, 1)
    print("Wired free-will handling in attempt loop")
else:
    print("WARN: loop anchor not found — checking snippet")

# ---- 4. On NO_MATCH — offer an explicit free-will exit ----
old4 = '''            _show_sibling(pool, shown_sibling_keys)
            print()
            print("  Try the question again when ready.")'''

new4 = '''            _show_sibling(pool, shown_sibling_keys)
            print()
            print("  Try the question again — or type 'next' to move on.")'''

if old4 in src:
    src = src.replace(old4, new4, 1)
    print("Updated retry prompt")

# ---- 5. On UNCERTAIN — offer free will too ----
old5 = '''                print()
                print("  I want to be sure this is the shape the memo expects.")
                _show_sibling(pool, shown_sibling_keys)
                print()
                print("  Try the same question again when ready.")
                continue'''

new5 = '''                print()
                print("  I want to be sure this is the shape the memo expects.")
                _show_sibling(pool, shown_sibling_keys)
                print()
                print("  Try the same question again — or type 'next' to move on.")
                continue'''

if old5 in src:
    src = src.replace(old5, new5, 1)
    print("Updated UNCERTAIN prompt")

# ---- 6. Q1 anchor should NOT be forced (already is fine, but let's note it) ----
# No change needed — the anchor is Q1, learner can type 'next' to skip it

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)