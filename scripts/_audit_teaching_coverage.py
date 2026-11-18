"""Audit: how many misconceptions have teachings? Coverage report."""
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.tutor.diagnosis import RULES, TEACHINGS

# Collect all distinct misconception IDs from RULES
all_mids = set()
for skill, rules in RULES.items():
    for entry in rules:
        if entry and len(entry) >= 1:
            mid = entry[0]
            if mid:
                all_mids.add(mid)

teaching_mids = set(TEACHINGS.keys())

covered = all_mids & teaching_mids
uncovered = all_mids - teaching_mids

print("=" * 60)
print("=== TEACHING COVERAGE AUDIT ===")
print("=" * 60)
print(f"Total distinct misconceptions in RULES: {len(all_mids)}")
print(f"Teachings authored in TEACHINGS:         {len(teaching_mids)}")
print(f"Misconceptions WITH teaching:            {len(covered)}  ({100*len(covered)/len(all_mids):.1f}%)")
print(f"Misconceptions WITHOUT teaching:         {len(uncovered)}  ({100*len(uncovered)/len(all_mids):.1f}%)")

print("\n" + "=" * 60)
print("=== UNCOVERED MISCONCEPTIONS BY NAMESPACE ===")
print("=" * 60)
by_ns = {}
for mid in uncovered:
    # Extract the middle word of the M_XXX_YYY pattern
    parts = mid.split('_')
    ns = parts[1] if len(parts) > 1 else 'OTHER'
    by_ns.setdefault(ns, []).append(mid)

for ns, mids in sorted(by_ns.items(), key=lambda x: -len(x[1])):
    print(f"\n[{ns}] — {len(mids)} missing")
    for m in sorted(mids):
        print(f"  - {m}")

print("\n" + "=" * 60)
print("=== COVERED MISCONCEPTIONS ===")
print("=" * 60)
for mid in sorted(covered):
    print(f"  ✓ {mid}")

print("\n" + "=" * 60)
print("=== NEXT ACTION ===")
print("=" * 60)
print(f"You need to author {len(uncovered)} teaching units in src/tutor/diagnosis.py")
print("to eliminate the 'There is a mistake here' fallback for known errors.")
