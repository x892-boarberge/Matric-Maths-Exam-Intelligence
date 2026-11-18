import json
from pathlib import Path

POOL_DIR = Path("data/processed/tutor/variant_pools")

print("=== Q5 and Q6 display checks ===\n")
for name in ["5.2", "5.4", "5.6", "6.1", "6.2", "6.3"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    v = d[0]
    q_text = v["variant_question"][:90]
    print(f"{name}: {q_text}")
    print(f"  Expected: {v['expected']}")
    # Check for bugs
    bugs = []
    if "1x^" in q_text: bugs.append("1x^ should be x^")
    if "+ -" in q_text: bugs.append("+ - should be - ")
    if "- -" in q_text: bugs.append("- - should be + ")
    if "1 units" in q_text: bugs.append("1 units should be 1 unit")
    if bugs:
        print(f"  ⚠️  BUGS: {bugs}")
    print()
