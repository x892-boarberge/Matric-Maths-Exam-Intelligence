import json, sqlite3, sys
from pathlib import Path

# ============================================================
# 1. DISCOVER — what sequence skill_ids actually exist?
# ============================================================
print("=== Discovering sequence skill_ids ===\n")

db = sqlite3.connect(r"data/learner_store/learners.db")
rows = db.execute("""
    SELECT DISTINCT skill_id FROM attempt
    WHERE skill_id LIKE '%seq%'
       OR question_id LIKE '%Q2%'
       OR question_id LIKE '%Q3%'
""").fetchall()
found_skills = [r[0] for r in rows]

# Filter to actual sequence skills (ignore Q2/Q3 of other topics)
seq_skills = [s for s in found_skills if 'seq' in s.lower()]
print(f"Sequence skills in attempt table: {seq_skills if seq_skills else 'NONE'}")

# Also check diagnostic rows for SEQ topic
import csv
with open("data/processed/diagnostics/diagnostic_errors_v9.csv", encoding="utf-8-sig") as f:
    diag = list(csv.DictReader(f))
seq_rows = [r for r in diag if r.get("topic", "").upper() in ("SEQ", "PATTERNS")]
print(f"DBE diagnostic rows for SEQ: {len(seq_rows)}")

# Show 8 sample DBE patterns to inform teaching
print("\n=== Sample DBE sequence errors ===")
seen = set()
count = 0
for r in seq_rows:
    text = (r.get("error_text") or "").strip() or (r.get("suggestion_text") or "").strip()
    if not text or text in seen:
        continue
    seen.add(text)
    count += 1
    print(f"  [{r.get('year','?')} Q{r.get('question_number','?')}] {text[:180]}")
    if count >= 8:
        break
