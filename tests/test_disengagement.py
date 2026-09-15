import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.tutor.disengagement import DisengagementKind, detect_disengagement
from src.tutor.schemas import LearnerState, Problem
from src.tutor.tutor_engine import TutorEngine


def test_answer_demand_detected():
    r = detect_disengagement("just give me the answer")
    assert r.kind == DisengagementKind.ANSWER_DEMAND


def test_frustrated_detected():
    r = detect_disengagement("I don't understand this")
    assert r.kind == DisengagementKind.FRUSTRATED


def test_engine_does_not_dump_solution_on_answer_demand():
    engine = TutorEngine()
    problem = Problem(
        problem_id="t1",
        skill_id="algebra.quadratic.solve",
        topic="Algebra & Equations",
        subtopic="Quadratic equations",
        structure_type="routine_calculation",
        prompt="Solve x^2 - 5x + 6 = 0",
        expected_answer="x = 2 or x = 3",
    )
    state = LearnerState(learner_id="t", skill_id=problem.skill_id)
    action = engine.step(state, problem, "just give me the answer", explicit_solution_request=True)
    msg = action.tutor_message.lower()
    assert "x = 2" not in msg
    assert "full solution" in msg or "won't give" in msg or "one useful step" in msg