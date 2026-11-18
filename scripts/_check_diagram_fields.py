import json
from pathlib import Path

# Check a rendered pool (4.1 — 30/30 rendered in batch)
print("=== 4.1_pool — diagram fields present? ===")
data = json.loads(Path("data/processed/tutor/variant_pools/4.1_pool.json").read_text(encoding="utf-8-sig"))
for i, v in enumerate(data[:3], 1):
    print(f"v{i}:")
    print(f"  diagram_path    = {v.get('diagram_path')!r}")
    print(f"  diagram_status  = {v.get('diagram_status')!r}")
    print(f"  diagram_note    = {v.get('diagram_note')!r}")
    p = v.get("diagram_path")
    if p:
        print(f"  file exists     = {Path(p).exists()}")

# Check a partial pool (5.4 — 26 partial)
print("\n=== 5.4_pool — partial diagram fields ===")
data = json.loads(Path("data/processed/tutor/variant_pools/5.4_pool.json").read_text(encoding="utf-8-sig"))
for i, v in enumerate(data[:2], 1):
    print(f"v{i}:")
    print(f"  diagram_path    = {v.get('diagram_path')!r}")
    print(f"  diagram_status  = {v.get('diagram_status')!r}")
    print(f"  diagram_partial_reason = {v.get('diagram_partial_reason')!r}")
