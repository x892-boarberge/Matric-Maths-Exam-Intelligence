import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor.diagnosis import RULES, SEQ_TEACHINGS, get_sequence_teaching

seq = [s for s in RULES if s.startswith("sequences.")]
print(f"Skills: {len(seq)}")
for s in sorted(seq):
    print(f"  {s}: {len(RULES[s])} rules")

print(f"\nSEQ_TEACHINGS: {len(SEQ_TEACHINGS)}")
sample = get_sequence_teaching("M_SEQ_GAPS")
if sample:
    print(f"Sample (M_SEQ_GAPS): {sample[:100]}...")
else:
    print("WARNING: M_SEQ_GAPS not found in SEQ_TEACHINGS")
