"""
MatricMath thin CLI tutor loop (no UI).
Engine decides; template renderer phrases; session is logged to JSONL.
"""
from __future__ import annotations

import sys
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.schemas import LearnerState, Problem, EventType
from src.tutor.tutor_engine import TutorEngine
from src.tutor.event_log import SessionLogger, read_events
from src.tutor.n08_loader import get_library
from src.tutor.mapping_adapter import v1_to_v2
from src.tutor.question_loader import load_corpus
from cli_navigation import pick_navigated_problem
from src.tutor.learner_store import open_store
from src.tutor.schemas import MasteryState


PROBLEMS = [
    {
        "skill_id": "algebra.quadratic.solve",
        "topic": "Algebra & Equations",
        "subtopic": "Quadratic equations",
        "structure_type": "routine_calculation",
        "prompt": "Solve x^2 - 5x + 6 = 0",
        "expected": "x = 2 or x = 3",
        "hint_correct": "Accept answers like: x = 2 or x = 3",
    },
    {
        "skill_id": "functions.parabola.range",
        "topic": "Functions & Graphs",
        "subtopic": "Parabola",
        "structure_type": "graph_interpretation",
        "prompt": "Parabola opens upward with turning point (-1, -4). State the range.",
        "expected": "y >= -4",
        "hint_correct": "Accept: y >= -4",
    },
    {
        "skill_id": "trig.reduction.simplify",
        "topic": "Trigonometry",
        "subtopic": "Reduction formulae",
        "structure_type": "routine_calculation",
        "prompt": "Simplify sin(180 - theta)",
        "expected": "sin theta",
        "hint_correct": "Accept: sin theta",
    },
    {
        "skill_id": "analytical_geom.parallelogram.prove",
        "topic": "Analytical Geometry",
        "subtopic": "Parallelogram proof",
        "structure_type": "proof_show_that",
        "prompt": "Prove ABCD is a parallelogram. (Do not assume from the diagram.)",
        "expected": "AB parallel CD and BC parallel AD (proved by equal gradients)",
        "hint_correct": "Need proof language, not 'as seen in the diagram'.",
    },
    {
        "skill_id": "euclidean.semicircle.prove",
        "topic": "Euclidean Geometry",
        "subtopic": "Angle in semicircle",
        "structure_type": "proof_show_that",
        "prompt": "Prove angle ABC = 90 where AC is a diameter.",
        "expected": "angle ABC = 90 (angle in semicircle theorem)",
        "hint_correct": "Need theorem citation, not only the conclusion.",
    },
]


def pick_problem():
    print("\nMatricMath CLI Tutor")
    print("=" * 60)
    lib = get_library(force_reload=True)
    print("N08 library: " + str(lib.load_status) + " | misconceptions: " + str(len(lib.by_misconception)))
    print("=" * 60)
    print("  P. Practise from real NSC corpus (choose topic)")
    for i, p in enumerate(PROBLEMS, 1):
        print("  " + str(i) + ". " + p["topic"] + " - " + p["subtopic"])
    print("  Q. Quit")
    while True:
        choice = input("\nChoose [1-5, P, Q]: ").strip().lower()
        if choice in ("q", "quit", "exit"):
            sys.exit(0)
        if choice == "p":
            return "__corpus__"
        if choice.isdigit() and 1 <= int(choice) <= len(PROBLEMS):
            return PROBLEMS[int(choice) - 1]
        print("Enter 1-5, P, or Q.")


