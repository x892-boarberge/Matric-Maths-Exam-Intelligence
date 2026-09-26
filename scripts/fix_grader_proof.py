"""Fix proof_keywords over-firing + confidence cap + partial answer rejection."""
from pathlib import Path
import ast

P = Path("src/tutor/math_grader.py")
src = P.read_text(encoding="utf-8-sig")

# ----------------------------------------------------------
# 1. proof_keywords: only fires on NON-NUMERIC text
# ----------------------------------------------------------
old = '''def m_proof_keywords(a: str, b: str):
    """'PT is a diameter' ↔ 'PT is a diameter' — keyword overlap."""
    def _toks(s):
        s = _normalise(s)
        s = re.sub(r"[^a-z0-9]+", " ", s)
        return set(s.split()) - {"is", "a", "the", "of", "to", "and", "or"}
    ta, tb = _toks(a), _toks(b)
    if not ta or not tb:
        return False, 0.0, ""
    overlap = len(ta & tb) / max(len(ta), len(tb))
    if overlap >= 0.7:
        return True, 0.75 + (overlap - 0.7), "proof keyword overlap"
    return False, 0.0, ""'''

new = '''def m_proof_keywords(a: str, b: str):
    """Proof-style answers — plain English assertions, not numbers.

    Only fires when BOTH sides are predominantly non-numeric.
    Will NOT fire on numeric answers, equation solutions, or short
    symbolic expressions.
    """
    def _is_prose(s):
        # Reject if the answer is a numeric/multi-root type
        if re.search(r"[-+]?\\d+\\.?\\d*", s) and not re.search(
            r"\\b(diameter|angle|parallel|perpendicular|bisect|equal|similar|tangent|cyclic|prove|circle|triangle|quadrilateral|midpoint|theorem)\\b",
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
    return False, 0.0, ""'''

if old in src:
    src = src.replace(old, new, 1)
    print("Fixed m_proof_keywords")
else:
    print("WARN: proof_keywords anchor not found")

# ----------------------------------------------------------
# 2. Cap confidence at 0.99 (never 1.05)
# ----------------------------------------------------------
old2 = '''    if best[1] and best[0] >= uncertain_threshold:
        return GradeResult(MatchKind.MATCH, best[0], best[1][0], best[1][1])'''
new2 = '''    if best[1] and best[0] >= uncertain_threshold:
        return GradeResult(MatchKind.MATCH, min(0.99, best[0]), best[1][0], best[1][1])'''
if old2 in src:
    src = src.replace(old2, new2, 1)
    print("Capped confidence at 0.99")

# ----------------------------------------------------------
# 3. Partial-answer guard: reject single-root match when expected has 2+ roots
# ----------------------------------------------------------
old3 = '''def grade(learner_text: str, expected_text: str,
          uncertain_threshold: float = 0.70) -> GradeResult:'''
new3 = '''def _count_expected_parts(text: str) -> int:
    """How many distinct answer parts does the expected text have?"""
    return len(_parts(text))


def _count_learner_parts(text: str) -> int:
    return len(_parts(text))


def grade(learner_text: str, expected_text: str,
          uncertain_threshold: float = 0.70) -> GradeResult:'''
if old3 in src:
    src = src.replace(old3, new3, 1)
    print("Added _count_* helpers")

# ----------------------------------------------------------
# 4. Guard inside grade() before accepting a match
# ----------------------------------------------------------
old4 = '''    if best[1] and best[0] >= uncertain_threshold:
        return GradeResult(MatchKind.MATCH, min(0.99, best[0]), best[1][0], best[1][1])'''

new4 = '''    if best[1] and best[0] >= uncertain_threshold:
        # Partial-answer guard: if expected has N roots and learner has < N,
        # downgrade to UNCERTAIN (so the tutor asks, doesn't fail).
        n_expected = _count_expected_parts(expected_text)
        n_learner = _count_learner_parts(learner_text)
        if n_expected >= 2 and n_learner >= 1 and n_learner < n_expected:
            # Confirm it's really a numeric multi-part situation
            if re.search(r"\\d", expected_text) and re.search(r"\\d", learner_text):
                return GradeResult(
                    MatchKind.UNCERTAIN,
                    min(0.65, best[0]),
                    best[1][0],
                    f"partial answer: learner has {n_learner} of {n_expected} parts",
                )
        return GradeResult(MatchKind.MATCH, min(0.99, best[0]), best[1][0], best[1][1])'''

if old4 in src:
    src = src.replace(old4, new4, 1)
    print("Added partial-answer guard")
else:
    print("WARN: match threshold anchor not found")

# ----------------------------------------------------------
# 5. Fix fraction_decimal so it runs BEFORE proof_keywords
# ----------------------------------------------------------
old5 = '''ALL_MATCHERS = [
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
    ("proof_keywords", m_proof_keywords),
]'''

new5 = '''ALL_MATCHERS = [
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
]'''

if old5 in src:
    src = src.replace(old5, new5, 1)
    print("Matchers ordered correctly")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)