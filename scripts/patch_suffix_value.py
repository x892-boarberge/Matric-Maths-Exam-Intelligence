"""Add a suffix-value layer to the graceful answer matcher."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATCHER = ROOT / "src" / "tutor" / "answer_matcher.py"
src = MATCHER.read_text(encoding="utf-8")

old_ret = '''    # Layer 5 - learner answer is the trailing value of the verbose expected
    trailing = _extract_trailing_value(e)
    if trailing and _strip_all_spaces(r2) == _strip_all_spaces(trailing):
        return Match.MATCH

    return Match.NO_MATCH'''

new_ret = '''    # Layer 5 - learner answer is the trailing value of the verbose expected
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

    return Match.NO_MATCH'''

if old_ret in src:
    src = src.replace(old_ret, new_ret, 1)
    MATCHER.write_text(src, encoding="utf-8")
    print("Added Layer 6 - suffix-value match")
else:
    print("WARNING - Layer 5 return block not found")