def pick_corpus_problem():
    import random
    problems = load_corpus()
    if not problems:
        print()
        print('No corpus questions with memo answers yet.')
        print('Add rows to data/processed/memo_answers/memo_answers_YYYY_P*.csv')
        sys.exit(1)

    while True:
        sample = random.sample(problems, min(10, len(problems)))
        print()
        print('Real NSC questions (random 10 of ' + str(len(problems)) + ' loaded):')
        for i, p in enumerate(sample, 1):
            label = p.prompt[:60].replace(chr(10), ' ')
            parts = p.problem_id.split('_')
            yr = parts[0] if len(parts) > 0 else '?'
            pap = parts[1] if len(parts) > 1 else '?'
            print(f'  {i}. [{p.topic_v2}] {yr} {pap} :: {p.skill_id}')
            print('     ' + label + '...')
        print('  R. Reshuffle   Q. Quit')
        choice = input('Choose [1-10, R, Q]: ').strip().lower()
        if choice in ('q', 'quit', 'exit'):
            sys.exit(0)
        if choice == 'r':
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(sample):
            return sample[int(choice) - 1]
        print('Enter 1-10, R, or Q.')





# ------------------------------------------------------------------
# Phase 1.5 - diagram support
# ------------------------------------------------------------------

import json as _json
import os as _os

_DIAGRAM_MAP = None
_DIAGRAM_PAGES_DIR = ROOT / "data" / "processed" / "diagrams" / "pages"
_DIAGRAM_MAP_PATH = ROOT / "data" / "processed" / "diagrams" / "question_page_map.json"


def _load_diagram_map():
    global _DIAGRAM_MAP
    if _DIAGRAM_MAP is not None:
        return _DIAGRAM_MAP
    if _DIAGRAM_MAP_PATH.exists():
        try:
            _DIAGRAM_MAP = _json.loads(_DIAGRAM_MAP_PATH.read_text(encoding="utf-8"))
        except Exception:
            _DIAGRAM_MAP = {}
    else:
        _DIAGRAM_MAP = {}
    return _DIAGRAM_MAP


def _diagram_path_for(problem):
    pid = problem.problem_id or ""
    parts = pid.split("_")
    if len(parts) < 3:
        return None
    year = parts[0]
    paper = parts[1]
    q_part = parts[2]
    if not q_part.startswith("Q"):
        return None
    qnum = q_part[1:]
    stem = year + "_nov_p" + paper[1] + "_exam_maths"
    dmap = _load_diagram_map()
    if stem not in dmap:
        return None
    q_to_page = dmap[stem]
    if qnum not in q_to_page:
        return None
    page = q_to_page[qnum]
    path = _DIAGRAM_PAGES_DIR / (stem + "_p" + str(page) + ".png")
    if path.exists():
        return path
    return None


def _open_diagram(problem):
    path = _diagram_path_for(problem)
    if path is None:
        return None
    try:
        _os.startfile(str(path))
        return path
    except Exception:
        return None


def format_topic_line(problem):
    if problem.topic and problem.topic_v2 and problem.topic != problem.topic_v2:
        topic_display = str(problem.topic) + " (" + str(problem.topic_v2) + ")"
    else:
        topic_display = str(problem.topic or problem.topic_v2 or "")
    if problem.subtopic:
        topic_display = topic_display + " / " + str(problem.subtopic)
    return "Topic: " + topic_display


