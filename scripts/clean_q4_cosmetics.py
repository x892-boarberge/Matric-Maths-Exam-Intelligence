import json
from pathlib import Path
from datetime import datetime
import shutil

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

REPLACEMENTS = [
    ("log_{1/2)", "log_{1/2}"),
    ("log_{1/3)", "log_{1/3}"),
    ("log_{1/4)", "log_{1/4}"),
    ("log_{1/5)", "log_{1/5}"),
    ("{1/2}^", "(1/2)^"),
    ("{1/3}^", "(1/3)^"),
    ("{1/4}^", "(1/4)^"),
    ("{1/5}^", "(1/5)^"),
    ("log_1/2", "log_{1/2}"),
    ("log_1/3", "log_{1/3}"),
    ("log_1/4", "log_{1/4}"),
    ("log_1/5", "log_{1/5}"),
]

def clean(s):
    if not isinstance(s, str):
        return s
    for old, new in REPLACEMENTS:
        s = s.replace(old, new)
    return s

def clean_recursive(obj):
    if isinstance(obj, str):
        return clean(obj)
    if isinstance(obj, list):
        return [clean_recursive(x) for x in obj]
    if isinstance(obj, dict):
        return {k: clean_recursive(v) for k, v in obj.items()}
    return obj

for name in ["4.4", "4.5", "4.6"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    d = clean_recursive(d)
    shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{name}: cleaned")

print("\n=== VERIFY AFTER CLEANUP ===\n")
for name in ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    print(f"{name}_pool.json: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:80]}")
        print(f"     Expected: {v['expected']}")
    print()
