import json
from pathlib import Path

POOL_DIR = Path("data/processed/tutor/variant_pools")
expected = ["8.1", "8.2.1", "8.2.2", "9.1", "9.2", "9.3", "9.4", "10.1", "10.2"]

print("=== Q8-Q10 pool existence check ===\n")
missing = []
for name in expected:
    p = POOL_DIR / f"{name}_pool.json"
    if not p.exists():
        print(f"  {name}: MISSING")
        missing.append(name)
        continue
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    sample = d[0] if d else {}
    q = sample.get("variant_question", "")[:70]
    exp = sample.get("expected", "")[:60]
    print(f"  {name}: {len(d)} variants")
    print(f"      Q: {q}")
    print(f"      Expected: {exp}")

print(f"\n=== Summary: {len(expected) - len(missing)}/{len(expected)} pools exist ===")
if missing:
    print(f"Missing: {missing}")
