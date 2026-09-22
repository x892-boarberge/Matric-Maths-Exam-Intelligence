"""
Graceful answer matcher.

The tutor understands what the learner meant, not the exact string the
memo writes. This module provides layered equivalence checks that accept
reasonable presentation variations while still detecting mathematical
errors.

Returns one of:
    MATCH     - equivalent to expected
    NO_MATCH  - clearly not equivalent
    AMBIGUOUS - cannot decide; ask the learner to confirm

Layers, each tried in order:
    1. Exact after light normalisation (case, whitespace, unicode symbols)
    2. Whitespace-stripped equivalence (x = 2 == x=2)
    3. Function name spacing (sintheta == sin theta == sin(theta))
    4. Structural or-equivalence (x=2or3 == x=2 or x=3)
"""
from enum import Enum
from typing import Any
import re


class Match(str, Enum):
    MATCH = "match"
    NO_MATCH = "no_match"
    AMBIGUOUS = "ambiguous"


FUNC_NAMES = [
    "arcsin", "arccos", "arctan",
    "sin", "cos", "tan", "csc", "sec", "cot",
    "log", "ln", "sqrt",
]

FUNC_PATTERN = "|".join(sorted(FUNC_NAMES, key=len, reverse=True))


def _light_normalise(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = s.replace("\u2265", ">=").replace("\u2264", "<=").replace("\u2260", "!=")
    s = s.replace("\u00d7", "*").replace("\u00b7", "*").replace("\u22c5", "*")
    s = s.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-")
    s = s.replace("**", "^")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\b0r\b", "or", s)
    s = re.sub(r"\b0 r\b", "or", s)
    s = re.sub(r"[.,;!?]+\s*$", "", s)
    return s


def _strip_all_spaces(s: str) -> str:
    return re.sub(r"\s+", "", s)


def _normalise_functions(s: str) -> str:
    """
    sin theta / sintheta / sin(theta) all become sin(theta).
    Same for cos, tan, log, ln, sqrt, and arc* variants.
    """
    def repl(m):
        func = m.group(1)
        arg = m.group(2)
        # If arg is already parenthesised, do not double-wrap
        if arg.startswith("(") and arg.endswith(")"):
            return func + arg
        return func + "(" + arg + ")"

    pattern = r"\b(" + FUNC_PATTERN + r")\s*([a-z0-9]+|\([^)]+\))"
    prev = None
    guard = 0
    while prev != s and guard < 5:
        prev = s
        s = re.sub(pattern, repl, s)
        guard += 1
    return s


def _split_or(s: str):
    return [p for p in re.split(r"or", s) if p]


def _structural_or_equivalent(r: str, e: str) -> bool:
    """
    x=2or3 == x=2orx=3
    Same variable, split on 'or', one side may omit the variable name.
    """
    r_parts = _split_or(r)
    e_parts = _split_or(e)
    if len(r_parts) != len(e_parts) or len(r_parts) < 2:
        return False
    prefix = None
    for ep in e_parts:
        m = re.match(r"^([a-z]+)=", ep)
        if not m:
            return False
        if prefix is None:
            prefix = m.group(1)
        elif prefix != m.group(1):
            return False
    for rp, ep in zip(r_parts, e_parts):
        if rp == ep:
            continue
        if rp == ep[len(prefix) + 1:]:
            continue
        return False
    return True


def _extract_trailing_value(s: str):
    """
    If the expected string ends with "= value" (e.g. "{5,7,9,12,25} IQR = 7"),
    return the value. Used to match a bare learner answer against a verbose
    memo phrase.
    """
    m = re.search(r"=\s*(-?[\d.]+(?:\s*/\s*\d+)?)\s*$", s)
    if m:
        return m.group(1).strip()
    return None


def compare(response: Any, expected: Any) -> Match:
    """
    Compare a learner response to an expected answer.
    Returns MATCH, NO_MATCH, or AMBIGUOUS.
    """
    if not isinstance(response, str) or not isinstance(expected, str):
        return Match.NO_MATCH
    if not response.strip() or not expected.strip():
        return Match.NO_MATCH

    r = _light_normalise(response)
    e = _light_normalise(expected)

    # Layer 1 - direct after light normalisation
    if r == e:
        return Match.MATCH

    # Layer 2 - strip all spaces
    r2 = _strip_all_spaces(r)
    e2 = _strip_all_spaces(e)
    if r2 == e2:
        return Match.MATCH

    # Layer 3 - function name normalisation
    r3 = _normalise_functions(r2)
    e3 = _normalise_functions(e2)
    if r3 == e3:
        return Match.MATCH

    # Layer 4 - structural or-equivalence
    if _structural_or_equivalent(r3, e3):
        return Match.MATCH

    # Layer 5 - learner answer is the trailing value of the verbose expected
    trailing = _extract_trailing_value(e)
    if trailing and _strip_all_spaces(r2) == _strip_all_spaces(trailing):
        return Match.MATCH

    # Layer 6 - learner's normalised answer is a value-suffix of the expected,
    # and the boundary is not inside a number.
    # "IQR = 7" vs "... IQR = 7" -> match
    # "7" vs "17" -> no match (7 is inside the number 17)
    if _strip_all_spaces(r2) and _strip_all_spaces(r2) in _strip_all_spaces(e2):
        idx = _strip_all_spaces(e2).rfind(_strip_all_spaces(r2))
        # only accept as suffix (not interior) and only if not preceded by a digit
        if idx >= 0 and idx + len(_strip_all_spaces(r2)) == len(_strip_all_spaces(e2)):
            preceding = _strip_all_spaces(e2)[idx - 1] if idx > 0 else ""
            if not preceding.isdigit():
                return Match.MATCH

    return Match.NO_MATCH


def is_correct(response: Any, expected: Any) -> bool:
    """Convenience: True only on MATCH."""
    return compare(response, expected) == Match.MATCH


def near_miss(response, expected, max_edits=2):
    """
    Return True if the response is close to the expected answer, but not
    close enough for the matcher to accept it. Used to ask the learner
    "did you mean ...?" instead of saying wrong.
    """
    def edit_distance(a, b):
        if a == b:
            return 0
        if len(a) < len(b):
            a, b = b, a
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a):
            curr = [i + 1]
            for j, cb in enumerate(b):
                curr.append(min(prev[j + 1] + 1, curr[j] + 1,
                                prev[j] + (ca != cb)))
            prev = curr
        return prev[-1]

    if not isinstance(response, str) or not isinstance(expected, str):
        return False
    r = _strip_all_spaces(_light_normalise(response))
    e = _strip_all_spaces(_light_normalise(expected))
    if not r or not e:
        return False
    return edit_distance(r, e) <= max_edits

