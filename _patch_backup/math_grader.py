"""
Layered practice-mode grader.

Cascade of matchers. Each returns confidence. Highest wins.
Below threshold → uncertain → caller asks the learner.

Never says "wrong" without confidence.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

try:
    import sympy as sp
    _HAS_SYMPY = True
except ImportError:
    _HAS_SYMPY = False


class MatchKind(Enum):
    MATCH = "match"
    NO_MATCH = "no_match"
    UNCERTAIN = "uncertain"


@dataclass
class GradeResult:
    kind: MatchKind
    confidence: float
    matcher: str
    reason: str = ""


# ==================================================================
# NORMALISATION
# ==================================================================

_UNICODE_MAP = [
    ("\u2212", "-"), ("\u2013", "-"), ("\u2014", "-"),
    ("\u00d7", "*"), ("\u00b7", "*"), ("\u22c5", "*"),
    ("\u2264", "<="), ("\u2265", ">="), ("\u2260", "!="),
    ("\u2208", " in "), ("\u2209", " not in "),
    ("\u211d", "R"), ("\u2124", "Z"), ("\u2115", "N"),
    ("\u2220", "angle "), ("\u2221", "angle "),
    ("\u221a", "sqrt"), ("\u221b", "cbrt"),
    ("\u03b8", "theta"), ("\u03c0", "pi"),
    ("\u00b2", "^2"), ("\u00b3", "^3"), ("\u2074", "^4"),
    ("\u2075", "^5"), ("\u2076", "^6"), ("\u2077", "^7"),
    ("\u00b0", "deg"),
    ("\u00b1", "+-"),
    ("\u2192", "->"),
    ("\u21d2", "=>"),
]

_ENGLISH_TO_SYMBOL = [
    (r"\bnot\s+equal\s+to\b", "!="),
    (r"\bis\s+not\s+equal\s+to\b", "!="),
    (r"\bnot\s+in\b", " not in "),
    (r"\bis\s+in\b", " in "),
    (r"\belement\s+of\b", " in "),
    (r"\bin\s+R\b", " in R"),
    (r"\bgreat(?:er)?\s+than\s+or\s+equal\s+to\b", ">="),
    (r"\bless\s+than\s+or\s+equal\s+to\b", "<="),
    (r"\bgreat(?:er)?\s+than\b", ">"),
    (r"\bless\s+than\b", "<"),
    (r"\bequal\s+to\b", "="),
    (r"\bplus\s+or\s+minus\b", "+-"),
    (r"\bsquare\s+root\s+of\b", "sqrt"),
    (r"\bcube\s+root\s+of\b", "cbrt"),
    (r"\bangle\b", "angle"),
    (r"\bdegree[s]?\b", "deg"),
    (r"\btheta\b", "theta"),
    (r"\bpi\b", "pi"),
]


def _normalise(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    for bad, good in _UNICODE_MAP:
        s = s.replace(bad, good)
    for pattern, repl in _ENGLISH_TO_SYMBOL:
        s = re.sub(pattern, repl, s, flags=re.IGNORECASE)
    # Comma decimal inside a number → dot (SA convention)
    s = re.sub(r"(\d),(\d)", r"\1.\2", s)
    # Insert * for implicit multiplication (2x → 2*x, 5n → 5*n)
    # Only for a single letter not followed by another letter
    s = re.sub(r"(\d)([a-z])(?![a-z])", r"\1*\2", s, flags=re.IGNORECASE)
    # 2(x+1) → 2*(x+1)
    s = re.sub(r"(\d)\(", r"\1*(", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # Lowercase for comparison stability
    return s.lower()


def _strip_prefix(s: str) -> str:
    """Strip a leading 'x = ' style prefix from a single value."""
    if not s:
        return s
    s = s.strip()
    m = re.match(r"^[a-zA-Z]\s*=\s*(.+)$", s)
    if m:
        return m.group(1).strip()
    return s


def _strip_label(s: str) -> str:
    """Remove 'x = ' or 'mean = ' or 'P(A or B) = ' or 'angle ACB = ' labels."""
    s = s.strip()
    # 'name = value' where name is up to 30 chars of letters/digits/brackets/subscripts
    m = re.match(r"^[a-z_0-9\(\)'∠\s]{1,40}\s*=\s*(.+)$", s)
    if m:
        return m.group(1).strip()
    return s


def _strip_subscripts(s: str) -> str:
    """T_n → T, S_20 → S."""
    return re.sub(r"([a-z])_\{?[a-z0-9]+\}?", r"\1", s)


def _strip_units(s: str) -> str:
    """Remove R prefix, currency symbols, deg suffix."""
    s = re.sub(r"\br\s*(\d)", r"\1", s)  # R58230 → 58230
    s = re.sub(r"\bdeg\b", "", s)         # 30deg → 30
    s = re.sub(r"°", "", s)
    return s.strip()


def _strip_spaces_in_numbers(s: str) -> str:
    """58 230.94 → 58230.94"""
    return re.sub(r"(\d)\s+(\d{3}\b)", r"\1\2", s)


def _canonical(s: str) -> str:
    """Full canonical form for exact comparison."""
    s = _normalise(s)
    s = _strip_spaces_in_numbers(s)
    s = _strip_subscripts(s)
    s = _strip_label(s)
    s = _strip_units(s)
    s = re.sub(r"\s+", "", s)
    return s


# ==================================================================
# SEGMENTATION
# ==================================================================

# Split on 'or' or 'and' or ';' or ', ' (comma followed by space and NOT digit)
SPLIT_RE = re.compile(r"\s*;\s*|\s+\bor\b\s+|\s+\band\b\s+|\s*,\s*(?![\d])", re.IGNORECASE)
FRACTION_RE = re.compile(r"^-?\d+\s*/\s*-?\d+$")


def _parts(s: str) -> list:
    s = _normalise(s)
    s = _strip_label(s)
    parts = [p.strip() for p in SPLIT_RE.split(s) if p.strip()]
    # Remove working-text fragments
    clean = []
    for p in parts:
        # Strip any residual 'x = ' style prefix
        p = _strip_prefix(p)
        # Strip trailing parentheses and working fragments
        p = re.sub(r"\(.*?\)", "", p).strip()
        p = re.sub(r"\b(from|see|moved|step|above|below|note)\b.*$", "", p).strip()
        if not p:
            continue
        if len(p) > 60:
            continue
        clean.append(p)
    return clean


# ==================================================================
# MATCHERS  (each returns (matched: bool, confidence: float, reason: str))
# ==================================================================

def m_exact(a: str, b: str):
    if _canonical(a) == _canonical(b):
        return True, 0.99, "exact after normalisation"
    return False, 0.0, ""


def m_numeric(a: str, b: str):
    """Single numeric value."""
    if not _HAS_SYMPY:
        return False, 0.0, ""
    try:
        av = sp.sympify(_strip_label(_strip_units(_normalise(a))))
        bv = sp.sympify(_strip_label(_strip_units(_normalise(b))))
        if sp.simplify(av - bv) == 0:
            return True, 0.96, "numeric equal"
    except Exception:
        pass
    return False, 0.0, ""


def m_numeric_multi_root(a: str, b: str):
    """Set of numbers — 'x = 2 or x = -5' vs '-5, 2'."""
    if not _HAS_SYMPY:
        return False, 0.0, ""
    ap = _parts(a)
    bp = _parts(b)
    if not ap or not bp:
        return False, 0.0, ""
    a_syms, b_syms = set(), set()
    for v in ap:
        try:
            a_syms.add(sp.sympify(_strip_units(v)))
        except Exception:
            pass
    for v in bp:
        try:
            b_syms.add(sp.sympify(_strip_units(v)))
        except Exception:
            pass
    if a_syms and b_syms and a_syms == b_syms:
        return True, 0.95, "multi-root set equal"

    # Pairwise fallback: same count, values equal after simplify
    if a_syms and b_syms and len(a_syms) == len(b_syms):
        remaining = set(b_syms)
        for av in a_syms:
            matched = False
            for bv in list(remaining):
                try:
                    if sp.simplify(av - bv) == 0:
                        remaining.discard(bv)
                        matched = True
                        break
                except Exception:
                    continue
            if not matched:
                return False, 0.0, ""
        if not remaining:
            return True, 0.95, "multi-root set equal (pairwise)"

    return False, 0.0, ""


def m_fraction_decimal(a: str, b: str):
    """3/4 ↔ 0.75, multi-part with tolerance."""
    if not _HAS_SYMPY:
        return False, 0.0, ""
    ap = _parts(a)
    bp = _parts(b)
    if not ap or not bp:
        return False, 0.0, ""
    a_vals = []
    b_vals = []
    for p in ap:
        try:
            a_vals.append(sp.sympify(p))
        except Exception:
            return False, 0.0, ""
    for p in bp:
        try:
            b_vals.append(sp.sympify(p))
        except Exception:
            return False, 0.0, ""
    if len(a_vals) != len(b_vals):
        return False, 0.0, ""
    # Try each permutation-free match
    remaining = list(b_vals)
    for av in a_vals:
        matched = False
        for bv in list(remaining):
            try:
                if sp.simplify(av - bv) == 0:
                    remaining.remove(bv)
                    matched = True
                    break
                try:
                    if abs(float(av) - float(bv)) <= 0.005:
                        remaining.remove(bv)
                        matched = True
                        break
                except Exception:
                    pass
            except Exception:
                continue
        if not matched:
            return False, 0.0, ""
    if not remaining:
        return True, 0.88, "fraction/decimal equal"
    return False, 0.0, ""


def m_symbolic(a: str, b: str):
    """Symbolic expression — 'Tn = 2 + 5n' vs 'T_n = 5n + 2'."""
    if not _HAS_SYMPY:
        return False, 0.0, ""
    try:
        a_expr = _strip_label(_strip_subscripts(_normalise(a)))
        b_expr = _strip_label(_strip_subscripts(_normalise(b)))
        # Pre-declare single-letter and common variables
        local_dict = {
            "n": sp.Symbol("n"),
            "x": sp.Symbol("x"),
            "y": sp.Symbol("y"),
            "t": sp.Symbol("t"),
            "k": sp.Symbol("k"),
            "a": sp.Symbol("a"),
            "b": sp.Symbol("b"),
            "c": sp.Symbol("c"),
            "d": sp.Symbol("d"),
            "r": sp.Symbol("r"),
            "T": sp.Symbol("T"),
            "S": sp.Symbol("S"),
        }
        av = sp.sympify(a_expr, locals=local_dict)
        bv = sp.sympify(b_expr, locals=local_dict)
        if sp.simplify(av - bv) == 0:
            return True, 0.94, "symbolic equal"
    except Exception:
        pass
    return False, 0.0, ""


def m_currency(a: str, b: str):
    """R58 230.94 ↔ R58230.94 ↔ A = 58230.94."""
    def _money(s):
        s = _normalise(s)
        s = _strip_label(s)
        s = re.sub(r"\br\s*", "", s)
        s = _strip_spaces_in_numbers(s)
        s = re.sub(r"\s+", "", s)
        return s
    if _money(a) == _money(b) and _money(a):
        return True, 0.93, "currency equal"
    return False, 0.0, ""


def m_coordinate_pair(a: str, b: str):
    """S(15; 16) ↔ S(15, 16) ↔ (15; 16)"""
    def _coords(s):
        nums = re.findall(r"-?\d+(?:\.\d+)?", _normalise(s))
        return tuple(nums)
    ca, cb = _coords(a), _coords(b)
    if ca and cb and ca == cb:
        return True, 0.92, "coordinate pair equal"
    return False, 0.0, ""


def m_interval(a: str, b: str):
    """x < -1 or x > 3 ↔ x ∈ (-∞; -1) ∪ (3; ∞) — light normalisation."""
    def _int(s):
        s = _normalise(s)
        s = re.sub(r"\s+", " ", s).strip()
        s = s.replace(" or ", " | ").replace("union", "|").replace("∪", "|")
        return s
    if _int(a) == _int(b):
        return True, 0.91, "interval equal"
    return False, 0.0, ""


def m_trig_general(a: str, b: str):
    """x = 30 + 360k ↔ x = 30° + k·360°"""
    def _trig(s):
        s = _normalise(s)
        s = s.replace("*", "").replace("·", "")
        s = re.sub(r"k\s*(\d+)", r"\1k", s)
        s = re.sub(r"(\d+)\s*k", r"\1k", s)
        s = s.replace("deg", "")
        s = re.sub(r"\s+", "", s)
        s = _strip_label(s)
        return s
    if _trig(a) == _trig(b):
        return True, 0.90, "trig general equal"
    return False, 0.0, ""


def m_plain_english_symbolic(a: str, b: str):
    """'x in R, x not equal to 3' ↔ 'x ∈ ℝ, x ≠ 3'"""
    if _canonical(a) == _canonical(b):
        return True, 0.90, "plain-english normalised equal"
    return False, 0.0, ""


def m_proof_keywords(a: str, b: str):
    """Proof-style answers — plain English assertions, not numbers.

    Only fires when BOTH sides are predominantly non-numeric.
    Will NOT fire on numeric answers, equation solutions, or short
    symbolic expressions.
    """
    def _is_prose(s):
        # Reject if the answer is a numeric/multi-root type
        if re.search(r"[-+]?\d+\.?\d*", s) and not re.search(
            r"\b(diameter|angle|parallel|perpendicular|bisect|equal|similar|tangent|cyclic|prove|circle|triangle|quadrilateral|midpoint|theorem)\b",
            s, re.IGNORECASE
        ):
            return False
        return True

    if not _is_prose(a) or not _is_prose(b):
        return False, 0.0, ""

    def _toks(s):
        s = _normalise(s)
        s = re.sub(r"[^a-z]+", " ", s)
        return set(s.split()) - {"is", "a", "an", "the", "of", "to", "and", "or", "that"}

    ta, tb = _toks(a), _toks(b)
    if not ta or not tb:
        return False, 0.0, ""

    # Require at least 3 meaningful words
    if len(ta) < 3 or len(tb) < 3:
        return False, 0.0, ""

    overlap = len(ta & tb) / max(len(ta), len(tb))
    if overlap >= 0.8:
        return True, min(0.85, 0.75 + (overlap - 0.8)), "proof keyword overlap"
    return False, 0.0, ""


# ==================================================================
# DISPATCH
# ==================================================================

ALL_MATCHERS = [
    ("exact", m_exact),
    ("numeric_multi_root", m_numeric_multi_root),
    ("fraction_decimal", m_fraction_decimal),
    ("trig_general", m_trig_general),
    ("currency", m_currency),
    ("coordinate_pair", m_coordinate_pair),
    ("numeric", m_numeric),
    ("interval", m_interval),
    ("plain_english_symbolic", m_plain_english_symbolic),
    ("symbolic", m_symbolic),
    ("proof_keywords", m_proof_keywords),  # last resort, prose only
]


def _count_expected_parts(text: str) -> int:
    """How many distinct answer parts does the expected text have?"""
    return len(_parts(text))


def _count_learner_parts(text: str) -> int:
    return len(_parts(text))


def grade(learner_text: str, expected_text: str,
          uncertain_threshold: float = 0.70) -> GradeResult:
    """
    Try every matcher. Return the highest-confidence result.

    If the top match is below threshold → UNCERTAIN (caller asks learner).
    If the top match is above threshold → MATCH.
    If no matcher fires and learner text looks empty/very short → NO_MATCH.
    """
    if not isinstance(learner_text, str) or not learner_text.strip():
        return GradeResult(MatchKind.NO_MATCH, 0.0, "empty", "no learner text")
    if not isinstance(expected_text, str) or not expected_text.strip():
        return GradeResult(MatchKind.UNCERTAIN, 0.0, "empty_expected", "no expected")

    # Multi-line: try each line, also the full text
    candidates = [learner_text]
    if "\n" in learner_text:
        candidates = [l for l in learner_text.splitlines() if l.strip()] + [learner_text]

    best = (0.0, None)
    for cand in candidates:
        for name, fn in ALL_MATCHERS:
            try:
                ok, conf, reason = fn(cand, expected_text)
            except Exception:
                continue
            if ok and conf > best[0]:
                best = (conf, (name, reason))

    if best[1] and best[0] >= uncertain_threshold:
        # Partial-answer guard: if expected has N roots and learner has < N,
        # downgrade to UNCERTAIN (so the tutor asks, doesn't fail).
        n_expected = _count_expected_parts(expected_text)
        n_learner = _count_learner_parts(learner_text)
        if n_expected >= 2 and n_learner >= 1 and n_learner < n_expected:
            # Confirm it's really a numeric multi-part situation
            if re.search(r"\d", expected_text) and re.search(r"\d", learner_text):
                return GradeResult(
                    MatchKind.UNCERTAIN,
                    min(0.65, best[0]),
                    best[1][0],
                    f"partial answer: learner has {n_learner} of {n_expected} parts",
                )
        return GradeResult(MatchKind.MATCH, min(0.99, best[0]), best[1][0], best[1][1])

    if best[1] and best[0] > 0.0:
        # Something fired but with low confidence
        return GradeResult(MatchKind.UNCERTAIN, best[0], best[1][0], best[1][1])

    # Nothing fired — check if learner text is very different
    if _looks_like_valid_attempt(learner_text):
        return GradeResult(MatchKind.UNCERTAIN, 0.0, "none", "no matcher fired")

    return GradeResult(MatchKind.NO_MATCH, 0.0, "none", "clearly not the answer")


def _looks_like_valid_attempt(text: str) -> bool:
    """Heuristic: does this look like a mathematical attempt?"""
    if not text:
        return False
    s = _normalise(text)
    # Has a number, variable, or operator
    return bool(re.search(r"\d|[a-z]=|=|\+|-|\*|/|<|>", s))


# --------------- convenience wrapper ---------------

def equivalent(learner_text: str, expected_text: str) -> bool:
    """Backward-compat: True only on confident MATCH."""
    return grade(learner_text, expected_text).kind == MatchKind.MATCH

# ==================================================================
# diagnose_wrong — warm diagnosis for wrong answers
# ==================================================================

def diagnose_wrong(learner_text: str, expected_text: str) -> Optional[str]:
    """Warm-diagnosis signal for a wrong answer.

    Returns None if it looks correct.
    Returns 'sign_flip' if magnitudes match but signs differ.
    Returns 'partial' if a strict subset of roots is present.
    Returns 'unknown' otherwise.
    """
    if equivalent(learner_text, expected_text):
        return None

    # Best line from learner
    best_got = set()
    lines = learner_text.splitlines() if "\n" in learner_text else [learner_text]
    for line in lines:
        g = set()
        for p in _parts(line):
            try:
                g.add(sp.sympify(p))
            except Exception:
                pass
        if len(g) > len(best_got):
            best_got = g

    want = set()
    for p in _parts(expected_text):
        try:
            want.add(sp.sympify(p))
        except Exception:
            pass

    if best_got and want:
        try:
            if {abs(x) for x in best_got} == {abs(x) for x in want} and best_got != want:
                return "sign_flip"
            if best_got < want and len(best_got) >= 1:
                return "partial"
        except Exception:
            pass

    return "unknown"
