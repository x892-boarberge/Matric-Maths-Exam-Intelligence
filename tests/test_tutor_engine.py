import sys
import pathlib
import pytest
from .event_log import SessionLogger
from .schemas import EventType

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.tutor.schemas import (
    LearnerState,
    Problem,
    HintLevel,
    ActionType,
    ProvenanceKind,
    MasteryState,
)
from src.tutor.tutor_engine import TutorEngine
from src.tutor.hint_policy import is_escalation_allowed


def state(skill_id="trig.reduction.simplify"):
    return LearnerState(learner_id="L1", skill_id=skill_id, current_session_id="S1")


def problem(skill_id, expected, st="routine_calculation"):
    return Problem(
        problem_id="P1",
        skill_id=skill_id,
        topic="T",
        subtopic="ST",
        structure_type=st,
        prompt="...",
        expected_answer=expected,
    )


def test_r1_no_worked_solution_on_first_attempt():
    eng = TutorEngine()
    a = eng.step(state(), problem("trig.reduction.simplify", "sin theta"), "-sin theta")
    assert a.hint_level != HintLevel.H4
    assert a.action != ActionType.OFFER_WORKED_STEP


def test_r2_diagnosis_always_produced():
    eng = TutorEngine()
    a = eng.step(state(), problem("trig.reduction.simplify", "sin theta"), "-sin theta")
    assert a.diagnosis is not None and a.diagnosis.rule_id


def test_r3_single_intervention_pattern():
    eng = TutorEngine()
    a = eng.step(state(), problem("trig.reduction.simplify", "sin theta"), "-sin theta")
    assert isinstance(a.intervention.intervention_pattern, str)
    assert ";" not in a.intervention.intervention_pattern


def test_r5_hint_escalation_gradual():
    eng = TutorEngine()
    s = state()
    p = problem("trig.reduction.simplify", "sin theta")
    prev = None
    for _ in range(5):
        a = eng.step(s, p, "-sin theta")
        if prev is not None and a.hint_level is not None:
            assert is_escalation_allowed(prev, a.hint_level)
        prev = a.hint_level


def test_r7_no_mastery_from_single_correct():
    eng = TutorEngine()
    s = state()
    eng.step(s, problem("trig.reduction.simplify", "sin theta"), "sin theta")
    assert s.mastery_state != MasteryState.MASTERED


def test_r8_mastery_needs_multiple_correct():
    eng = TutorEngine()
    s = state()
    p = problem("trig.reduction.simplify", "sin theta")
    for _ in range(3):
        eng.step(s, p, "sin theta")
    assert s.mastery_state == MasteryState.MASTERED


def test_r9_escalation_to_human_after_repeated_failure():
    eng = TutorEngine()
    s = state()
    p = problem("trig.reduction.simplify", "sin theta")
    last = None
    for _ in range(6):
        last = eng.step(s, p, "-sin theta")
    assert last.action == ActionType.FLAG_FOR_HUMAN


def test_r10_provenance_always_set():
    eng = TutorEngine()
    a = eng.step(state(), problem("trig.reduction.simplify", "sin theta"), "-sin theta")
    assert a.intervention.provenance in (
        ProvenanceKind.N08_BACKED,
        ProvenanceKind.GENERIC_FALLBACK,
    )


@pytest.mark.parametrize(
    "skill_id,response,expected,misconception",
    [
        (
            "algebra.quadratic.solve",
            "x = 2 or x = -3",
            "x = 2 or x = 3",
            "M_SIGN_ERROR_FACTORISATION",
        ),
        (
            "functions.parabola.range",
            "y >= -1",
            "y >= -4",
            "M_TP_COORD_CONFUSION",
        ),
        (
            "trig.reduction.simplify",
            "-sin theta",
            "sin theta",
            "M_REDUCTION_SIGN",
        ),
        (
            "analytical_geom.parallelogram.prove",
            "AB parallel CD as seen in the diagram, BC parallel AD as seen in the diagram.",
            "AB parallel CD and BC parallel AD (proved by equal gradients)",
            "M_DIAGRAM_ASSUMPTION",
        ),
        (
            "euclidean.semicircle.prove",
            "Angle ABC = 90 because it's in a semicircle.",
            "angle ABC = 90 (angle in semicircle theorem)",
            "M_MISSING_THEOREM_CITATION",
        ),
    ],
)
def test_five_case_diagnosis(skill_id, response, expected, misconception):
    eng = TutorEngine()
    s = state(skill_id)
    p = problem(skill_id, expected, st="proof_show_that")
    a = eng.step(s, p, response)
    assert a.diagnosis.misconception_id == misconception
    assert a.intervention.provenance == ProvenanceKind.N08_BACKED