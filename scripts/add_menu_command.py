"""Add 'menu' exit door to the drill."""
from pathlib import Path
import ast

P = Path("src/tutor/drill.py")
src = P.read_text(encoding="utf-8-sig")

# 1. Recognise 'menu' / 'back' / 'topics' in the collector
old = '''        if low in ("next", "skip", "n"):
            return "NEXT"
        if low in ("end", "stop", "enough"):
            return "END"'''

new = '''        if low in ("next", "skip", "n"):
            return "NEXT"
        if low in ("menu", "topics", "back", "topics:"):
            return "MENU"
        if low in ("end", "stop", "enough"):
            return "END"'''

if old in src:
    src = src.replace(old, new, 1)
    print("Added MENU command")
else:
    print("WARN: collector anchor not found")

# 2. Handle MENU in the attempt loop — exit drill entirely
old2 = '''            if submission == "END":
                questions_attempted += 1  # counting the question we're on
                print()
                print("  Good. Free will beats force. Ending the sitting here.")
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                # Honest summary
                print()
                print(f"  This sitting: {questions_correct} correct, "
                      f"{questions_skipped} skipped, "
                      f"{questions_attempted - questions_correct - questions_skipped} left.")
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": questions_attempted,
                        "skipped": questions_skipped,
                        "exit_reason": "learner_end"}'''

new2 = '''            if submission == "MENU":
                print()
                print("  Back to the topic menu. Pick anything you like.")
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": questions_attempted,
                        "skipped": questions_skipped,
                        "exit_reason": "menu"}

            if submission == "END":
                questions_attempted += 1  # counting the question we're on
                print()
                print("  Good. Free will beats force. Ending the sitting here.")
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                print()
                print(f"  This sitting: {questions_correct} correct, "
                      f"{questions_skipped} skipped, "
                      f"{questions_attempted - questions_correct - questions_skipped} left.")
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": questions_attempted,
                        "skipped": questions_skipped,
                        "exit_reason": "learner_end"}'''

if old2 in src:
    src = src.replace(old2, new2, 1)
    print("MENU exits the drill cleanly")
else:
    print("WARN: END block anchor not found")

# 3. Update prompt to show menu
old3 = '''    print("  Show your working. 'done' to submit, 'help' for a worked example,")
    print("  'next' to move on, 'end' to finish the sitting, 'q' to quit.")'''

new3 = '''    print("  Show your working. 'done' to submit, 'help' for a worked example,")
    print("  'next' to skip this question, 'end' to finish this sitting,")
    print("  'menu' to pick a different topic, 'q' to quit the tutor.")'''

if old3 in src:
    src = src.replace(old3, new3, 1)
    print("Updated prompt with menu option")

# 4. After a passed sitting, offer menu too
old4 = '''    if passed and interactive_input:
        print()
        again = input("  Another sitting on this skill? [Y/n]: ").strip().lower()
        if again in ("", "y", "yes"):
            # Recurse with sitting_number+1
            return run(engine, store, learner_id, session_id, anchor,
                       logger=logger, interactive_input=interactive_input,
                       sitting_number=sitting_number + 1)'''

new4 = '''    if interactive_input:
        print()
        print("  Options:")
        print("    Enter / y  →  another sitting on this skill")
        print("    menu       →  pick a different topic")
        print("    q          →  quit")
        again = input("  > ").strip().lower()
        if again in ("", "y", "yes"):
            return run(engine, store, learner_id, session_id, anchor,
                       logger=logger, interactive_input=interactive_input,
                       sitting_number=sitting_number + 1)
        if again in ("menu", "m"):
            _try_recompute_mastery(store, learner_id, anchor.skill_id)
            return {"sittings_passed": 1 if passed else 0,
                    "correct": questions_correct, "total": SITTING_SIZE,
                    "exit_reason": "menu",
                    "template_id": template_id,
                    "sitting_number": sitting_number}'''

if old4 in src:
    src = src.replace(old4, new4, 1)
    print("Post-sitting menu option added")
else:
    print("WARN: post-sitting prompt anchor not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)