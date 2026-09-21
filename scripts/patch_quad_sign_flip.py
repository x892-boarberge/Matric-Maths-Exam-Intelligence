"""Replace hardcoded _quad_sign_flip with a general predicate."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAG = ROOT / "src" / "tutor" / "diagnosis.py"
src = DIAG.read_text(encoding="utf-8")

old = '''def _quad_sign_flip(nr: str, expected: str) -> bool:
    n = nr.replace(" ", "")
    if "x=-3" in n:
        return True
    if re.search(r"x\\s*=\\s*2\\s*or\\s*x\\s*=\\s*-3", nr):
        return True
    if re.search(r"x\\s*=\\s*-3\\s*or\\s*x\\s*=\\s*2", nr):
        return True
    if re.search(r"x=2\\s*or\\s*-3", nr) or re.search(r"x=-3\\s*or\\s*2", nr):
        return True
    return False'''

new = '''def _extract_roots(text: str):
    """Extract numeric roots from patterns like 'x = 5', 'x = -5', 'x=-5'."""
    if not isinstance(text, str):
        return set()
    roots = set()
    for m in re.finditer(r"x\\s*=\\s*(-?\\d+(?:\\.\\d+)?)", text):
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
    return True'''

if old in src:
    src = src.replace(old, new, 1)
    DIAG.write_text(src, encoding="utf-8")
    print("Patched _quad_sign_flip")
else:
    print("Old predicate not found. Inspect diagnosis.py manually.")
    # Print the region around _quad_sign_flip so we can see what's there
    idx = src.find("def _quad_sign_flip")
    if idx >= 0:
        print()
        print("Current definition:")
        print(src[idx:idx+600])
