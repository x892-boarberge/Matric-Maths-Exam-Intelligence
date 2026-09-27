"""
Drill engine — practice mode (v2, holistic rewrite).

Anchor → attempt → grade → save attempt → sibling on fail → loop → mastery.

Works identically for every topic. No answer leaks. No note spam.
"""
from __future__ import annotations

import random
import uuid
from typing import Optional

from .schemas import Problem, WorkingSubmission, WorkingStep
from . import analogue_library
from .template_router import route_template
from .presentation_matcher import check_presentation, format_note
from .math_grader import grade, diagnose_wrong, MatchKind
from .diagnosis import diagnose


SITTING_SIZE = 5
PASS_THRESHOLD = 4


# ============================================================
# Pool helpers
# ============================================================
def _load_pool(template_id: str):
    return analogue_library.POOL.get(template_id, [])


def _extract_expected(analogue: dict) -> str:
    steps = analogue.get("steps", [])
    if not steps:
        return ""
    last = str(steps[-1])
    if ":" in last:
        last = last.split(":", 1)[1]
    return last.strip()


def _analogue_to_problem(analogue: dict, template_id: str, skill_id: str) -> Problem:
    return Problem(
        problem_id=f"drill_{template_id}_{uuid.uuid4().hex[:6]}",
        skill_id=skill_id,
        topic="",
        subtopic="",
        structure_type="routine_calculation",
        prompt=analogue["problem"],
        expected_answer=_extract_expected(analogue),
        topic_v2=None,
    )


# ============================================================
# Working input
# ============================================================
def _collect_working(q_num: int, total: int):
    steps = []
    print()
    print(f"  Question {q_num} of {total}")
    print("  Show your working. 'done' to submit, 'help' for a worked example,")
    print("  'next' to skip this question, 'end' to finish this sitting,")
    print("  'menu' to pick a different topic, 'q' to quit the tutor.")
    print()
    while True:
        idx = len(steps) + 1
        try:
            raw = input(f"    Line {idx}: ").rstrip()
        except (EOFError, KeyboardInterrupt):
            return None
        s = raw.strip()
        if not s:
            continue
        low = s.lower()
        # Free will: the learner controls the pace
        if low in ("q", "quit", "exit"):
            return None
        if low in ("next", "skip", "n"):
            return "NEXT"
        if low in ("menu", "topics", "back", "topics:"):
            return "MENU"
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
            )
        if low.startswith("answer:"):
            ans = s[len("answer:"):].strip()
            if ans:
                return WorkingSubmission(
                    steps=[WorkingStep(index=1, raw_text=ans)],
                    source="typed",
                    final_answer=ans,
                )
        steps.append(s)


# ============================================================
# Sibling example — same template, different variant
# ============================================================
def _show_sibling(pool, shown_keys):
    candidates = [a for a in pool if analogue_library.analogue_key(a) not in shown_keys]
    if not candidates:
        candidates = pool
    if not candidates:
        return None
    ex = random.choice(candidates)
    print()
    print("  Let's look at a similar one first.")
    print()
    print(f"    Problem: {ex['problem']}")
    for s in ex.get("steps", []):
        print(f"      {s}")
    if ex.get("note"):
        print(f"    Note: {ex['note']}")
    shown_keys.add(analogue_library.analogue_key(ex))
    return ex


# ============================================================
# Warm diagnosis message
# ============================================================
def _speak_diagnosis(kind: str):
    if kind == "sign_flip":
        print()
        print("  I see the shape of the working. The sign on one root looks")
        print("  flipped — the number is right, the sign isn't. Worth a look.")
    elif kind == "partial":
        print()
        print("  One of the roots is right. The other is missing or different.")
        print("  Both matter for this question.")
    else:
        print()
        print("  There's something off. Let's look at a similar one together.")


