"""Diagnosis rules — v1.1 base + v1.2 additive rules. Matching uses normalised text."""

from __future__ import annotations

import re
from pathlib import Path
from .answer_matcher import is_correct as _graceful_is_correct
from typing import Callable, Dict, List, Tuple

from .schemas import DiagnosisResult, ErrorType


def _norm(text: str) -> str:
    if text is None:
        return ""
    s = str(text).lower().strip()
    s = s.replace("θ", "theta").replace("Θ", "theta")
    s = s.replace("≥", ">=").replace("≤", "<=")
    s = s.replace("–", "-").replace("—", "-")
    s = s.replace("**", "^")  # v1.2
    s = s.replace("0r", " or ")
    s = s.replace("ror", " or ")
    s = re.sub(r"\bor(\d)", r"or \1", s)
    s = re.sub(r"(\d)or\b", r"\1 or", s)
    s = re.sub(r"\b(sin|cos|tan|cot|sec|csc)(theta|x|\()", r"\1 \2", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\bor(\d)", r"or \1", s)   # v1.2: or3 -> or 3
    s = re.sub(r"(\d)or\b", r"\1 or", s)
    s = re.sub(r"\s*=\s*", "=", s)
    s = re.sub(r"\s*>\s*=\s*", ">=", s)
    s = re.sub(r"\s*<\s*=\s*", "<=", s)
    s = re.sub(r"\s*\+\s*", "+", s)
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"\s+or\s+", " or ", s)
    s = re.sub(r"\s*\(\s*", "(", s)
    s = re.sub(r"\s*\)\s*", ")", s)
    s = re.sub(r"\s*\*\s*", "*", s)
    s = re.sub(r"\s*\^\s*", "^", s)
    return s.strip()

def _is_correct(response: str, expected: str) -> bool:
    return _graceful_is_correct(response, expected)
# ----- v1.1 predicates -----

def _extract_roots(text: str):
    """Extract numeric roots from patterns like 'x = 5', 'x = -5', 'x=-5'."""
    if not isinstance(text, str):
        return set()
    roots = set()
    for m in re.finditer(r"x\s*=\s*(-?\d+(?:\.\d+)?)", text):
        try:
            roots.add(float(m.group(1)))
        except ValueError:
            continue
    return roots


def _quad_sign_flip(nr: str, expected: str) -> bool:
    """
    General sign-error detector.

    Fires when the learner's roots share the same magnitudes as the
    expected roots but at least one sign differs. Silent when the
    roots differ in value (that is a different error).
    """
    if not isinstance(nr, str) or not isinstance(expected, str):
        return False
    got = _extract_roots(nr)
    want = _extract_roots(expected)
    if not got or not want:
        return False
    # Same magnitudes on both sides?
    if {abs(v) for v in got} != {abs(v) for v in want}:
        return False
    # At least one sign differs?
    if got == want:
        return False
    return True


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


# ----- v1.2 predicates -----

def _factorisation_incomplete(nr: str, expected: str) -> bool:
    """Factors present, no solved roots; expected has roots."""
    if "x=" not in _norm(expected):
        return False
    if "x=" in nr:
        return False
    # two bracket groups e.g. (x-2)(x-3) or (x-2)(x-3)=0
    return bool(re.search(r"\([^)]+\)\s*\([^)]+\)", nr))


def _asymptote_confusion(nr: str, expected: str) -> bool:
    if re.search(r"horizontal\s+asymptote\s*:?\s*x\s*=", nr):
        return True
    if re.search(r"vertical\s+asymptote\s*:?\s*y\s*=", nr):
        return True
    return False


def _identity_misapply(nr: str, expected: str) -> bool:
    n = re.sub(r"\s+", "", nr)
    n = n.replace("theta", "")
    bad = [
        "sin^2+cos^2=sin^2cos^2",
        "sin^2+cos^2=sin^2*cos^2",
        "1=sin^2cos^2",
        "1=sin^2*cos^2",
        "sin^2cos^2=1",
        "sin^2*cos^2=1",
    ]
    return any(b in n for b in bad)

def _chain_rule_drop(nr: str, expected: str) -> bool:
    """Demo-scoped: same inner and power; response coeff is proper divisor of expected."""
    compact = nr.replace(" ", "")
    # Boundary: already wrote outer * inner factor → not a pure "drop"
    if re.search(r"\)\^\d+\*\d+", compact):
        return False
    if compact.count("*") >= 2:
        return False

    pat = re.compile(r"(?P<coef>\d+)\*?\((?P<inner>[^)]+)\)\^(?P<pow>\d+)")
    mr = pat.search(compact)
    me = pat.search(_norm(expected).replace(" ", ""))
    if not mr or not me:
        return False
    if mr["inner"] != me["inner"] or mr["pow"] != me["pow"]:
        return False
    cr, ce = int(mr["coef"]), int(me["coef"])
    if cr >= ce or cr <= 0:
        return False
    return ce % cr == 0



