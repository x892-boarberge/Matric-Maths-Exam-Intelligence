"""
Drill engine — practice mode (v2, holistic rewrite).

Anchor → attempt → grade → save attempt → sibling on fail → loop → mastery.

Works identically for every topic. No answer leaks. No note spam.
"""
from __future__ import annotations

import json
import random
import uuid
from typing import Optional

from .schemas import Problem, WorkingSubmission, WorkingStep
from . import analogue_library
from .template_router import route_template
from .presentation_matcher import check_presentation, format_note
from .math_grader import grade, diagnose_wrong, MatchKind
from .step_grader import grade_steps as grade_steps_fn, grade_steps_inline
from .step_schemes import build_scheme
from .diagnosis import diagnose


SITTING_SIZE = 5
PASS_THRESHOLD = 4


# ============================================================
# Pool helpers
# ============================================================
def _template_path_for_anchor(problem_id: str):
    """Map an anchor problem_id to its DBE template JSON path."""
    from pathlib import Path as _P
    _root = _P(__file__).resolve().parents[2]
    tdir = _root / "data" / "processed" / "tutor" / "question_templates"
    parts = str(problem_id).split("_")
    if len(parts) < 3:
        return None
    year, paper = parts[0], parts[1]
    qpart = parts[2].split(".")[0]  # 'Q1.1.1' -> 'Q1'
    p = tdir / f"template_{year}_{paper}_{qpart}.json"
    return p if p.exists() else None


def _anchor_template_metadata(problem_id: str):
    """Return the template dict for an anchor problem_id, or None."""
    tp = _template_path_for_anchor(problem_id)
    if not tp:
        return None
    try:
        import json as _json
        return _json.loads(tp.read_text(encoding="utf-8"))
    except Exception:
        return None


def _try_get_anchor_diagram_image(problem_id: str):
    """Return the parent paper's page-image path for this anchor,
    if the template carries one. Falls through to the rendered spec
    (see _try_render_anchor_diagram) if the page image is missing."""
    t = _anchor_template_metadata(problem_id)
    if not t:
        return None
    img = t.get("diagram_image")
    if not img:
        return None
    from pathlib import Path as _P
    root = _P(__file__).resolve().parents[2]
    p = root / img
    return str(p) if p.exists() else None


def _try_render_anchor_diagram(problem_id: str):
    """If the template for this anchor carries a diagram spec,
    render it to a per-anchor PNG and return the path. Otherwise
    fall back to the parent paper's page image if present."""
    t = _anchor_template_metadata(problem_id)
    if not t:
        return None
    d = t.get("diagram")
    s = t.get("diagram_spec")

    # Preferred: parent paper page image (exact replica of the real DBE diagram)
    page = _try_get_anchor_diagram_image(problem_id)
    if page:
        return page

    # Fallback: render from spec (approximate reconstruction)
    if d and s:
        try:
            from pathlib import Path as _P
            from tutor import diagram_dispatcher as _disp
            root = _P(__file__).resolve().parents[2]
            cache = root / "data" / "processed" / "diagrams" / "drill_cache"
            cache.mkdir(parents=True, exist_ok=True)
            safe = str(problem_id).replace(".", "_").replace("/", "_")
            out = cache / f"{safe}.png"
            _disp.render_diagram(d, out_path=out, **s)
            return str(out)
        except Exception:
            pass
    return None



_SKILL_DIAGRAM_INDEX = None


def _load_skill_diagram_index():
    global _SKILL_DIAGRAM_INDEX
    if _SKILL_DIAGRAM_INDEX is None:
        import json as _json
        from pathlib import Path as _P
        root = _P(__file__).resolve().parents[2]
        p = root / "data" / "processed" / "tutor" / "skill_diagram_index.json"
        _SKILL_DIAGRAM_INDEX = (
            _json.loads(p.read_text(encoding="utf-8"))
            if p.exists() else {}
        )
    return _SKILL_DIAGRAM_INDEX


