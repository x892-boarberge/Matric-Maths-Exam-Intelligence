"""Update salt tests for the new warmth contract."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "test_salt_check.py"
src = TEST.read_text(encoding="utf-8")

old = '''def test_salt_check_catches_no_warmth():
    ok, reason = is_seasoned("Solve the equation.")
    assert not ok
    assert "warmth" in reason'''

new = '''def test_salt_check_catches_no_warmth():
    # A truly cold declarative line: no question, no soft opener,
    # no teaching verb, no acknowledgement.
    ok, reason = is_seasoned("Equals zero.")
    assert not ok
    assert "warmth" in reason


def test_salt_check_accepts_teaching_verbs():
    # Teaching verbs are warmth signals for pedagogical lines.
    for line in ["Solve the equation.", "Check the sign.", "Look at the factor."]:
        ok, reason = is_seasoned(line)
        assert ok, line + " - " + reason


def test_salt_hint_accepts_direct_teaching():
    from src.tutor.salt_check import is_seasoned_hint
    ok, reason = is_seasoned_hint("Set x + 5 = 0. That gives x = -5.")
    assert ok, reason


def test_salt_hint_still_catches_laws():
    from src.tutor.salt_check import is_seasoned_hint
    ok, reason = is_seasoned_hint("You must set x + 5 = 0.")
    assert not ok


def test_salt_hint_still_catches_leaks():
    from src.tutor.salt_check import is_seasoned_hint
    ok, reason = is_seasoned_hint("Fallback to generic prompt.")
    assert not ok'''

if old in src:
    src = src.replace(old, new, 1)
    TEST.write_text(src, encoding="utf-8")
    print("Salt test updated")
else:
    print("WARNING - old test body not found")
