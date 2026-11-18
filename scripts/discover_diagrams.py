import json, sys
from pathlib import Path
from collections import Counter

# 1. What diagram types does each pool declare?
POOL_DIR = Path("data/processed/tutor/variant_pools")
hints = Counter()
pool_hints = {}
for p in sorted(POOL_DIR.glob("*_pool.json")):
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    pool_name = p.stem.replace("_pool", "")
    if not d: continue
    v = d[0]
    hint = v.get("diagram_hint", "(none)")
    pool_hints[pool_name] = hint
    hints[hint] += 1

print("=== Diagram types by pool ===")
for name, hint in sorted(pool_hints.items()):
    print(f"  {name:12}  {hint}")

print("\n=== Diagram type counts ===")
for hint, count in sorted(hints.items(), key=lambda x: -x[1]):
    print(f"  {count:3}×  {hint}")

# 2. Is matplotlib available?
print("\n=== Rendering dependencies ===")
try:
    import matplotlib
    print(f"  matplotlib: {matplotlib.__version__}")
except ImportError:
    print("  matplotlib: NOT INSTALLED")
try:
    import numpy as np
    print(f"  numpy: {np.__version__}")
except ImportError:
    print("  numpy: NOT INSTALLED")

# 3. Where should diagrams live?
diag_dir = Path("data/processed/tutor/variant_diagrams")
print(f"\n=== Diagram output dir ===")
print(f"  Target: {diag_dir}")
print(f"  Exists: {diag_dir.exists()}")
if diag_dir.exists():
    pngs = list(diag_dir.glob("*.png"))
    print(f"  Existing PNGs: {len(pngs)}")
