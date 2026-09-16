import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.tutor.schemas import LearnerState, Problem
from src.tutor.tutor_engine import TutorEngine

CASES = [
    ("algebra.quadratic.solve", "Algebra", "Quadratic", "(x-2)(x-3)", "x=2 or x=3"),
    (
        "functions.hyperbola.asymptotes",
        "Functions",
        "Asymptotes",
        "horizontal asymptote: x=1",
        "vertical x=1; horizontal y=2",
    ),
    (
        "trig.identity.simplify",
        "Trig",
        "Identity",
        "sin^2 theta + cos^2 theta = sin^2 theta cos^2 theta",
        "1",
    ),
    ("calculus.chain_rule", "Calculus", "Chain", "3(2x+1)^2", "6(2x+1)^2"),
    ("sequences.gp.term", "Sequences", "GP", "2 * 3^n", "2 * 3^(n-1)"),
    ("statistics.boxplot.iqr", "Stats", "IQR", "18", "{2, 5, 8, 12, 20} IQR = 7"),
    ("euclidean.similarity.ratio", "Euclidean", "Similarity", "3:2", "2:3"),
]


def main():
    engine = TutorEngine()
    for i, (skill, topic, sub, resp, exp) in enumerate(CASES, 1):
        p = Problem(f"V12-{i}", skill, topic, sub, "demo", f"Demo {sub}", exp)
        s = LearnerState("L", skill)
        a = engine.step(s, p, resp)
        print(
            f"{i}. {skill:32s} mid={str(a.diagnosis.misconception_id):28s} "
            f"prov={a.intervention.provenance.value:16s} n08={a.intervention.n08_intervention_id}"
        )


if __name__ == "__main__":
    main()