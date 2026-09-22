"""
Analogue library.

When a learner has failed the same skill six times, the tutor does not
give up. It shows a simpler worked problem of the same type, then
invites the learner to try the original again with the analogue in front
of them.

Each entry is a small worked example. Short. Safe. Correct. The aim is
to demonstrate the mechanism, not to solve the learner's exact question.

Public:
    get_analogue(skill_id) -> dict or None
    has_analogue(skill_id) -> bool
    all_skills() -> list
"""


ANALOGUES = {
    "algebra.quadratic.solve": {
        "problem": "Solve (x + 2)(x - 3) = 0",
        "steps": [
            "When a product is zero, at least one factor is zero.",
            "Set each factor to zero on its own line:",
            "x + 2 = 0  gives  x = -2",
            "x - 3 = 0  gives  x = 3",
            "Answer:  x = -2  or  x = 3",
        ],
        "note": "Check the sign in each factor. The sign inside the bracket is not the root.",
    },
    "functions.parabola.range": {
        "problem": "A parabola opens upward with turning point at (2; 5). State its range.",
        "steps": [
            "Opens upward, so the turning point is the lowest point.",
            "The range starts at the y-value of the turning point.",
            "y-value is 5, so the range is y >= 5.",
        ],
        "note": "Remember: the range depends on the y-coordinate of the turning point, not the x.",
    },
    "trig.reduction.simplify": {
        "problem": "Simplify sin(180 - x)",
        "steps": [
            "180 - x lies in the second quadrant.",
            "In the second quadrant, sin is positive.",
            "sin(180 - x) = sin x",
        ],
        "note": "Use the CAST diagram. Identify the quadrant first, then the sign.",
    },
    "analytical_geom.parallelogram.prove": {
        "problem": "Show that A(0; 0), B(2; 2), C(4; 0), D(2; -2) form a parallelogram.",
        "steps": [
            "A quadrilateral is a parallelogram if both pairs of opposite sides are parallel.",
            "m_AB = (2 - 0) / (2 - 0) = 1",
            "m_DC = (0 - (-2)) / (4 - 2) = 1",
            "So AB is parallel to DC.",
            "Similarly m_BC = -1 and m_AD = -1, so BC is parallel to AD.",
            "Answer: ABCD is a parallelogram (both pairs of opposite sides parallel).",
        ],
        "note": "Write the coordinates of each point. Compare gradients of opposite sides.",
    },
    "euclidean.semicircle.prove": {
        "problem": "In a circle, AB is a diameter and C is on the circle. Prove angle ACB = 90.",
        "steps": [
            "Given: AB is a diameter of the circle.",
            "C lies on the circle.",
            "Theorem: the angle in a semicircle is a right angle.",
            "Therefore angle ACB = 90.",
        ],
        "note": "Name the theorem in your reason. Do not just write the conclusion.",
    },
    "functions.hyperbola.asymptotes": {
        "problem": "Write down the domain of g(x) = 1 / (x - 2).",
        "steps": [
            "The denominator cannot be zero.",
            "x - 2 = 0 gives x = 2.",
            "So x = 2 is excluded from the domain.",
            "Answer: x is an element of R, x is not equal to 2.",
        ],
        "note": "Remember: the vertical asymptote is the value that makes the denominator zero.",
    },
    "trig.identity.simplify": {
        "problem": "Simplify sin x . cos x + sin x . cos x",
        "steps": [
            "The two terms are identical, so combine them.",
            "2 sin x cos x",
            "Using the double-angle identity, that is sin 2x.",
            "Answer: sin 2x",
        ],
        "note": "Look for repeated products first, then match to a standard identity.",
    },
    "calculus.chain_rule": {
        "problem": "Differentiate g(x) = (3x + 1)^2.",
        "steps": [
            "Outer function: (something)^2. Derivative is 2(something).",
            "Inner function: 3x + 1. Derivative is 3.",
            "Multiply: g'(x) = 2(3x + 1) * 3 = 6(3x + 1).",
        ],
        "note": "Remember the chain rule: outer derivative times inner derivative. Do not forget the inner.",
    },
    "sequences.gp.term": {
        "problem": "A geometric sequence has first term 5 and constant ratio 2. Find T4.",
        "steps": [
            "Formula: T_n = a * r^(n - 1)",
            "a = 5, r = 2, n = 4",
            "T_4 = 5 * 2^3 = 5 * 8 = 40",
        ],
        "note": "Remember: the exponent is (n - 1), not n. Off by one is the common error.",
    },
    "statistics.boxplot.iqr": {
        "problem": "A box plot has Q1 = 6 and Q3 = 14. Find the IQR.",
        "steps": [
            "IQR = Q3 - Q1",
            "IQR = 14 - 6 = 8",
        ],
        "note": "Remember: IQR is Q3 minus Q1, not the range (max minus min).",
    },
    "euclidean.similarity.ratio": {
        "problem": "Triangle ABC has sides AB = 3, BC = 4, AC = 5. Triangle PQR is similar and corresponds with A -> P. If PQ = 6, find QR.",
        "steps": [
            "The sides are in the same ratio.",
            "Scale factor: PQ / AB = 6 / 3 = 2",
            "QR = BC * 2 = 4 * 2 = 8",
        ],
        "note": "Remember: match the corresponding vertices first, then set up the ratio.",
    },
}


def get_analogue(skill_id):
    """Return the analogue for a skill, or None if unavailable."""
    return ANALOGUES.get(skill_id)


def has_analogue(skill_id):
    return skill_id in ANALOGUES


def all_skills():
    return sorted(ANALOGUES.keys())
