"""Add celebration and meta_comment pools to the salt check coverage."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "test_salt_check.py"
src = TEST.read_text(encoding="utf-8")

old = '''        + m._HOSTILE
        + m._HOSTILE_REPEAT
    )'''

new = '''        + m._HOSTILE
        + m._HOSTILE_REPEAT
        + m._CELEBRATION
        + m._META_COMMENT
        + m._OTHER_LANGUAGE
        + m._OTHER_LANGUAGE_REPEAT
    )'''

if old in src:
    src = src.replace(old, new, 1)
    TEST.write_text(src, encoding="utf-8")
    print("Salt test extended")
else:
    print("Salt test block not found. Inspect manually.")
