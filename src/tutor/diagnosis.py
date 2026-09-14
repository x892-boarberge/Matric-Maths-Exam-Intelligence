import re
from .schemas import DiagnosisResult, ErrorType


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _has_sign_flip_in_factorisation(response: str, expected: str) -> bool:
    exp = set(re.findall(r"x\s*=\s*(-?\d+)", _norm(expected)))
    got = set(re.findall(r"x\s*=\s*(-?\d+)", _norm(response)))
    return bool(exp and got and exp != got)


def _confused_turning_point_y(response: str, expected: str) -> bool:
    exp = re.findall(r"y\s*[≥>=]+\s*(-?\d+)", _norm(expected))
    got = re.findall(r"y\s*[≥>=]+\s*(-?\d+)", _norm(response))
    return bool(exp and got and exp != got)


def _reduction_sign_error(response: str, expected: str) -> bool:
    r, e = _norm(response), _norm(expected)
    return ("-sin" in r) and ("sin" in e) and (r != e)


def _assumption_from_diagram(response: str, expected: str) -> bool:
    triggers = [
        "as seen in the diagram",
        "from the diagram",
        "clearly",
        "obviously",
        "by inspection",
    ]
    r = _norm(response)
    return any(t in r for t in triggers)


def _missing_theorem_citation(response: str, expected: str) -> bool:
    theorem_terms = [
        "angle in semicircle",
        "angle at centre",
        "subten",
        "theorem",
        "equal chord",
        "pythagoras",
    ]
    r = _norm(response)
    conclusion_present = ("90" in r or "right angle" in r)
    theorem_cited = any(t in r for t in theorem_terms)
    return conclusion_present and not theorem_cited


RULES = {
    "algebra.quadratic.solve": [
        {
            "rule_id": "D_QUAD_SIGN_FLIP",
            "predicate": _has_sign_flip_in_factorisation,
            "error_type": ErrorType.PROCEDURAL,
            "misconception_id": "M_SIGN_ERROR_FACTORISATION",
            "explanation": "Learner flipped the sign of a root when reading the factor.",
        },
    ],
    "functions.parabola.range": [
        {
            "rule_id": "D_PARAB_RANGE_YP",
            "predicate": _confused_turning_point_y,
            "error_type": ErrorType.REPRESENTATION,
            "misconception_id": "M_TP_COORD_CONFUSION",
            "explanation": "Learner used the x-coordinate of the turning point as the y-bound.",
        },
    ],
    "trig.reduction.simplify": [
        {
            "rule_id": "D_TRIG_RED_SIGN",
            "predicate": _reduction_sign_error,
            "error_type": ErrorType.CONCEPTUAL,
            "misconception_id": "M_REDUCTION_SIGN",
            "explanation": "Learner applied the wrong sign from the reduction identity.",
        },
    ],
    "analytical_geom.parallelogram.prove": [
        {
            "rule_id": "D_AGEO_UNSUPPORTED_ASSUMPTION",
            "predicate": _assumption_from_diagram,
            "error_type": ErrorType.STRATEGY,
            "misconception_id": "M_DIAGRAM_ASSUMPTION",
            "explanation": "Learner assumed a property from the diagram without proving it.",
        },
    ],
    "euclidean.semicircle.prove": [
        {
            "rule_id": "D_EUCL_MISSING_JUSTIFICATION",
            "predicate": _missing_theorem_citation,
            "error_type": ErrorType.PROCEDURAL,
            "misconception_id": "M_MISSING_THEOREM_CITATION",
            "explanation": "Learner stated the correct conclusion without citing the theorem.",
        },
    ],
}


def diagnose(skill_id: str, response: str, expected: str) -> DiagnosisResult:
    if _norm(response) == _norm(expected):
        return DiagnosisResult(
            error_type=ErrorType.NONE,
            misconception_id=None,
            confidence=1.0,
            rule_id="D_CORRECT",
            explanation="Response matches expected answer.",
        )

    for rule in RULES.get(skill_id, []):
        try:
            if rule["predicate"](response, expected):
                return DiagnosisResult(
                    error_type=rule["error_type"],
                    misconception_id=rule["misconception_id"],
                    confidence=0.8,
                    rule_id=rule["rule_id"],
                    explanation=rule["explanation"],
                )
        except Exception:
            continue

    return DiagnosisResult(
        error_type=ErrorType.UNKNOWN,
        misconception_id=None,
        confidence=0.0,
        rule_id="D_UNMATCHED",
        explanation="No diagnosis rule matched. Escalating for review.",
    )