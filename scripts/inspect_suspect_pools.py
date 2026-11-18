import json
from pathlib import Path

POOL_DIR = Path("data/processed/tutor/variant_pools")

for name in ["9.3", "9.4", "10.1"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    print(f"\n=== {name} ({len(d)} variants) ===")
    for i, v in enumerate(d[:3], 1):
        print(f"\n  [{i}] Q: {v['variant_question'][:120]}")
        print(f"      Expected: {v['expected']}")
        demo = v.get("demonstration", "")
        if demo:
            print(f"      Demo starts: {demo[:100]}...")
