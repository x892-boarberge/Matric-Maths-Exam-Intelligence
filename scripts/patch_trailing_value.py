"""Add a trailing-value layer for verbose expected answers."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATCHER = ROOT / "src" / "tutor" / "answer_matcher.py"
src = MATCHER.read_text(encoding="utf-8")

# Add the extraction helper just before compare()
helper = '''

def _extract_trailing_value(s: str):
    """
    If the expected string ends with "= value" (e.g. "{5,7,9,12,25} IQR = 7"),
    return the value. Used to match a bare learner answer against a verbose
    memo phrase.
    """
    m = re.search(r"=\\s*(-?[\\d.]+(?:\\s*/\\s*\\d+)?)\\s*$", s)
    if m:
        return m.group(1).strip()
    return None

'''
if "_extract_trailing_value" not in src:
    src = src.replace(
        "def compare(response: Any, expected: Any) -> Match:",
        helper.strip() + "\n\n\ndef compare(response: Any, expected: Any) -> Match:",
        1,
    )
    print("Added _extract_trailing_value helper")

# Add Layer 5 in compare() before the final return
old_ret = '''    # Layer 4 - structural or-equivalence
    if _structural_or_equivalent(r3, e3):
        return Match.MATCH

    return Match.NO_MATCH'''

new_ret = '''    # Layer 4 - structural or-equivalence
    if _structural_or_equivalent(r3, e3):
        return Match.MATCH

    # Layer 5 - learner answer is the trailing value of the verbose expected
    trailing = _extract_trailing_value(e)
    if trailing and _strip_all_spaces(r2) == _strip_all_spaces(trailing):
        return Match.MATCH

    return Match.NO_MATCH'''

if old_ret in src:
    src = src.replace(old_ret, new_ret, 1)
    print("Added Layer 5 - trailing-value match")
else:
    print("WARNING - Layer 4 return block not found")

MATCHER.write_text(src, encoding="utf-8")
print("answer_matcher.py patched")
