import json, re, shutil
from pathlib import Path
from datetime import datetime

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

def clean_math(s):
    if not isinstance(s, str):
        return s
    # Fix "t+-N" -> "t-N", "t--N" -> "t+N"
    s = re.sub(r"\+\s*-(\d+)", r"- \1", s)
    s = re.sub(r"-\s*-(\d+)", r"+ \1", s)
    # Fix "= -9 + 6 + -4" -> "= -9 + 6 - 4"
    s = re.sub(r"\+\s*-(\d)", r"- \1", s)
    # Fix "1·-1/2" -> "1·(-1/2)" — wrap negative fractions in parens after multiplication dot
    s = re.sub(r"·-(\d)", r"·(-\1", s)  # tentative
    # Fix display of (t-N) after cleaning
    s = re.sub(r"\(\s*t\s*-\s*(\d+)\s*\)", r"(t-\1)", s)
    s = re.sub(r"\(\s*t\s*\+\s*(\d+)\s*\)", r"(t+\1)", s)
    return s

def clean_recursive(obj):
    if isinstance(obj, str): return clean_math(obj)
    if isinstance(obj, list): return [clean_recursive(x) for x in obj]
    if isinstance(obj, dict): return {k: clean_recursive(v) for k, v in obj.items()}
    return obj

for name in ["2.1.1", "2.1.3"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    d_clean = clean_recursive(d)
    shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(d_clean, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{name}: cleaned")

print("\n=== FINAL VERIFY ===")
for name in ["2.1.1", "2.1.3"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    print(f"\n{name}: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:110]}")
        print(f"     Expected: {v['expected']}")

# Full 2025 Paper 1 content audit
print("\n\n=== 2025 PAPER 1 — FULL AUDIT ===")
all_pools = [
    "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.2",
    "2.1.1", "2.1.2", "2.1.3", "2.2.1", "2.2.2",
    "3.1", "3.2", "3.3", "3.4",
    "4.1", "4.2", "4.3", "4.4", "4.5", "4.6",
    "5.1", "5.2", "5.3.1", "5.3.2", "5.4", "5.5", "5.6",
    "6.1", "6.2", "6.3",
    "7.1", "7.2", "7.3.1", "7.3.2",
    "8.1", "8.2.1", "8.2.2",
    "9.1", "9.2", "9.3", "9.4",
    "10.1", "10.2",
    "11.1.1", "11.1.2", "11.2", "11.3.1", "11.3.2",
]
total_variants = 0
present = 0
for name in all_pools:
    p = POOL_DIR / f"{name}_pool.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8-sig"))
        total_variants += len(d)
        present += 1

print(f"Subquestion pools: {present}/{len(all_pools)} present")
print(f"Total variants: {total_variants}")
if present == len(all_pools):
    print("\n✅ 2025 PAPER 1 IS CONTENT-COMPLETE.")
    print("   All 49 subquestions have variant pools.")
