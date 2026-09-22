"""Diagnose every layer of the near-miss pipeline."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.answer_matcher import _light_normalise, near_miss, compare

print("=== _light_normalise ===")
print("input :", repr("x = -5 0r 22."))
print("output:", repr(_light_normalise("x = -5 0r 22.")))
print()

print("=== near_miss ===")
print("result:", near_miss("x = -5 0r 22.", "x = -5 or x = 2"))
print()

print("=== compare ===")
print("result:", compare("x = -5 0r 22.", "x = -5 or x = 2").value)
print()

eng = Path("src/tutor/tutor_engine.py").read_text(encoding="utf-8")
print("=== engine wiring ===")
print("has D_NEAR_MISS string         :", "D_NEAR_MISS" in eng)
print("has near_miss import           :", "from .answer_matcher import near_miss" in eng)
print("has near-miss renderer branch  :", 'D_NEAR_MISS' in eng and 'I read your answer' in eng)
print()

mat = Path("src/tutor/answer_matcher.py").read_text(encoding="utf-8")
print("=== answer_matcher state ===")
print("has punctuation strip          :", 'r"[.,;!?]+\\s*$"' in mat)
print("has 0r fix                     :", "0r" in mat)
