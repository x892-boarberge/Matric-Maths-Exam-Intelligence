import csv
import sqlite3
from pathlib import Path

# 1. What finance skill_ids exist in the DB?
print("=== 1. Finance skill_ids in attempt table ===")
conn = sqlite3.connect(r"data/learner_store/learners.db")
rows = conn.execute(
    "SELECT DISTINCT skill_id FROM attempt WHERE skill_id LIKE '%fin%' OR skill_id LIKE '%Q7%'"
).fetchall()
if rows:
    for r in rows:
        print(f"  {r[0]}")
else:
    print("  NONE — finance namespace doesn't exist yet")

# 2. What finance rows are in the DBE diagnostic corpus?
print("\n=== 2. DBE diagnostic rows for finance (FIN topic) ===")
with open("data/processed/diagnostics/diagnostic_errors_v9.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fin_rows = [r for r in reader if r.get("topic", "").upper() == "FIN"]

print(f"  Total finance rows in DBE: {len(fin_rows)}\n")
# Show first 15 unique error/suggestion texts
seen = set()
count = 0
for r in fin_rows:
    err = (r.get("error_text") or "").strip()
    sug = (r.get("suggestion_text") or "").strip()
    text = err or sug
    if not text or text in seen:
        continue
    seen.add(text)
    count += 1
    year = r.get("year", "?")
    q = r.get("question_number", "?")
    print(f"  [{year} Q{q}] {text[:200]}")
    if count >= 15:
        break

# 3. What's in 2025_P1_Q7.json (existing playbook)?
print("\n=== 3. Existing 2025_P1_Q7.json subquestions ===")
import json
q7 = json.loads(Path("data/processed/tutor/playbooks/2025_P1_Q7.json").read_text(encoding="utf-8-sig"))
for k in sorted(q7["subquestions"].keys()):
    sq = q7["subquestions"][k]
    print(f"  {k}: {sq.get('variant_question', '')[:80]}")
