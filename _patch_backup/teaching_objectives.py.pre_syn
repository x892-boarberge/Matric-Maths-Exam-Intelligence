"""
Teaching objectives runtime.

Each objective is sourced from a DBE recommendation. It is not a hint
and it is not a quote shown to the learner. It is a short lesson
Tanaka delivers at the point of need, tests with a probe, and then
hands the original problem back.

Public:
    find_for(misconception_id) -> dict | None
    teach(objective)           -> dict   (interactive; returns outcome)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[2]
OBJ_DIR = ROOT / "data" / "processed" / "tutor" / "teaching_objectives"

_CACHE: Optional[dict] = None


def _load_all() -> dict:
    """Return {misconception_id: objective_dict}, cached."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    out = {}
    if not OBJ_DIR.exists():
        _CACHE = out
        return out
    for p in sorted(OBJ_DIR.glob("*.json")):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        mid = obj.get("trigger_misconception")
        if mid:
            out[mid] = obj
    _CACHE = out
    return out


def _norm_id(mid):
    """Normalise a misconception id by stripping the topic prefix.

    N08 library uses ids like M_TRIG_REDUCTION_SIGN. Hand rules use
    M_REDUCTION_SIGN. Both name the same error. Normalising lets
    find_for() resolve either spelling to the same objective.
    """
    if not isinstance(mid, str):
        return mid
    for prefix in ("M_TRIG_", "M_ALG_", "M_FUNC_", "M_CALC_",
                   "M_STAT_", "M_SEQ_", "M_PROB_", "M_FIN_",
                   "M_AGEO_", "M_EUCL_", "M_INEQ_"):
        if mid.startswith(prefix):
            return "M_" + mid[len(prefix):]
    return mid


def find_for(misconception_id: str) -> Optional[dict]:
    """Return the objective that teaches this misconception, or None.

    Tries the exact id first, then the topic-stripped version, so
    M_TRIG_REDUCTION_SIGN and M_REDUCTION_SIGN both resolve.
    """
    if not misconception_id:
        return None
    cache = _load_all()
    obj = cache.get(misconception_id)
    if obj is not None:
        return obj
    normalised = _norm_id(misconception_id)
    if normalised != misconception_id:
        return cache.get(normalised)
    return None


def teach(objective: dict, *, probe_reader=None) -> dict:
    """
    Deliver the lesson, ask the probe, return the outcome.

    probe_reader: optional callable(prompt) -> str, for tests and web.
                  If None, uses input().

    Returns:
        {"objective_id": ..., "probe_attempt": str,
         "probe_correct": bool, "completed": True}
    """
    if probe_reader is None:
        probe_reader = input

    lesson = objective.get("lesson") or {}
    print()
    print("=" * 60)
    print("  Tanaka: let me show you something first.")
    print("=" * 60)
    print()
    if lesson.get("concept"):
        print(f"  {lesson['concept']}")
        print()
    if lesson.get("why"):
        print(f"  Why it matters: {lesson['why']}")
        print()
    ex = lesson.get("example") or {}
    if ex.get("problem"):
        print(f"  Example:  {ex['problem']}")
        for line in ex.get("work", []):
            print(f"            {line}")
        print()

    probe = lesson.get("probe") or {}
    outcome = {
        "objective_id": objective.get("objective_id"),
        "probe_attempt": "",
        "probe_correct": False,
        "completed": True,
    }
    if probe.get("problem"):
        print(f"  Your turn:  {probe['problem']}")
        if probe.get("hint"):
            print(f"  Hint:       {probe['hint']}")
        print()
        try:
            answer = probe_reader("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            answer = ""
        outcome["probe_attempt"] = answer

        from .math_grader import grade
        if answer:
            result = grade(answer, probe.get("expected", ""))
            outcome["probe_correct"] = result.kind.value == "match"
        print()
        if outcome["probe_correct"]:
            print("  ✓ Yes. Now go back and try your original question again.")
        else:
            print(f"  Close. The expected form is: {probe.get('expected','')}")
            print("  Try your original question again anyway.")
    print()
    return outcome
