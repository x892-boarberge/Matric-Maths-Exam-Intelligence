"""Rewrite remaining notes to start with a warmth opener."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "src" / "tutor" / "analogue_library.py"
src = LIB.read_text(encoding="utf-8")

replacements = [
    (
        '"note": "The range depends on the y-coordinate of the turning point, not the x.",',
        '"note": "Remember: the range depends on the y-coordinate of the turning point, not the x.",',
    ),
    (
        '"note": "The vertical asymptote is the value that makes the denominator zero.",',
        '"note": "Remember: the vertical asymptote is the value that makes the denominator zero.",',
    ),
    (
        '"note": "The exponent is (n - 1), not n. Off by one is the common error.",',
        '"note": "Remember: the exponent is (n - 1), not n. Off by one is the common error.",',
    ),
    (
        '"note": "IQR is Q3 minus Q1, not the range (max minus min).",',
        '"note": "Remember: IQR is Q3 minus Q1, not the range (max minus min).",',
    ),
    (
        '"note": "Match the corresponding vertices first, then set up the ratio.",',
        '"note": "Remember: match the corresponding vertices first, then set up the ratio.",',
    ),
]

fixed = 0
for old, new in replacements:
    if old in src:
        src = src.replace(old, new, 1)
        fixed += 1
        print("Fixed:", old[:60])
    else:
        print("Not found:", old[:60])

LIB.write_text(src, encoding="utf-8")
print()
print("Fixed", fixed, "of", len(replacements), "notes")
