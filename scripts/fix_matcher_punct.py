"""Strip trailing punctuation in _light_normalise."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "src" / "tutor" / "answer_matcher.py"
src = M.read_text(encoding="utf-8")

old = '''    s = re.sub(r"\\s+", " ", s)
    # Common learner typo: digit-zero instead of letter-o in "or"
    s = re.sub(r"\\b0r\\b", "or", s)
    s = re.sub(r"\\b0 r\\b", "or", s)
    return s'''

new = '''    s = re.sub(r"\\s+", " ", s)
    # Common learner typo: digit-zero instead of letter-o in "or"
    s = re.sub(r"\\b0r\\b", "or", s)
    s = re.sub(r"\\b0 r\\b", "or", s)
    # Strip trailing punctuation learners add: . , ; ! ?
    s = re.sub(r"[.,;!?]+\\s*$", "", s)
    return s'''

if old in src:
    src = src.replace(old, new, 1)
    M.write_text(src, encoding="utf-8")
    print("Trailing punctuation strip added")
else:
    print("WARNING - normalise block not found. Inspect manually.")
