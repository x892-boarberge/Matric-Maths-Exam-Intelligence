import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.tutor.schemas import LearnerState, Problem
from src.tutor.tutor_engine import TutorEngine


CASES = [
    dict(
        skill_id="algebra.quadratic.solve",
        topic="Algebra & Equations",
        subtopic="Quadratic equations",
        structure_type="routine_calculation",
        prompt="Solve x^2 - 5x + 6 = 0",
        expected="x = 2 or x = 3",
        response="x = 2 or x = -3",
    ),
    dict(
        skill_id="functions.parabola.range",
        topic="Functions & Graphs",
        subtopic="Parabola",
        structure_type="graph_interpretation",
        prompt="Parabola opens upward with turning point (-1, -4). State the range.",
        expected="y >= -4",
        response="y >= -1",
    ),
    dict(
        skill_id="trig.reduction.simplify",
        topic="Trigonometry",
        subtopic="Reduction formulae",
        structure_type="routine_calculation",
        prompt="Simplify sin(180 - theta)",
        expected="sin theta",
        response="-sin theta",
    ),
    dict(
        skill_id="analytical_geom.parallelogram.prove",
        topic="Analytical Geometry",
        subtopic="Parallelogram proof",
        structure_type="proof_show_that",
        prompt="Prove ABCD is a parallelogram.",
        expected="AB parallel CD and BC parallel AD (proved by equal gradients)",
        response="AB parallel CD as seen in the diagram, BC parallel AD as seen in the diagram.",
    ),
    dict(
        skill_id="euclidean.semicircle.prove",
        topic="Euclidean Geometry",
        subtopic="Angle in semicircle",
        structure_type="proof_show_that",
        prompt="Prove angle ABC = 90 where AC is a diameter.",
        expected="angle ABC = 90 (angle in semicircle theorem)",
        response="Angle ABC = 90 because it's in a semicircle.",
    ),
]


def main():
    engine = TutorEngine()
    line = "=" * 78
    print(line)
    for i, c in enumerate(CASES, 1):
        problem = Problem(
            problem_id=f"P{i}",
            skill_id=c["skill_id"],
            topic=c["topic"],
            subtopic=c["subtopic"],
            structure_type=c["structure_type"],
            prompt=c["prompt"],
            expected_answer=c["expected"],
        )
        state = LearnerState(
            learner_id=f"L{i}",
            skill_id=c["skill_id"],
            current_session_id=f"S{i}",
        )
        action = engine.step(state, problem, c["response"])

        print(f"\nCase {i}: {c['topic']} / {c['subtopic']}")
        print(f"  Response:      {c['response']}")
        print(
            f"  Diagnosis:     {action.diagnosis.error_type.value:14s} "
            f"[{action.diagnosis.misconception_id or '-'}] "
            f"rule={action.diagnosis.rule_id}"
        )
        print(
            f"  Intervention:  {action.intervention.intervention_pattern:28s} "
            f"[{action.intervention.provenance.value}] "
            f"n08={action.intervention.n08_intervention_id}"
        )
        print(f"  Hint level:    {action.hint_level.value if action.hint_level else '-'}")
        print(f"  Action:        {action.action.value}")
        print(f"  Engine rule:   {action.rule_id}")
        print(f"  Tutor says:    {action.tutor_message}")
    print("\n" + line)


if __name__ == "__main__":
    main()
    