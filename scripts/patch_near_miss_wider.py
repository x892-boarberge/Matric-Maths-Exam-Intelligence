"""Widen near-miss tolerance and confirm the engine injects D_NEAR_MISS."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATCHER = ROOT / "src" / "tutor" / "answer_matcher.py"
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"

m = MATCHER.read_text(encoding="utf-8")
old_sig = "def near_miss(response, expected, max_edits=2):"
new_sig = "def near_miss(response, expected, max_edits=3):"
if old_sig in m:
    m = m.replace(old_sig, new_sig, 1)
    MATCHER.write_text(m, encoding="utf-8")
    print("near_miss tolerance widened to 3")
else:
    print("near_miss signature not found (already widened?)")

e = ENGINE.read_text(encoding="utf-8")
if "D_NEAR_MISS" in e:
    print("D_NEAR_MISS injection present in engine")
else:
    print("WARNING - D_NEAR_MISS not in engine. Run wire_near_miss_and_pivot first.")
