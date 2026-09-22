"""
Second-person hints keyed on misconception_id.

These are used when the diagnosis has fired and the tutor knows exactly
what went wrong. The hint speaks to the learner, about the maths, not
about the learner.

Levels:
    H1  - conceptual hint, names the concept
    H2  - strategic hint, suggests the operation
    H3  - micro-step, one concrete move

Salt-checked. All second person. All rooted in the specific error.
"""

HINTS = {
    "M_SIGN_ERROR_FACTORISATION": {
        "H1": "One of your roots has the wrong sign. Look at each factor — what value of x makes it zero?",
        "H2": "For a factor like (x + 5), the root is the value that makes the whole bracket zero. Try setting it equal to zero and solving.",
        "H3": "Set x + 5 = 0. That gives x = -5, not x = +5.",
    },
    "M_FACTORISATION_INCOMPLETE": {
        "H1": "You wrote the factors. What is the next step once you have them?",
        "H2": "When a product equals zero, each factor can equal zero on its own.",
        "H3": "Set each factor equal to zero on its own line: first (x - 2) = 0, then (x - 3) = 0.",
    },
    "M_TP_COORD_CONFUSION": {
        "H1": "Which coordinate of the turning point sets the range — the x or the y?",
        "H2": "The range describes the y-values, so you need the y-coordinate of the turning point.",
        "H3": "If the turning point is at (h; k), the range starts at y = k.",
    },
    "M_REDUCTION_SIGN": {
        "H1": "Which quadrant does this angle sit in? Check the sign before simplifying.",
        "H2": "Use the CAST diagram. In the second quadrant, only sin is positive.",
        "H3": "For sin(180 - x): 180 - x is in the second quadrant, and sin is positive there. So sin(180 - x) = sin x.",
    },
    "M_DIAGRAM_ASSUMPTION": {
        "H1": "You used a property of the diagram. Was it given, or did you assume it?",
        "H2": "In a proof, only given information can be used. Anything else must be proved.",
        "H3": "Write the given first. Then show each step and cite the theorem or reason.",
    },
    "M_MISSING_THEOREM_CITATION": {
        "H1": "You reached the correct statement. Where is the reason?",
        "H2": "Every statement in a Euclidean proof needs a reason in brackets.",
        "H3": "Write the theorem's name next to each statement, e.g. (angle in semicircle).",
    },
    "M_ASYMPTOTE_CONFUSION": {
        "H1": "Which asymptote is horizontal and which is vertical?",
        "H2": "The vertical asymptote comes from the denominator of the fraction.",
        "H3": "Set the denominator equal to zero to find the vertical asymptote; the constant added is the horizontal one.",
    },
    "M_IDENTITY_MISAPPLY": {
        "H1": "Which Pythagorean identity applies here — sin²+cos²=1?",
        "H2": "Write the identity on its own line first, then substitute.",
        "H3": "sin²x + cos²x = 1. Rearrange if needed, then substitute.",
    },
    "M_CHAIN_RULE_DROP": {
        "H1": "You differentiated the outer part. What about the inside?",
        "H2": "The chain rule: derivative of the outer times derivative of the inner.",
        "H3": "For (2x + 1)³: outer derivative 3(2x + 1)² times inner derivative 2, giving 6(2x + 1)².",
    },
    "M_GP_COMMON_RATIO": {
        "H1": "Which formula did you use — arithmetic or geometric?",
        "H2": "For a GP the term is a·r^(n-1), not a + (n-1)d.",
        "H3": "Set the exponent to (n - 1), not n. So T_n = a·r^(n-1).",
    },
    "M_BOXPLOT_IQR": {
        "H1": "Which quartiles did you use for the IQR?",
        "H2": "IQR is Q3 minus Q1, not the range.",
        "H3": "Subtract the lower quartile from the upper quartile: Q3 - Q1.",
    },
    "M_SIMILARITY_RATIO": {
        "H1": "Which direction is the ratio — big to small, or small to big?",
        "H2": "The ratio uses corresponding sides. Match the vertices first.",
        "H3": "Write the ratio as (image side) : (object side), then solve for the unknown.",
    },
}


def get_hint(misconception_id, hint_level):
    """Return the second-person hint for a misconception at a level, or None."""
    entry = HINTS.get(misconception_id)
    if not entry:
        return None
    return entry.get(hint_level)
