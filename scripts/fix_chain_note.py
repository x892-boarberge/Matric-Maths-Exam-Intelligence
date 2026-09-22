"""Rewrite the chain rule note to start with a warmth opener."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "src" / "tutor" / "analogue_library.py"
src = LIB.read_text(encoding="utf-8")

old = '"note": "Chain rule: outer derivative times inner derivative. Do not forget the inner.",'
new = '"note": "Remember the chain rule: outer derivative times inner derivative. Do not forget the inner.",'

if old in src:
    src = src.replace(old, new, 1)
    LIB.write_text(src, encoding="utf-8")
    print("Chain rule note fixed")
else:
    print("Chain rule note text not found")
