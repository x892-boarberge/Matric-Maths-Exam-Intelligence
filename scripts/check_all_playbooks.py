import json
from pathlib import Path

pb_dir = Path("data/processed/tutor/playbooks")
files = sorted(pb_dir.glob("2025_P1_Q*.json"))

expected = {"Q1": 6, "Q2": 5, "Q3": 4, "Q4": 6, "Q5": 7, "Q6": 3, "Q7": 4, "Q8": 3, "Q9": 4, "Q10": 2, "Q11": 5}

print(f"{'File':<25} {'Subqs':<8} {'Expected':<10} {'Status'}")
print("-" * 60)

for f in files:
    try:
        d = json.loads(f.read_text(encoding="utf-8-sig"))
        subq_count = len(d.get("subquestions", {}))
    except Exception as e:
        print(f"{f.name:<25} {'ERROR':<8} {'—':<10} {e}")
        continue
    q_key = f.stem.replace("2025_P1_", "")
    exp = expected.get(q_key, "?")
    status = "OK" if subq_count == exp else ("STUB" if subq_count == 0 else f"MISMATCH")
    print(f"{f.name:<25} {subq_count:<8} {exp:<10} {status}")
