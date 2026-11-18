import json
from pathlib import Path

pool = json.loads(Path("data/processed/tutor/variant_pools/4.1_pool.json").read_text(encoding="utf-8-sig"))
skipped = [4, 7, 16, 17, 23, 28]
for i in skipped:
    v = pool[i - 1]
    print(f"Variant {i}:")
    print(f"  Q: {v['variant_question']}")
    print()
