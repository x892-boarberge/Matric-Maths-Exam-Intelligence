import json
from pathlib import Path
d = json.loads(Path("data/processed/tutor/playbooks/2025_P1_Q11.json").read_text(encoding="utf-8-sig"))
print("Existing subquestions:", sorted(d["subquestions"].keys()))
print()
print("Paper has: 11.1.1, 11.1.2, 11.2, 11.3.1, 11.3.2")
all_keys = {"11.1.1", "11.1.2", "11.2", "11.3.1", "11.3.2"}
missing = all_keys - set(d["subquestions"].keys())
print("Missing:", sorted(missing))
