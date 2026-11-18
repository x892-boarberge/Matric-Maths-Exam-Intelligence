import json
from pathlib import Path

data = json.loads(Path("data/processed/tutor/playbooks/2025_P1_Q2.json").read_text(encoding="utf-8-sig"))
print("Top-level keys:", list(data.keys()))
subs = data.get("subquestions", {})
print(f"\nSubquestion count: {len(subs)}")
for sid, sub in subs.items():
    print(f"\n{sid}: {type(sub).__name__}")
    if isinstance(sub, dict):
        for k, v in sub.items():
            print(f"  {k}: {str(v)[:120]}")
    break
