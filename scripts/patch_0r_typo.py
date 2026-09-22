"""Normalise the 0r -> or typo everywhere; raise near-miss tolerance."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATCHER = ROOT / "src" / "tutor" / "answer_matcher.py"
src = MATCHER.read_text(encoding="utf-8")

# 1. Add the 0r -> or fix to _light_normalise
old_light = '''    s = s.replace("**", "^")
    s = re.sub(r"\\s+", " ", s)
    return s'''
new_light = '''    s = s.replace("**", "^")
    s = re.sub(r"\\s+", " ", s)
    # Common learner typo: digit-zero instead of letter-o in "or"
    s = re.sub(r"\\b0r\\b", "or", s)
    s = re.sub(r"\\b0 r\\b", "or", s)
    return s'''

if old_light in src and "0r" not in src.split("_light_normalise")[1].split("def ")[0]:
    src = src.replace(old_light, new_light, 1)
    print("_light_normalise now fixes 0r -> or")
else:
    print("_light_normalise already patched or block not found")

# 2. Raise near_miss tolerance to 4
old_sig = "def near_miss(response, expected, max_edits=3):"
new_sig = "def near_miss(response, expected, max_edits=4):"
if old_sig in src:
    src = src.replace(old_sig, new_sig, 1)
    print("near_miss tolerance raised to 4")
else:
    print("near_miss already patched or signature not found")

MATCHER.write_text(src, encoding="utf-8")
print("patch complete")
