from pathlib import Path

path = Path(r"C:\Users\Administrator\Desktop\Matric-Maths-Exam-Intelligence\src\tutor\diagnosis.py")

path.write_text(r'''"""Diagnosis rules for the five demo skills. Matching uses normalised text."""

from __future__ import annotations

import re
from typing import Callable, Dict, Tuple

from .schemas import DiagnosisResult, ErrorType


def _norm(text: str) -> str:
    if text is None:
        return ""
    s = str(text).lower().strip()
    s = s.replace("θ", "theta").replace("Θ", "theta")
    s = s.replace("≥", ">=").replace("≤", "<=")
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*=\s*", "=", s)
    s = re.sub(r"\s*>\s*=\s*", ">=", s)
    s = re.sub(r"\s*<\s*=\s*", "<=", s)
    s = re.sub(r"\s*\+\s*", "+", s)
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"\s+or\s+", " or ", s)
    s = re.sub(r"\s*\(\s*", "(", s)
    s = re.sub(r"\s*\)\s*", ")", s)
    return s.strip()


def _is_correct(response: str, expected: str) -> bool:
    nr = _norm(response)
    ne = _norm(expected)
    if not nr or not ne:
        return False
    if nr == ne:
        return True
    loose_r = re.sub(r"\bor\s*x\s*=\s*", "or ", nr)
    loose_e = re.sub(r"\bor\s*x\s*=\s*", "or ", ne)
    if loose_r == loose_e:
        return True
    parts_r = [p.strip() for p in re.split(r"\bor\b", loose_r) if p.strip()]
    parts_e = [p.strip() for p in re.split(r"\bor\b", loose_e) if p.strip()]
    if len(parts_r) == 2 and len(parts_e) == 2 and set(parts_r) == set(parts_e):
        return True
    return False


def _quad_sign_flip(nr: str, expected: str) -> bool:
    n = nr.replace(" ", "")
    if "x=-3" in n:
        return True
    if re.search(r"x\s*=\s*2\s*or\s*x\s*=\s*-3", nr):
        return True
    if re.search(r"x\s*=\s*-3\s*or\s*x\s*=\s*2", nr):
        return True
    if re.search(r"x=2\s*or\s*-3", nr) or re.search(r"x=-3\s*or\s*2", nr):
        return True
    return False


def _parab_range_yp(nr: str, expected: str) -> bool:
    return bool(re.search(r"y\s*>=\s*-1\b", nr))


def _trig_red_sign(nr: str, expected: str) -> bool:
    if re.search(r"-\s*sin\s*\(?\s*theta\s*\)?", nr):
        return True
    n = nr.replace(" ", "")
    return n in ("-sintheta", "-sin(theta)")


def _ageo_diagram(nr: str, expected: str) -> bool:
    return "as seen" in nr or "from the diagram" in nr or "in the diagram" in nr


def _eucl_missing_cite(nr: str, expected: str) -> bool:
    has_90 = "90" in nr or "right angle" in nr
    has_theorem = "theorem" in nr or "semicircle" in nr or "diameter" in nr
    if has_90 and not has_theorem:
        return True
    if has_90 and "because it's in a semicircle" in nr and "theorem" not in nr:
        return True
    return False


RuleFn = Callable[[str, str], bool]

RULES: Dict[str, Tuple[str, ErrorType, str, RuleFn]] = {
    "algebra.quadratic.solve": (
        "M_SIGN_ERROR_FACTORISATION",
        ErrorType.PROCEDURAL,
        "Learner flipped the sign of a root when reading the factor.",
        _quad_sign_flip,
    ),
    "functions.parabola.range": (
        "M_TP_COORD_CONFUSION",
        ErrorType.REPRESENTATION,
        "Learner used the x-coordinate of the turning point as the range bound.",
        _parab_range_yp,
    ),
    "trig.reduction.simplify": (
        "M_REDUCTION_SIGN",
        ErrorType.CONCEPTUAL,
        "Learner applied an incorrect sign under the reduction formula.",
        _trig_red_sign,
    ),
    "analytical_geom.parallelogram.prove": (
        "M_DIAGRAM_ASSUMPTION",
        ErrorType.STRATEGY,
        "Learner assumed parallelism from the diagram without proof.",
        _ageo_diagram,
    ),
    "euclidean.semicircle.prove": (
        "M_MISSING_THEOREM_CITATION",
        ErrorType.PROCEDURAL,
        "Learner stated 90 degrees without citing the theorem.",
        _eucl_missing_cite,
    ),
}


def diagnose(skill_id: str, learner_response: str, expected_answer: str) -> DiagnosisResult:
    nr = _norm(learner_response)

    if _is_correct(learner_response, expected_answer):
        return DiagnosisResult(
            error_type=ErrorType.NONE,
            misconception_id=None,
            confidence=1.0,
            rule_id="D_CORRECT",
            explanation="Response matches expected answer after normalisation.",
        )

    rule = RULES.get(skill_id)
    if rule:
        mid, etype, expl, pred = rule
        if pred(nr, _norm(expected_answer)):
            return DiagnosisResult(
                error_type=etype,
                misconception_id=mid,
                confidence=0.85,
                rule_id=f"D_{mid}",
                explanation=expl,
            )

    return DiagnosisResult(
        error_type=ErrorType.UNKNOWN,
        misconception_id=None,
        confidence=0.3,
        rule_id="D_UNKNOWN",
        explanation="No matching correct or misconception pattern after normalisation.",
    )
''', encoding="utf-8")

print("Wrote", path, "size=", path.stat().st_size)
print(path.read_text(encoding="utf-8")[:80])