def main() -> None:
    item = pick_problem()

    if item == "__corpus__":
        problem = pick_navigated_problem(load_corpus())
        if problem is None:
            sys.exit(0)
        item = {
            "skill_id": problem.skill_id,
            "topic": problem.topic,
            "subtopic": problem.subtopic,
            "structure_type": problem.structure_type,
            "prompt": problem.prompt,
            "expected": problem.expected_answer,
            "hint_correct": "Answer as you would in the exam.",
            "_preloaded_problem": problem,
        }

    # Ask for a learner id so the session can be persisted.
    learner_id = input("\nEnter learner id (or press Enter for 'cli_user'): ").strip()
    if not learner_id:
        learner_id = "cli_user"

    # Open the persistent learner store.
    store_path = ROOT / "data" / "learner_store" / "learners.db"
    store = open_store(store_path)
    store.load_learner(learner_id)
    print("Learner:", learner_id, "| store:", store_path)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_id = "cli_" + stamp
    # Register this session against the learner
    store.start_session(learner_id, item["skill_id"])
    log_dir = ROOT / "data" / "processed" / "tutor" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / (session_id + ".jsonl")

    logger = SessionLogger(session_id, log_path)
    logger.emit(
        EventType.SESSION_STARTED,
        {"mode": "cli", "skill_id": item["skill_id"]},
    )

    problem = item.get("_preloaded_problem") or Problem(
        problem_id="CLI1",
        skill_id=item["skill_id"],
        topic=item["topic"],
        topic_v2=v1_to_v2(item["topic"]),
        subtopic=item["subtopic"],
        structure_type=item["structure_type"],
        prompt=item["prompt"],
        expected_answer=item["expected"],
    )

    state = LearnerState(
        learner_id=learner_id,
        skill_id=item["skill_id"],
        current_session_id=session_id,
    )

    engine = TutorEngine(session_logger=logger, learner_store=store, session_id=session_id)

    logger.emit(
        EventType.PROBLEM_PRESENTED,
        {
            "problem_id": problem.problem_id,
            "skill_id": problem.skill_id,
            "topic": problem.topic,
            "topic_v2": problem.topic_v2,
            "prompt": problem.prompt,
        },
    )

    print("\n" + "-" * 60)
    print(format_topic_line(problem))
    print("Problem: " + problem.prompt)

    _diagram = _diagram_path_for(problem)
    if _diagram is not None:
        print("Diagram page: " + str(_diagram))
        _opened = _open_diagram(problem)
        if _opened is not None:
            print("(opened in your image viewer - type \"diagram\" to reopen)")
        else:
            print("(open the image manually to see the diagram)")
    print("-" * 60)
    print("Commands:  quit  |  answer  (ask for more help)  |  just type your attempt")
    print("Note: " + item["hint_correct"])
    print("-" * 60)

    while True:
        raw = input("\nYour answer: ").strip()
        if not raw:
            print("Type an attempt, or 'quit'.")
            continue
        low = raw.lower()
        if low in ("q", "quit", "exit"):
            break
        if low in ("diagram", "d"):
            _p = _open_diagram(problem)
            if _p is not None:
                print("(reopened: " + str(_p) + ")")
            else:
                print("(no diagram page for this question)")
            continue

        explicit = low in (
            "answer",
            "just give me the answer",
            "give me the answer",
            "solution",
            "solve it",
        )

        action = engine.step(
            state,
            problem,
            raw,
            explicit_solution_request=explicit,
        )

        print("\n  diagnosis:    " + action.diagnosis.error_type.value, end="")
        if action.diagnosis.misconception_id:
            print(" [" + action.diagnosis.misconception_id + "]", end="")
        print()
        print(
            "  intervention: " + action.intervention.intervention_pattern
            + " [" + action.intervention.provenance.value + "] "
            + str(action.intervention.n08_intervention_id or "")
        )
        print("  hint level:   " + (action.hint_level.value if action.hint_level else "-"))
        print("  action:       " + action.action.value)
        print("  tutor:        " + action.tutor_message)

        if action.diagnosis.error_type.value == "none":
            print("\nCorrect for this demo item. Session can end, or keep practising.")
            more = input("Another attempt on same problem? [y/N]: ").strip().lower()
            if more != "y":
                break

        # The session never ends because the learner is struggling.
        # Only quit or correct answer ends it.

    summary = logger.close()

    # Close the store session and print mastery.
    store.end_session(session_id)
    try:
        m = store.get_mastery(learner_id, item["skill_id"])
        print("\n" + "=" * 60)
        print("Mastery for", item["skill_id"] + ":", m["mastery_state"])
        print("Sittings passed:", m["sittings_passed"])
    except Exception:
        pass
    store.close()

    print("\n" + "=" * 60)
    print("Session log: " + str(log_path))
    print("SESSION_ENDED: " + str(summary))
    print("Events: " + str(len(read_events(log_path))))
    print("=" * 60)


if __name__ == "__main__":
    main()
