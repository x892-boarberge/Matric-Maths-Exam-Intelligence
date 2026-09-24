"""
CLI navigation — topic → subtopic → question.

Used by cli_tutor.py. Kept separate so a future web UI or app
front-end can reuse the same grouping logic.
"""
from typing import List, Optional

TOPIC_LABELS = {
    "ALG":  "Algebra & Equations",
    "SEQ":  "Sequences & Series",
    "FUNC": "Functions & Graphs",
    "TRIG": "Trigonometry",
    "CALC": "Calculus",
    "FIN":  "Finance",
    "PROB": "Probability",
    "STAT": "Statistics",
    "AGEO": "Analytical Geometry",
    "EUCL": "Euclidean Geometry",
}

TOPIC_ORDER = ["ALG", "SEQ", "FUNC", "TRIG", "CALC", "FIN", "PROB", "STAT", "AGEO", "EUCL"]


def _year_paper(problem) -> str:
    """Extract 'YYYY PN' from the problem_id, or '?' if not parseable."""
    parts = problem.problem_id.split("_")
    yr = parts[0] if len(parts) > 0 else "?"
    pap = parts[1] if len(parts) > 1 else "?"
    return f"{yr} {pap}"


def _short_prompt(problem, max_len: int = 66) -> str:
    p = (problem.prompt or "").replace("\n", " ").strip()
    if len(p) > max_len:
        p = p[:max_len - 3] + "..."
    return p


def _group_by_topic(problems) -> dict:
    out = {}
    for p in problems:
        key = p.topic_v2 or "UNMAPPED"
        out.setdefault(key, []).append(p)
    return out


def _group_by_subtopic(problems) -> dict:
    """Order: keep insertion order of subtopics as they appear in the corpus."""
    out = {}
    for p in problems:
        key = (p.subtopic or "").strip() or "(no subtopic)"
        out.setdefault(key, []).append(p)
    return out


def pick_topic(problems) -> Optional[str]:
    """Level 1: show topics. Return topic code, or None to quit."""
    by_topic = _group_by_topic(problems)

    # Only show topics in TOPIC_ORDER that have problems
    shown = [code for code in TOPIC_ORDER if code in by_topic]
    # Plus any unexpected codes
    for code in sorted(by_topic.keys()):
        if code not in shown and code != "UNMAPPED":
            shown.append(code)
    if "UNMAPPED" in by_topic:
        shown.append("UNMAPPED")

    print()
    print("Choose a topic")
    print("=" * 60)
    for i, code in enumerate(shown, 1):
        label = TOPIC_LABELS.get(code, code)
        n = len(by_topic[code])
        print(f"  {i:2d}. {label:<26s} {n:3d} questions")
    print("   Q. Quit")
    print("=" * 60)

    while True:
        raw = input(f"\nChoose [1-{len(shown)}, Q]: ").strip().lower()
        if raw in ("q", "quit", "exit"):
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(shown):
            return shown[int(raw) - 1]
        print(f"Enter a number between 1 and {len(shown)}, or Q.")


def pick_question(problems, topic_code: str):
    """Level 2: show questions within a topic, grouped by subtopic.

    Returns a Problem object, or None to go back.
    """
    topic_problems = [p for p in problems if (p.topic_v2 or "UNMAPPED") == topic_code]
    if not topic_problems:
        print("No problems in this topic.")
        return None

    by_sub = _group_by_subtopic(topic_problems)
    label = TOPIC_LABELS.get(topic_code, topic_code)

    # Build a flat numbered list, remembering which problem each number maps to.
    numbered = []
    for sub_name, items in by_sub.items():
        for p in items:
            numbered.append(p)

    print()
    print(f"{label}  ({len(numbered)} questions)")
    print("=" * 60)

    idx = 0
    for sub_name, items in by_sub.items():
        print(f"  {sub_name}")
        for p in items:
            idx += 1
            yp = _year_paper(p)
            print(f"    {idx:3d}. [{yp}] {_short_prompt(p)}")
        print()

    print("  B. Back   Q. Quit")
    print("=" * 60)

    while True:
        raw = input(f"\nChoose [1-{len(numbered)}, B, Q]: ").strip().lower()
        if raw in ("q", "quit", "exit"):
            return "QUIT"
        if raw in ("b", "back"):
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(numbered):
            return numbered[int(raw) - 1]
        print(f"Enter a number between 1 and {len(numbered)}, B, or Q.")


def pick_navigated_problem(problems):
    """Full navigation loop: topic → question. Returns a Problem, or None to quit."""
    if not problems:
        return None
    while True:
        topic = pick_topic(problems)
        if topic is None:
            return None
        result = pick_question(problems, topic)
        if result == "QUIT":
            return None
        if result is None:
            continue  # back to topic menu
        return result
