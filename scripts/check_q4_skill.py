import sqlite3
from pathlib import Path

db = Path("data/learner_store/learners.db")
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row

print("=== Recent Q4.1 attempts — what skill_id? ===")
rows = conn.execute(
    "SELECT question_id, skill_id, timestamp FROM attempt "
    "WHERE question_id LIKE '%4.1%' ORDER BY timestamp DESC LIMIT 10"
).fetchall()

if not rows:
    print("  NO ATTEMPTS FOUND for any %4.1% question_id")
    print("  (This means the attempt wasn't stored — separate issue)")
else:
    for r in rows:
        print(f"  {r['question_id']}  ->  skill_id={r['skill_id']!r}")

print()
print("=== Distinct skill_ids overall ===")
rows2 = conn.execute(
    "SELECT DISTINCT skill_id FROM attempt ORDER BY skill_id"
).fetchall()
for r in rows2:
    print(f"  {r['skill_id']!r}")

conn.close()
