import json
from pathlib import Path

POOL_DIR = Path("data/processed/tutor/variant_pools")
print("=== Q11 pool existence ===")
expected = ["11.1.1", "11.1.2", "11.2", "11.3.1", "11.3.2"]
missing = []
for name in expected:
    p = POOL_DIR / f"{name}_pool.json"
    if not p.exists():
        print(f"  {name}: MISSING")
        missing.append(name)
        continue
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    v = d[0] if d else {}
    print(f"  {name}: {len(d)} variants")
    print(f"      Q: {v.get('variant_question', '')[:80]}")
    print(f"      Expected: {v.get('expected', '')}")

if missing:
    print(f"\nMissing: {missing}")
else:
    print(f"\nAll 5 Q11 pools present.")