# ============================================================
# Record attempt into the store (correct AND wrong)
# ============================================================
def _save_attempt(store, session_id, learner_id, skill_id,
                  response, rule_id, error_type,
                  misconception_id=None, hint_level=None):
    try:
        store.save_attempt(
            session_id=session_id,
            learner_id=learner_id,
            skill_id=skill_id,
            response=response[:500],
            diagnosis_rule_id=rule_id or "",
            misconception_id=misconception_id,
            hint_level=hint_level,
            error_type=error_type,
        )
    except Exception:
        pass


# ============================================================
# Mastery summary (warm, non-blocking)
# ============================================================
def _speak_mastery(skill_id, template_id, questions_correct, total_questions,
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
    print("  line by line, in their format.")


# ============================================================
# Main drill
# ============================================================
def run(engine, store, learner_id, session_id, anchor, logger=None,
        interactive_input=True, sitting_number=1):
    template_id = route_template(anchor.skill_id, anchor.prompt)
    if template_id is None:
        print(f"  (No template for skill {anchor.skill_id} — skipping.)")
        return {"sittings_passed": 0, "correct": 0, "total": 0, "exit_reason": "no_template"}

    pool = _load_pool(template_id)
    if not pool:
        print(f"  (No variants for {template_id} — skipping.)")
        return {"sittings_passed": 0, "correct": 0, "total": 0, "exit_reason": "empty_pool"}

    topic_label = anchor.topic or anchor.skill_id.split(".")[0]

    print()
    print("=" * 60)
    print(f"  Drill: {anchor.skill_id}")
    if sitting_number > 1:
        print(f"  Sitting {sitting_number}")
    print(f"  Template: {template_id}  ({len(pool)} variants)")
    print("=" * 60)

    # ---- Build question sequence: anchor first, then variations ----
    sequence = []
    anchor_ok = bool(anchor.expected_answer and anchor.expected_answer.strip())
    if anchor_ok:
        sequence.append({"type": "anchor", "problem": anchor})

    cycle = pool.copy()
    random.shuffle(cycle)
    cycle_idx = 0
    shown_variant_keys = set()

    while len(sequence) < SITTING_SIZE:
        if cycle_idx >= len(cycle):
            cycle_idx = 0
            random.shuffle(cycle)
        analogue = cycle[cycle_idx]
        cycle_idx += 1
        key = analogue_library.analogue_key(analogue)
        if key in shown_variant_keys:
            continue
        shown_variant_keys.add(key)
        sequence.append({
            "type": "variation",
            "problem": _analogue_to_problem(analogue, template_id, anchor.skill_id),
        })

    # ---- Drill loop ----
    questions_correct = 0
    questions_first_try = 0
    questions_skipped = 0
    questions_attempted = 0
    total_attempts = 0
    shown_note_ids = set()
    shown_sibling_keys = set()

    for i, item in enumerate(sequence, 1):
        drill_problem = item["problem"]

        print()
        print("-" * 60)
        print(f"  Problem: {drill_problem.prompt}")
        if item["type"] == "anchor":
            print("  (This is the original question you picked.)")
        print("-" * 60)

        attempts_on_this_q = 0
        while True:
            if not interactive_input:
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": total_attempts, "exit_reason": "non_interactive"}

            submission = _collect_working(i, SITTING_SIZE)

            if submission is None:
                _close_early(questions_correct, i - 1)
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": total_attempts, "exit_reason": "quit"}

            if submission == "MENU":
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
                        "exit_reason": "learner_end"}

            if submission == "NEXT":
                # Learner chose to move on — that is their right.
                questions_skipped += 1
                questions_attempted += 1
                print()
                print("  Moving on. You can come back to this pattern any time.")
                break  # exit the attempt loop, advance to next question

            if submission == "HELP" or submission == "MORE":
                # Show a worked example from the same template, then retry
                _show_sibling(pool, shown_sibling_keys)
                print()
                print("  Try the question again when ready — or type 'next' to move on.")
                continue

            attempts_on_this_q += 1
            total_attempts += 1
            learner_text = submission.joined()

            result = grade(learner_text, drill_problem.expected_answer)

            # ---- MATCH ----
            if result.kind == MatchKind.MATCH:
                questions_correct += 1
                questions_attempted += 1
                if attempts_on_this_q == 1:
                    questions_first_try += 1

                _save_attempt(store, session_id, learner_id, anchor.skill_id,
                              learner_text, f"D_{result.matcher}", "none")

                print()
                print(f"  ✓ Correct.  ({questions_correct}/{i} this sitting)")

                # One NEW presentation note per question (dedup)
                try:
                    notes = check_presentation(
                        [s.raw_text for s in submission.steps],
                        topic=anchor.topic_v2, max_notes=5,
                    )
                    for n in notes:
                        if n.rule_id in shown_note_ids:
                            continue
                        shown_note_ids.add(n.rule_id)
                        print(format_note(n))
                        break
                except Exception:
                    pass
                break

            # ---- UNCERTAIN — sibling then retry (NO ANSWER REVEAL) ----
            if result.kind == MatchKind.UNCERTAIN:
                print()
                print("  I want to be sure this is the shape the memo expects.")
                _show_sibling(pool, shown_sibling_keys)
                print()
                print("  Try the same question again — or type 'next' to move on.")
                continue

            # ---- NO_MATCH — diagnose warmly, sibling, retry ----
            kind = diagnose_wrong(learner_text, drill_problem.expected_answer)

            # Get N08 diagnosis for accurate misconception id
            misconception_id = None
            try:
                diag = diagnose(anchor.skill_id, learner_text,
                                drill_problem.expected_answer)
                if diag and diag.misconception_id:
                    misconception_id = diag.misconception_id
            except Exception:
                pass

            _save_attempt(store, session_id, learner_id, anchor.skill_id,
                          learner_text, "D_NO_MATCH",
                          (kind or "unknown"), misconception_id)

            _speak_diagnosis(kind or "unknown")
            if misconception_id:
                print(f"  Noticed: {misconception_id}")

            # One NEW presentation note (dedup)
            try:
                notes = check_presentation(
                    [s.raw_text for s in submission.steps],
                    topic=anchor.topic_v2, max_notes=5,
                )
                for n in notes:
                    if n.rule_id in shown_note_ids:
                        continue
                    shown_note_ids.add(n.rule_id)
                    print(format_note(n))
                    break
            except Exception:
                pass

            _show_sibling(pool, shown_sibling_keys)
            print()
            print("  Try the question again — or type 'next' to move on.")

    # ---- Sitting complete ----
    passed = questions_correct >= PASS_THRESHOLD
    _speak_mastery(anchor.skill_id, template_id,
                   questions_correct, SITTING_SIZE, topic_label,
                   questions_skipped=questions_skipped)

    _try_recompute_mastery(store, learner_id, anchor.skill_id)

    # Show mastery state — honest
    try:
        m = store.get_mastery(learner_id, anchor.skill_id)
        print(f"  Mastery: {m['mastery_state']}  |  Sittings passed: {m['sittings_passed']}")
    except Exception:
        pass

    # ---- Another sitting? ----
    if interactive_input:
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
                    "sitting_number": sitting_number}

    return {
        "sittings_passed": 1 if passed else 0,
        "correct": questions_correct,
        "total": SITTING_SIZE,
        "first_try": questions_first_try,
        "attempts": total_attempts,
        "exit_reason": "completed",
        "template_id": template_id,
        "sitting_number": sitting_number,
    }


def _try_recompute_mastery(store, learner_id, skill_id):
    try:
        store.recompute_mastery(learner_id, skill_id)
    except Exception:
        pass


def _close_early(questions_correct, questions_attempted):
    print()
    print("=" * 60)
    print(f"  Session closed.  {questions_correct}/{questions_attempted} correct.")
    print("  Progress saved.")
    print("=" * 60)