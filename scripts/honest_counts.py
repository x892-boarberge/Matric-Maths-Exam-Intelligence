"""Fix: honest counts, tracked skips, mastery in summary, CLI text."""
from pathlib import Path
import ast

P = Path("src/tutor/drill.py")
src = P.read_text(encoding="utf-8-sig")

# ---- 1. Track skips explicitly ----
old = '''    questions_correct = 0
    questions_first_try = 0
    total_attempts = 0
    shown_note_ids = set()
    shown_sibling_keys = set()'''

new = '''    questions_correct = 0
    questions_first_try = 0
    questions_skipped = 0
    questions_attempted = 0
    total_attempts = 0
    shown_note_ids = set()
    shown_sibling_keys = set()'''

if old in src:
    src = src.replace(old, new, 1)
    print("Added skip/attempt tracking")
else:
    print("WARN: tracker anchor not found")

# ---- 2. On NEXT, count a skip and advance honestly ----
old2 = '''            if submission == "NEXT":
                # Learner chose to move on — count it as attempted, not correct
                print()
                print("  Moving on to the next question. You can come back to this")
                print("  pattern any time. That's what practice is for.")
                break  # exit the attempt loop, advance to next question'''

new2 = '''            if submission == "NEXT":
                # Learner chose to move on — that is their right.
                questions_skipped += 1
                questions_attempted += 1
                print()
                print("  Moving on. You can come back to this pattern any time.")
                break  # exit the attempt loop, advance to next question'''

if old2 in src:
    src = src.replace(old2, new2, 1)
    print("NEXT now counts a skip")

# ---- 3. On END, count the current question as attempted but not answered ----
old3 = '''            if submission == "END":
                print()
                print("  Good. Free will beats force. Ending the sitting here.")
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": total_attempts, "exit_reason": "learner_end"}'''

new3 = '''            if submission == "END":
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

if old3 in src:
    src = src.replace(old3, new3, 1)
    print("END reports honest counts")
else:
    print("WARN: END anchor not found")

# ---- 4. On MATCH, mark attempted ----
old4 = '''            # ---- MATCH ----
            if result.kind == MatchKind.MATCH:
                questions_correct += 1
                if attempts_on_this_q == 1:
                    questions_first_try += 1'''

new4 = '''            # ---- MATCH ----
            if result.kind == MatchKind.MATCH:
                questions_correct += 1
                questions_attempted += 1
                if attempts_on_this_q == 1:
                    questions_first_try += 1'''

if old4 in src:
    src = src.replace(old4, new4, 1)
    print("MATCH now counts a question")
else:
    print("WARN: MATCH anchor not found")

# ---- 5. Sitting complete summary — honest + mastery state ----
old5 = '''    passed = questions_correct >= PASS_THRESHOLD
    _speak_mastery(anchor.skill_id, template_id,
                   questions_correct, SITTING_SIZE, topic_label)

    _try_recompute_mastery(store, learner_id, anchor.skill_id)

    # Show mastery state
    try:
        m = store.get_mastery(learner_id, anchor.skill_id)
        print(f"  Mastery: {m['mastery_state']}  |  Sittings passed: {m['sittings_passed']}")
    except Exception:
        pass'''

new5 = '''    passed = questions_correct >= PASS_THRESHOLD
    _speak_mastery(anchor.skill_id, template_id,
                   questions_correct, SITTING_SIZE, topic_label,
                   questions_skipped=questions_skipped)

    _try_recompute_mastery(store, learner_id, anchor.skill_id)

    # Show mastery state — honest
    try:
        m = store.get_mastery(learner_id, anchor.skill_id)
        print(f"  Mastery: {m['mastery_state']}  |  Sittings passed: {m['sittings_passed']}")
    except Exception:
        pass'''

if old5 in src:
    src = src.replace(old5, new5, 1)
    print("Sitting complete passes skip count to summary")
else:
    print("WARN: sitting complete anchor not found")

# ---- 6. Update _speak_mastery signature ----
old6 = '''def _speak_mastery(skill_id, template_id, questions_correct, total_questions, topic_label):
    print()
    print("=" * 60)
    print(f"  Drill complete — {template_id}")
    print(f"  Questions correct: {questions_correct}/{total_questions}")
    print("=" * 60)
    print()
    if questions_correct >= PASS_THRESHOLD:
        print(f"  You've worked through the variants of this pattern, {topic_label}.")
        print("  The method held together. That's the point of the drill.")
    else:
        print(f"  You got {questions_correct} of {total_questions}. That's close.")
        print("  One more sitting and the method will lock in.")
    print()
    print("  Disclaimer — practice is one thing, exam is another. In the exam")
    print("  you'll be marked strictly against the DBE memo. Same method, but")
    print("  line by line, in their format.")'''

new6 = '''def _speak_mastery(skill_id, template_id, questions_correct, total_questions,
                   topic_label, questions_skipped=0):
    print()
    print("=" * 60)
    print(f"  Drill complete — {template_id}")
    line = f"  Correct: {questions_correct}/{total_questions}"
    if questions_skipped:
        line += f"   (skipped: {questions_skipped})"
    print(line)
    print("=" * 60)
    print()
    if questions_correct >= PASS_THRESHOLD:
        print(f"  The method held together across the variants, {topic_label}.")
        print("  That is the point of the drill.")
    elif questions_skipped and questions_correct > 0:
        print(f"  You moved on from {questions_skipped} of them. That is your call.")
        print("  Come back to this pattern when you feel like it.")
    else:
        print(f"  You got {questions_correct} of {total_questions}. That is close.")
        print("  One more sitting and the method will lock in.")
    print()
    print("  Disclaimer — practice is one thing, exam is another. In the exam")
    print("  you'll be marked strictly against the DBE memo. Same method, but")
    print("  line by line, in their format.")'''

if old6 in src:
    src = src.replace(old6, new6, 1)
    print("Mastery summary now shows skips honestly")
else:
    print("WARN: mastery function anchor not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)