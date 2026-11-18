import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor.diagnosis import diagnose

for pair in [
    ("t = 3 or t = 1/3", "t = -1"),
    ("t = 1", "t = -1"),
    ("t = -3", "t = -1"),
    ("t = 2", "t = 2"),
]:
    learner, expected = pair
    r = diagnose("functions.log.value", learner, expected)
    print(f"learner={learner!r}  expected={expected!r}")
    print(f"  -> misconception: {r.misconception_id}")
    print()
