import sys, sqlite3, json
from pathlib import Path
sys.path.insert(0, '.')

print("=== PART 9 AUDIT — 2026-11-09 ===\n")
conn = sqlite3.connect("data/learner_store/learners.db")

# 1. Hypothesis schema (B4 amendment check)
print("1. Hypothesis table — B4 ledger amendment status:")
cols = [r[1] for r in conn.execute("PRAGMA table_info(hypothesis)")]
print(f"   Columns: {cols}")
for needed in ["success_criterion", "evaluate_by", "snapshot_id", "analyst_function", "args_json"]:
    print(f"   {'OK' if needed in cols else 'MISSING'}  {needed}")

# 2. Demo rows in live DB
if "created_by" in cols:
    n = conn.execute("SELECT COUNT(*) FROM hypothesis WHERE created_by='demo'").fetchone()[0]
    print(f"\n2. Demo hypotheses in live DB: {n}")

# 3. Overdue view
views = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='view'")]
print(f"\n3. Views: {views}")
print(f"   {'OK' if 'hypotheses_overdue' in views else 'MISSING'}  hypotheses_overdue")

# 4. Pool thinness
print("\n4. Pool counts (thin pools):")
for pool in ["4.2", "4.4"]:
    p = Path(f"data/processed/tutor/variant_pools/{pool}_pool.json")
    if p.exists():
        n = len(json.loads(p.read_text(encoding='utf-8-sig')))
        print(f"   {pool}: {n} variants {'THIN' if n < 30 else 'OK'}")

# 5. Diagram status
print("\n5. Diagram status across pools:")
counts = {"rendered": 0, "partial": 0, "skipped": 0, "not_required": 0}
for f in Path("data/processed/tutor/variant_pools").glob("*_pool.json"):
    data = json.loads(f.read_text(encoding='utf-8-sig'))
    for v in data:
        s = v.get("diagram_status") or v.get("diagram") or "skipped"
        if s in counts: counts[s] += 1
        else: counts["skipped"] += 1
print(f"   {counts}")

# 6. Sequences skills in RULES
print("\n6. Sequences skills in RULES:")
from src.tutor.diagnosis import RULES
seq = [s for s in sorted(RULES) if s.startswith("sequences.")]
if seq:
    for s in seq:
        print(f"   OK  {s} ({len(RULES[s])} rules)")
else:
    print("   NONE")

# 7. Skills actually attempted in Q2/Q3
print("\n7. Skill_ids attempted in Q2/Q3:")
rows = conn.execute("SELECT DISTINCT skill_id FROM attempt WHERE question_id LIKE '%Q2%' OR question_id LIKE '%Q3%'").fetchall()
for r in rows: print(f"   {r[0]}")
if not rows: print("   (no attempts yet)")

# 8. DBE rows for sequences
print("\n8. DBE sequences rows:")
import csv
with open("data/processed/diagnostics/diagnostic_errors_v9.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
seq_rows = [r for r in rows if "sequence" in (r.get("topic","")+r.get("error_text","")).lower()
            or "terms" in r.get("error_text","").lower() or "series" in r.get("error_text","").lower()]
print(f"   {len(seq_rows)} rows matched 'sequence|terms|series' in topic/error")

conn.close()
