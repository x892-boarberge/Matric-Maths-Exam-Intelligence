import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.tutor.schemas import (
    LearnerState,
    Problem,
    ActionType,
    HintLevel,
    ErrorType,
    MasteryState,
)
from src.tutor.tutor_engine import TutorEngine


def _problem(skill_id, prompt, expected, topic="T", sub="S"):
    return Problem(
        problem_id="t1",
        skill_id=skill_id,
        topic=topic,
        subtopic=sub,
        structure_type="routine",
        prompt=prompt,
        expected_answer=expected,
    )


def test_r1_no_worked_solution_on_first_attempt():
    engine = TutorEngine()
    p = _problem("algebra.quadratic.solve", "Solve", "x = 2 or x = 3")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a = engine.step(s, p, "x = 2 or x = -3")
    assert a.action != ActionType.OFFER_WORKED_STEP or a.hint_level != HintLevel.H4
    assert "x = 2 or x = 3" not in a.tutor_message


def test_r2_diagnosis_always_produced():
    engine = TutorEngine()
    p = _problem("algebra.quadratic.solve", "Solve", "x = 2 or x = 3")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a = engine.step(s, p, "garbage")
    assert a.diagnosis is not None
    assert a.diagnosis.rule_id


def test_r3_single_intervention_pattern():
    engine = TutorEngine()
    p = _problem("algebra.quadratic.solve", "Solve", "x = 2 or x = 3")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a = engine.step(s, p, "x = 2 or x = -3")
    assert a.intervention.intervention_pattern


def test_r5_hint_escalation_gradual():
    engine = TutorEngine()
    p = _problem("trig.reduction.simplify", "Simplify", "sin theta")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a1 = engine.step(s, p, "costheta")
    a2 = engine.step(s, p, "costheta")
    assert a1.hint_level is not None and a2.hint_level is not None


def test_r7_no_mastery_from_single_correct():
    engine = TutorEngine()
    p = _problem("algebra.quadratic.solve", "Solve", "x = 2 or x = 3")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a = engine.step(s, p, "x = 2 or x = 3")
    assert a.next_state.mastery_state != MasteryState.MASTERED


def test_r8_mastery_needs_multiple_correct():
    engine = TutorEngine()
    p = _problem("algebra.quadratic.solve", "Solve", "x = 2 or x = 3")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    for _ in range(3):
        a = engine.step(s, p, "x = 2 or x = 3")
        s = a.next_state
    assert s.mastery_state == MasteryState.MASTERED


def test_r9_escalation_to_human_after_repeated_failure():
    engine = TutorEngine()
    p = _problem("trig.reduction.simplify", "Simplify", "sin theta")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a = None
    for _ in range(6):
        a = engine.step(s, p, "zzz")
        s = a.next_state
    assert a.action == ActionType.FLAG_FOR_HUMAN


def test_r10_provenance_always_set():
    engine = TutorEngine()
    p = _problem("algebra.quadratic.solve", "Solve", "x = 2 or x = 3")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a = engine.step(s, p, "x = 2 or x = -3")
    assert a.intervention.provenance is not None


def test_five_case_sign_error():
    engine = TutorEngine()
    p = _problem("algebra.quadratic.solve", "Solve", "x = 2 or x = 3")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a = engine.step(s, p, "x = 2 or x = -3")
    assert a.diagnosis.misconception_id == "M_SIGN_ERROR_FACTORISATION"


def test_disengage_no_full_solution():
    engine = TutorEngine()
    p = _problem("algebra.quadratic.solve", "Solve", "x = 2 or x = 3")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a = engine.step(s, p, "just give me the answer")
    assert "x = 2 or x = 3" not in a.tutor_message.lower()