def _gp_common_ratio(nr: str, expected: str) -> bool:
    # off-by-one: a*r^n vs a*r^(n-1)
    if re.search(r"\d+\s*\*\s*\d+\s*\^\s*n\b", nr) and "n-1" in _norm(expected):
        if "n-1" not in nr and "^(n-1)" not in nr.replace(" ", ""):
            return True
    # arithmetic form a+(n-1)d style for GP expected
    if re.search(r"\d+\s*\+\s*\(?\s*n\s*-\s*1\s*\)?", nr) and "*" in _norm(expected):
        return True
    return False


def _boxplot_iqr(nr: str, expected: str) -> bool:
    """Expected embeds {a,b,c,d,e} IQR = val. Fire if response equals range."""
    m = re.search(
        r"\{(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\}.*iqr\s*=\s*(\d+)",
        _norm(expected),
    )
    if not m:
        return False
    a, b, c, d, e = map(int, m.groups()[:5])
    iqr = int(m.group(6))
    rng = e - a
    # response is a bare number
    rm = re.search(r"-?\d+", nr)
    if not rm:
        return False
    val = int(rm.group(0))
    if val == rng and val != iqr:
        return True
    return False


def _similarity_ratio(nr: str, expected: str) -> bool:
    def parse_ratio(s: str):
        m = re.search(r"(\d+)\s*:\s*(\d+)", s)
        if m:
            return int(m.group(1)), int(m.group(2))
        m = re.search(r"(\d+)\s*/\s*(\d+)", s)
        if m:
            return int(m.group(1)), int(m.group(2))
        return None

    pr, pe = parse_ratio(nr), parse_ratio(_norm(expected))
    if not pr or not pe:
        return False
    a, b = pr
    c, d = pe
    if a * d == b * c:
        return False  # equivalent
    if a * c == b * d and (a, b) != (c, d):
        # reciprocal: a/b == d/c
        return a * c == b * d
    # classic reciprocal a:b vs b:a
    return (a, b) == (d, c)


# ------------------------------------------------------------------
# N08 v2 — trigger-based fallback layer
# Loads 69 misconceptions from misconceptions_v2.csv.
# Fires only when skill-scoped rules miss, gated by topic.
# ------------------------------------------------------------------

_TRIGGER_LIBRARY = None


def _load_trigger_library():
    """Load the trigger regexes from misconceptions_v2.csv (cached)."""
    global _TRIGGER_LIBRARY
    if _TRIGGER_LIBRARY is not None:
        return _TRIGGER_LIBRARY

    import pandas as pd
    path = Path(__file__).resolve().parents[2] / "data" / "processed" / "tutor" / "misconceptions_v2.csv"
    if not path.exists():
        _TRIGGER_LIBRARY = []
        return _TRIGGER_LIBRARY

    try:
        df = pd.read_csv(path)
    except Exception:
        _TRIGGER_LIBRARY = []
        return _TRIGGER_LIBRARY

    rules = []
    for _, row in df.iterrows():
        try:
            pattern = re.compile(str(row["trigger_pattern"]), re.IGNORECASE)
        except re.error:
            continue
        rules.append({
            "mid": str(row["misconception_id"]).strip(),
            "topic": str(row["topic"]).strip(),
            "error_class": str(row["error_class"]).strip(),
            "description": str(row["description"]).strip(),
            "pattern": pattern,
            "severity": str(row["severity"]).strip(),
        })
    _TRIGGER_LIBRARY = rules
    return rules


_TOPIC_PREFIX = {
    "algebra.": "ALG",
    "sequences.": "SEQ",
    "functions.": "FUNC",
    "finance.": "FIN",
    "calculus.": "CALC",
    "probability.": "PROB",
    "trig.": "TRIG",
    "euclidean.": "EUCL",
    "analytical_geom.": "AGEO",
    "stats.": "STAT",
}


def _topic_from_skill(skill_id: str):
    if not skill_id:
        return None
    s = str(skill_id).lower()
    for prefix, code in _TOPIC_PREFIX.items():
        if s.startswith(prefix):
            return code
    return None


_CLASS_TO_ERROR_TYPE = {
    "procedural":   ErrorType.PROCEDURAL,
    "conceptual":   ErrorType.CONCEPTUAL,
    "notation":     ErrorType.REPRESENTATION,
    "presentation": ErrorType.PROCEDURAL,
    "reading":      ErrorType.STRATEGY,
    "arithmetic":   ErrorType.ARITHMETIC,
    "general":      ErrorType.UNKNOWN,
}


