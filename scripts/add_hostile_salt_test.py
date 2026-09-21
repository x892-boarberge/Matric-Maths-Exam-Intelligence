"""Add hostile lines to the salt-check coverage test."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "test_salt_check.py"
src = TEST.read_text(encoding="utf-8")

old = '''        + m._OFF_TOPIC
        + m._PRAISE_SPECIFIC
    )'''

new = '''        + m._OFF_TOPIC
        + m._PRAISE_SPECIFIC
        + m._HOSTILE
        + m._HOSTILE_REPEAT
    )'''

if old in src:
    src = src.replace(old, new, 1)
    TEST.write_text(src, encoding="utf-8")
    print("Salt test extended to cover hostile lines")
else:
    print("Salt test block not found.")
