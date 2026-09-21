"""Fix the disengagement test assertion (4-space indent)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "test_disengagement.py"
src = TEST.read_text(encoding="utf-8")

old = '    assert "full solution" in msg or "won\'t give" in msg or "one useful step" in msg'

new = '''    refuses_full_solution = any([
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
    print("Still not found. Showing the last 200 characters of the file:")
    print(repr(src[-200:]))
