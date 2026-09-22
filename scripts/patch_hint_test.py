"""Update the hint check script to use is_seasoned_hint."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "test_presentation_library.py"

# No change there - instead add a dedicated test file for hints
hint_test = '''"""Tests for the misconception hint library."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor import misconception_hints as mh
from src.tutor.salt_check import is_seasoned_hint


def test_all_hints_exist():
    assert len(mh.HINTS) == 12


def test_three_levels_per_misconception():
    for mid, entry in mh.HINTS.items():
        for lvl in ["H1", "H2", "H3"]:
            assert lvl in entry, mid + " missing " + lvl


def test_get_hint_returns_string():
    s = mh.get_hint("M_SIGN_ERROR_FACTORISATION", "H1")
    assert isinstance(s, str)
    assert len(s) > 20


def test_get_hint_unknown_returns_none():
    assert mh.get_hint("M_DOES_NOT_EXIST", "H1") is None
    assert mh.get_hint("M_SIGN_ERROR_FACTORISATION", "H9") is None


def test_all_hints_pass_forbidden_check():
    fails = []
    for mid, entry in mh.HINTS.items():
        for lvl, hint in entry.items():
            ok, reason = is_seasoned_hint(hint)
            if not ok:
                fails.append((mid, lvl, reason))
    assert not fails, str(fails)


def test_hints_do_not_leak_diagnostic_language():
    forbidden = ["learner flipped", "the learner", "the user"]
    for mid, entry in mh.HINTS.items():
        for lvl, hint in entry.items():
            low = hint.lower()
            for bad in forbidden:
                assert bad not in low, mid + " " + lvl + " contains " + bad
'''
out = ROOT / "tests" / "test_misconception_hints.py"
out.write_text(hint_test, encoding="utf-8")
print("test_misconception_hints.py written")
