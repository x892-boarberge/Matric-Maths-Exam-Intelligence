"""Fix the disengagement test to check intent not wording."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "test_disengagement.py"
src = TEST.read_text(encoding="utf-8")

old = '''        msg = action.tutor_message.lower()
        assert "x = 2" not in msg
        assert "full solution" in msg or "won't give" in msg or "one useful step" in msg'''

new = '''        msg = action.tutor_message.lower()
        assert "x = 2" not in msg
        # The tutor must signal that it will not give the full answer.
        # Wording is now sourced from the meta library, so check for the
        # intent rather than a specific phrase.
        refuses_full_solution = any([
            "full solution" in msg,
            "won't give" in msg,
            "will not give" in msg,
            "one useful step" in msg,
            "not going to hand" in msg,
            "not give you the full" in msg,
        ])
        assert refuses_full_solution, "tutor did not signal refusal: " + msg'''

if old in src:
    src = src.replace(old, new, 1)
    TEST.write_text(src, encoding="utf-8")
    print("Disengagement test patched")
else:
    print("Old assertion not found. Inspect test_disengagement.py manually.")
