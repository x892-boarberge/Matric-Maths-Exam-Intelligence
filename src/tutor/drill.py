"""
Drill engine — practice mode.

Anchor → attempt → grade by math equivalence → sibling example on fail
→ infinite loop → mastery check → warm disclaimer.

Never rigid on format. Reads working, not just final line.
"""
from __future__ import annotations

import random
import uuid
from typing import Optional

from .schemas import (
    LearnerState, Problem, WorkingSubmission, WorkingStep,
)
from . import analogue_library
from .template_router import route_template
from .math_grader import equivalent, diagnose_wrong, grade, MatchKind


VARIATIONS_PER_TEMPLATE = 5
PASS_THRESHOLD = 4  # 4 of 5


# ------------------------------------------------------------------
# Pool
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# Working input
# ------------------------------------------------------------------
def _collect_working(step_number: int, total: int):
    steps = []
    print()
    print(f"  Question {step_number} of {total}")
    print("  Show your working. Type 'done' when finished, 'q' to quit.")
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
        if low in ("q", "quit", "exit"):
            return None
        if low in ("done", "submit"):
            if not steps:
                print("    (type at least one line first, or 'q' to quit)")
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


# ------------------------------------------------------------------
# Sibling example
# ------------------------------------------------------------------
def _show_sibling(pool, exclude_keys):
    candidates = [a for a in pool if analogue_library.analogue_key(a) not in exclude_keys]
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
    exclude_keys.add(analogue_library.analogue_key(ex))
    return ex


def _speak_diagnosis(kind: str, misconception_id: Optional[str]):
    """Warm, non-lecturing message about what the tutor noticed."""
    if kind == "sign_flip":
        print()
        print("  I see the shape of the working. The sign on one root looks")
        print("  flipped — the number is right, the sign isn't. Worth a look.")
    elif kind == "partial":
        print()
        print("  One of the roots is right. The other one is missing or different.")
        print("  Both matter for this question.")
    elif misconception_id:
        print()
        print(f"  Something came up: {misconception_id.replace('_', ' ').lower()}.")
    else:
        print()
        print("  There's something off. Let's look at a similar one together.")


# ------------------------------------------------------------------
# Mastery disclaimer
# ------------------------------------------------------------------
def _speak_mastery(skill_id: str, template_id: str, correct: int, total: int, topic_label: str):
    print()
    print("=" * 60)
    print(f"  Template mastered: {template_id}")
    print(f"  Result: {correct}/{total}")
    print("=" * 60)
    print()
    print(f"  You've worked through the variants of this pattern, {topic_label}.")
    print("  The method held together. That is the point of the drill.")
    print()
    print("  Disclaimer — practice is one thing, exam is another. In the exam")
    print("  you'll be marked strictly against the DBE memo. Same method, but")
    print("  line by line, in their format. Exam mode unlocks when the skill")
    print("  is fully mastered.")
    print()


# ------------------------------------------------------------------
# Main drill
# ------------------------------------------------------------------
def run(engine, store, learner_id: str, session_id: str, anchor: Problem,
        logger=None, interactive_input=True) -> dict:
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
    print(f"  Template: {template_id}  ({len(pool)} variants)")
    print(f"  Pattern:  show your working — the tutor reads the math, not the format.")
    print("=" * 60)

    cycle = pool.copy()
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
        print("-" * 60)

        # Attempt loop — infinite until correct or quit
        while True:
            if not interactive_input:
                return {"sittings_passed": 0, "correct": 0, "total": 0,
                        "exit_reason": "non_interactive"}

            submission = _collect_working(q_num, VARIATIONS_PER_TEMPLATE)
            if submission is None:
                _close_early(correct_count, total_count)
                return {"sittings_passed": 0, "correct": correct_count,
                        "total": total_count, "exit_reason": "quit"}

            total_count += 1
            learner_text = submission.joined()

            # ---- Practice grader (math equivalence, not format) ----
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
                # Learner says "that's not what I meant" — do NOT fire diagnosis.
                # Just loop back and let them retype.
                print()
                print("  No problem. Try the same question again.")
                continue

            # ---- Wrong — diagnose warmly, show sibling, retry ----
            kind = diagnose_wrong(learner_text, drill_problem.expected_answer)
            _speak_diagnosis(kind or "unknown", None)

            # Also hand to engine for N08 lookup
            state = LearnerState(
                learner_id=learner_id,
                skill_id=anchor.skill_id,
                current_session_id=session_id,
            )
            try:
                action = engine.step(state, drill_problem, submission,
                                     explicit_solution_request=False)
                if action.diagnosis.misconception_id:
                    print(f"  Noticed: {action.diagnosis.misconception_id}")
            except Exception:
                pass

            _show_sibling(pool, shown_keys)
            print()
            print("  Try the question again when you're ready.")

    # ---- Drill complete ----
    passed = correct_count >= PASS_THRESHOLD
    _speak_mastery(anchor.skill_id, template_id, correct_count, total_count, topic_label)

    # Update store
    try:
        store.recompute_mastery(learner_id, anchor.skill_id)
        m = store.get_mastery(learner_id, anchor.skill_id)
        print(f"  Mastery: {m['mastery_state']}  |  Sittings passed: {m['sittings_passed']}")
    except Exception:
        pass

    return {
        "sittings_passed": 1 if passed else 0,
        "correct": correct_count,
        "total": total_count,
        "exit_reason": "completed",
        "template_id": template_id,
    }


def _close_early(correct, total):
    print()
    print("=" * 60)
    print(f"  Session closed.  {correct}/{total} correct this drill.")
    print("  Progress saved.")
    print("=" * 60)