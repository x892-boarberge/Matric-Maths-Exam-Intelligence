"""Add is_seasoned_hint; fix trailing-space bug in warmth check."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SALT = ROOT / "src" / "tutor" / "salt_check.py"
src = SALT.read_text(encoding="utf-8")

# 1. Fix the trailing-space bug
old_warmth = '''    # Warmth signal
    if "?" in line:
        return True, ""
    punct = [" ", ",", ".", ":", ";", "!", "-", "\\u2014"]
    for opener in WARMTH_OPENERS:
        for p in punct:
            if low.startswith(opener + p):
                return True, ""
    # Also allow warmth mid-line for very short lines
    for opener in WARMTH_OPENERS:
        if " " + opener + " " in low[:40]:
            return True, ""'''

new_warmth = '''    # Warmth signal
    if "?" in line:
        return True, ""
    punct = [" ", ",", ".", ":", ";", "!", "-", "\\u2014"]
    for opener in WARMTH_OPENERS:
        o = opener.rstrip()
        for p in punct:
            if low.startswith(o + p):
                return True, ""
    # Also allow warmth mid-line for very short lines
    for opener in WARMTH_OPENERS:
        o = opener.rstrip()
        if " " + o + " " in low[:40]:
            return True, ""'''

if old_warmth in src:
    src = src.replace(old_warmth, new_warmth, 1)
    print("Trailing-space bug fixed")
else:
    print("WARNING - warmth block not found or already patched")

# 2. Add is_seasoned_hint function
if "def is_seasoned_hint" not in src:
    hint_fn = '''


def is_seasoned_hint(line):
    """
    Check for hints and teaching lines.

    Hints are direct by design. They do not need a warmth opener. They
    need to pass the forbidden checks (no laws, no shaming, no leaks,
    no blame) and be non-empty.

    Returns:
        (True, "") if the hint is acceptable.
        (False, reason) otherwise.
    """
    if not isinstance(line, str) or not line.strip():
        return False, "empty line"

    low = line.lower()
    for pattern in FORBIDDEN:
        if re.search(pattern, low):
            return False, "forbidden phrase: " + pattern

    return True, ""
'''
    src = src.rstrip() + hint_fn
    print("is_seasoned_hint added")
else:
    print("is_seasoned_hint already present")

SALT.write_text(src, encoding="utf-8")
print("salt_check.py updated")