def _error_type_for_class(cls: str) -> ErrorType:
    return _CLASS_TO_ERROR_TYPE.get(str(cls).lower(), ErrorType.UNKNOWN)


RuleFn = Callable[[str, str], bool]
RuleSpec = Tuple[str, ErrorType, str, RuleFn]

# skill_id -> ordered list of rules (first match wins)
RULES: Dict[str, List[RuleSpec]] = {
    "algebra.quadratic.solve": [
        (
            "M_SIGN_ERROR_FACTORISATION",
            ErrorType.PROCEDURAL,
            "Learner flipped the sign of a root when reading the factor.",
            _quad_sign_flip,
        ),
        (
            "M_FACTORISATION_INCOMPLETE",
            ErrorType.PROCEDURAL,
            "Factorised form written, but each linear factor not solved for x.",
            _factorisation_incomplete,
        ),
    ],
    "functions.parabola.range": [
        (
            "M_TP_COORD_CONFUSION",
            ErrorType.REPRESENTATION,
            "Learner used the x-coordinate of the turning point as the range bound.",
            _parab_range_yp,
        ),
    ],
    "trig.reduction.simplify": [
        (
            "M_REDUCTION_SIGN",
            ErrorType.CONCEPTUAL,
            "Learner applied an incorrect sign under the reduction formula.",
            _trig_red_sign,
        ),
    ],
    "analytical_geom.parallelogram.prove": [
        (
            "M_DIAGRAM_ASSUMPTION",
            ErrorType.STRATEGY,
            "Learner assumed parallelism from the diagram without proof.",
            _ageo_diagram,
        ),
    ],
    "euclidean.semicircle.prove": [
        (
            "M_MISSING_THEOREM_CITATION",
            ErrorType.PROCEDURAL,
            "Learner stated 90 degrees without citing the theorem.",
            _eucl_missing_cite,
        ),
    ],
    # v1.2 new skills
    "functions.hyperbola.asymptotes": [
        (
            "M_ASYMPTOTE_CONFUSION",
            ErrorType.REPRESENTATION,
            "Horizontal and vertical asymptotes swapped or mislabelled.",
            _asymptote_confusion,
        ),
    ],
    "trig.identity.simplify": [
        (
            "M_IDENTITY_MISAPPLY",
            ErrorType.CONCEPTUAL,
            "Invalid Pythagorean-form identity applied.",
            _identity_misapply,
        ),
    ],
    "calculus.chain_rule": [
        (
            "M_CHAIN_RULE_DROP",
            ErrorType.PROCEDURAL,
            "Outer derivative taken, inner derivative factor omitted. (demo-scoped)",
            _chain_rule_drop,
        ),
    ],
    "sequences.gp.term": [
        (
            "M_GP_COMMON_RATIO",
            ErrorType.PROCEDURAL,
            "GP term handled with arithmetic thinking OR wrong ratio OR off-by-one exponent.",
            _gp_common_ratio,
        ),
    ],
    "statistics.boxplot.iqr": [
        (
            "M_BOXPLOT_IQR",
            ErrorType.REPRESENTATION,
            "Range used in place of IQR.",
            _boxplot_iqr,
        ),
    ],
    "euclidean.similarity.ratio": [
        (
            "M_SIMILARITY_RATIO",
            ErrorType.CONCEPTUAL,
            "Similarity ratio inverted (image:object vs object:image).",
            _similarity_ratio,
        ),
    ],
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

    for mid, etype, expl, pred in RULES.get(skill_id, []):
        if pred(nr, expected_answer):
            return DiagnosisResult(
                error_type=etype,
                misconception_id=mid,
                confidence=0.85,
                rule_id=f"D_{mid}",
                explanation=expl,
            )

    # Layer 2 — trigger-based fallback (N08 v2)
    topic_hint = _topic_from_skill(skill_id)
    for rule in _load_trigger_library():
        if topic_hint and rule["topic"] not in (topic_hint, "GEN"):
            continue
        if rule["pattern"].search(nr):
            return DiagnosisResult(
                error_type=_error_type_for_class(rule["error_class"]),
                misconception_id=rule["mid"],
                confidence=0.65,
                rule_id=f"D_TRIGGER_{rule['mid']}",
                explanation=rule["description"],
            )

    return DiagnosisResult(
        error_type=ErrorType.UNKNOWN,
        misconception_id=None,
        confidence=0.3,
        rule_id="D_UNKNOWN",
        explanation="No matching correct or misconception pattern after normalisation.",
    )


def reachable_misconception_ids() -> set[str]:
    ids = set()
    for rules in RULES.values():
        for mid, *_ in rules:
            ids.add(mid)
    for rule in _load_trigger_library():
        ids.add(rule["mid"])
    return ids