def _reference_diagram_for_skill(skill_id: str):
    """Return a parent page image path for a variant of this skill.
    Uses the skill → diagram index; returns the first page image whose
    template carries a diagram for this skill. Returns None if no
    skill-matching image exists."""
    index = _load_skill_diagram_index()
    entries = index.get(skill_id, [])
    if not entries:
        return None
    from pathlib import Path as _P
    root = _P(__file__).resolve().parents[2]
    for e in entries:
        img = e.get("image")
        if not img:
            continue
        p = root / img
        if p.exists():
            return str(p)
    return None


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
    expected = _extract_expected(analogue)
    scheme = build_scheme(template_id, analogue, expected)
    return Problem(
        problem_id=f"drill_{template_id}_{uuid.uuid4().hex[:6]}",
        skill_id=skill_id,
        topic="",
        subtopic="",
        structure_type="routine_calculation",
        prompt=analogue["problem"],
        expected_answer=expected,
        topic_v2=None,
        step_scheme=scheme,
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

# ============================================================
# Step-level feedback (Phase 5e)
# ============================================================

import re as _re


def _corpus_id_to_memo_id(problem_id: str) -> str:
    """2023_P1_Q1_1.1.1 -> 2023_P1_Q1.1.1 (drop underscore + repeated digit)."""
    if not problem_id or problem_id.startswith("drill_"):
        return ""
    # Q<n>_<n>. -> Q<n>.
    return _re.sub(r"Q(\d+)_\1\.", r"Q\1.", problem_id)


def _step_feedback(problem_id: str, learner_lines: list[str]) -> dict | None:
    """Return step-grader result for the anchor, or None if not applicable."""
    memo_id = _corpus_id_to_memo_id(problem_id)
    if not memo_id:
        return None
    try:
        r = grade_steps_fn(memo_id, learner_lines)
    except Exception:
        return None
    if r["total_marks"] == 0:
        return None
    return r


def _print_step_feedback(result: dict) -> None:
    """Format the step result for the CLI, with help for missing steps."""
    awarded = result["awarded_marks"]
    total = result["total_marks"]
    steps = result["steps"]

    missing = [s for s in steps if s.get("match_status") == "NOT_MATCHED"]
    uncertain = [s for s in steps if s.get("match_status") == "UNCERTAIN"]

    if not missing and not uncertain:
        print(f"  Full method shown — memo awards {total}/{total}.")
        return

    print(f"  Memo would award {awarded}/{total}.")
    for s in missing:
        mark_word = "mark" if s["marks"] == 1 else "marks"
        print(f"    You skipped: {s['desc']}  ({s['marks']} {mark_word})")
        # Show what the memo wanted, from the FIRST acceptable form
        forms = s.get("forms") or []
        if forms:
            print(f"      The memo would show:   {forms[0]}")
    for u in uncertain:
        print(f"    Cannot verify: {u['desc']}")
    print("    (In the exam, markers award marks per step.)")


# ============================================================
# Auto-outcome measurement
# ============================================================

def _close_open_interventions(store, learner_id, skill_id, step_result,
                               current_qid, session_id):
    """For every open intervention on this learner+skill, record whether the
    learner now shows what was being taught.

    Called on MATCH. The outcome is:
      - improved   : the step that was taught is now MATCHED
                     (or, if no step can be checked, the answer matched)
      - unchanged  : the step is still NOT_MATCHED
      - (skip)     : the step is UNCERTAIN, or we can't determine

    This is the piece that makes the loop turn by itself. Every time a
    learner does well, the tutor learns something about its own teaching.
    """
    try:
        open_invs = store.interventions.list_open(learner_id, skill_id)
    except Exception:
        return
    if not open_invs:
        return

    # Build a lookup: step_index -> match_status from the current attempt
    step_status = {}
    if step_result is not None:
        for s in step_result.get("steps", []):
            step_status[int(s.get("index", -1))] = s.get("match_status")

    for inv in open_invs:
        try:
            ctx = json.loads(inv.get("context") or "{}")
        except Exception:
            ctx = {}
        step_index = ctx.get("step_index")

        if step_index is not None and int(step_index) in step_status:
            status = step_status[int(step_index)]
            if status == "MATCHED":
                result = "improved"
            elif status == "NOT_MATCHED":
                result = "unchanged"
            else:
                continue  # UNCERTAIN — cannot judge, leave open
            evidence = {
                "measured_via": "step_grader",
                "step_index": int(step_index),
                "current_qid": current_qid,
                "session_id": session_id,
            }
        else:
            # No step to check — fall back to overall answer match.
            result = "improved"
            evidence = {
                "measured_via": "answer_match",
                "current_qid": current_qid,
                "session_id": session_id,
            }

        try:
            store.interventions.record_outcome(
                intervention_id=inv["intervention_id"],
                learner_id=learner_id,
                result=result,
                measurement_kind="follow_up",
                evidence=evidence,
            )
        except Exception:
            pass  # never break the drill

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
        if item["type"] == "anchor":
            _diag = _try_render_anchor_diagram(drill_problem.problem_id)
            if _diag:
                print(f"  Diagram: {_diag}")
                print()
        else:
            # Variation — try to show a reference diagram from another
            # DBE question that uses the same skill.
            _ref = _reference_diagram_for_skill(drill_problem.skill_id)
            if _ref:
                print(f"  Reference diagram: {_ref}")
                print("  (Same shape, different numbers.)")
                print()
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

                # ---- Phase 5e: step-level feedback ----
                # Try anchor (CSV lookup) first, fall back to inline scheme (variants)
                learner_lines_for_steps = [s.raw_text for s in submission.steps]
                step_result = _step_feedback(
                    drill_problem.problem_id,
                    learner_lines_for_steps,
                )
                if step_result is None and getattr(drill_problem, "step_scheme", None):
                    try:
                        step_result = grade_steps_inline(
                            drill_problem.step_scheme,
                            learner_lines_for_steps,
                        )
                    except Exception:
                        step_result = None
                if step_result is not None:
                    _print_step_feedback(step_result)


                    # Log interventions for each missing step shown to the learner.
                    # When the learner later does this skill again, we check
                    # whether they showed the step -- that is the outcome.
                    try:
                        missing = [
                            s for s in step_result.get("steps", [])
                            if s.get("match_status") == "NOT_MATCHED"
                        ]
                        for m in missing:
                            store.interventions.log(
                                learner_id=learner_id,
                                skill_id=anchor.skill_id,
                                action_type="memo_line_shown",
                                action_desc="Showed memo version of missed step: " + m["desc"],
                                question_id=drill_problem.problem_id,
                                session_id=session_id,
                                context={"step_index": m["index"],
                                         "step_desc": m["desc"]},
                            )
                    except Exception:
                        pass  # never break the drill


                    # Auto-close prior interventions on this skill. If we taught
                    # something last time and the learner now shows it, we learn
                    # that our teaching worked. If they still don't, we learn
                    # that it didn't. Either way, the loop turns itself.
                    _close_open_interventions(
                        store, learner_id, anchor.skill_id, step_result,
                        drill_problem.problem_id, session_id,
                    )

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

            # Phase 5e: if diagnosis could not explain, record a discovery.
            # This is the beginning of the Tutor Learning Engine — the tutor
            # notices what its rules cannot explain, preserves the evidence,
            # and lets recurrence strengthen the pattern over time.
            try:
                if (kind or "unknown") == "unknown":
                    store.discoveries.record(
                        learner_id=learner_id,
                        skill_id=anchor.skill_id,
                        question_id=drill_problem.problem_id,
                        learner_lines=[s.raw_text for s in submission.steps],
                        expected_answer=drill_problem.expected_answer,
                        session_id=session_id,
                    )
            except Exception:
                pass  # discovery logging must never break the drill

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