import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.tutor.diagnosis import diagnose
from src.tutor.schemas import ErrorType


CASES = [
    # Rule 1 — factorisation incomplete
    ("algebra.quadratic.solve", "(x-2)(x-3)", "x=2 or x=3", "M_FACTORISATION_INCOMPLETE"),
    ("algebra.quadratic.solve", "x=2 or x=3", "x=2 or x=3", None),
    ("algebra.quadratic.solve", "(x-2)(x-3)=0", "x=2 or x=3", "M_FACTORISATION_INCOMPLETE"),
    # Rule 2 — asymptote
    (
        "functions.hyperbola.asymptotes",
        "horizontal asymptote: x=1",
        "vertical x=1; horizontal y=2",
        "M_ASYMPTOTE_CONFUSION",
    ),
    (
        "functions.hyperbola.asymptotes",
        "vertical x=1; horizontal y=2",
        "vertical x=1; horizontal y=2",
        None,
    ),
    (
        "functions.hyperbola.asymptotes",
        "x=1, y=2",
        "vertical x=1; horizontal y=2",
        "NOT_ASYM",
    ),
    # Rule 3 — identity
    (
        "trig.identity.simplify",
        "sin^2 theta + cos^2 theta = sin^2 theta cos^2 theta",
        "1",
        "M_IDENTITY_MISAPPLY",
    ),
    ("trig.identity.simplify", "1", "1", None),
    ("trig.identity.simplify", "sin^2 + cos^2 = 1", "1", "NOT_ID"),
    # Rule 4 — chain rule
    ("calculus.chain_rule", "3(2x+1)^2", "6(2x+1)^2", "M_CHAIN_RULE_DROP"),
    ("calculus.chain_rule", "6(2x+1)^2", "6(2x+1)^2", None),
    ("calculus.chain_rule", "3*(2x+1)^2*2", "6(2x+1)^2", "NOT_CHAIN"),
    # Rule 5 — GP
    ("sequences.gp.term", "2 * 3^n", "2 * 3^(n-1)", "M_GP_COMMON_RATIO"),
    ("sequences.gp.term", "2 * 3^(n-1)", "2 * 3^(n-1)", None),
    ("sequences.gp.term", "2*3**(n-1)", "2 * 3^(n-1)", None),
    # Rule 6 — boxplot (range=18, IQR=7)
    ("statistics.boxplot.iqr", "18", "{2, 5, 8, 12, 20} IQR = 7", "M_BOXPLOT_IQR"),
    ("statistics.boxplot.iqr", "7", "{2, 5, 8, 12, 20} IQR = 7", None),
    (
        "statistics.boxplot.iqr",
        "Q3 - Q1 = 12 - 5 = 7",
        "{2, 5, 8, 12, 20} IQR = 7",
        "NOT_IQR",
    ),
    # Rule 7 — similarity
    ("euclidean.similarity.ratio", "3:2", "2:3", "M_SIMILARITY_RATIO"),
    ("euclidean.similarity.ratio", "2:3", "2:3", None),
    ("euclidean.similarity.ratio", "2/3", "2:3", "NOT_SIM"),
]


def test_v1_2_cases():
    for skill, resp, exp, want in CASES:
        d = diagnose(skill, resp, exp)
        if want is None:
            assert d.error_type == ErrorType.NONE, (skill, resp, d)
        elif want == "NOT_ASYM":
            assert d.misconception_id != "M_ASYMPTOTE_CONFUSION", (skill, resp, d)
        elif want == "NOT_ID":
            assert d.misconception_id != "M_IDENTITY_MISAPPLY", (skill, resp, d)
        elif want == "NOT_CHAIN":
            assert d.misconception_id != "M_CHAIN_RULE_DROP", (skill, resp, d)
        elif want == "NOT_IQR":
            assert d.misconception_id != "M_BOXPLOT_IQR", (skill, resp, d)
        elif want == "NOT_SIM":
            assert d.misconception_id != "M_SIMILARITY_RATIO", (skill, resp, d)
        else:
            assert d.misconception_id == want, (skill, resp, d.misconception_id, d)