"""B4 ledger amendment: add missing columns, drop demo row, create overdue view.
Non-destructive: ALTER TABLE + DELETE + CREATE VIEW. No table rebuild."""
import sqlite3, sys
from pathlib import Path
from datetime import datetime

db = Path("data/learner_store/learners.db")
backup = db.with_suffix(f".db.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(db.read_bytes())
print(f"Backup: {backup}\n")

conn = sqlite3.connect(db)

# Safety check
cols = [r[1] for r in conn.execute("PRAGMA table_info(hypothesis)")]
if "success_criterion" in cols:
    print("FATAL: migration already applied")
    sys.exit(1)

# 1. Add the 5 missing columns (nullable — enforced by app-level validation)
print("1. Adding columns:")
for col, typ in [
    ("success_criterion", "TEXT"),
    ("evaluate_by",       "TEXT"),
    ("snapshot_id",       "INTEGER"),
    ("analyst_function",  "TEXT"),
    ("args_json",         "TEXT"),
]:
    conn.execute(f"ALTER TABLE hypothesis ADD COLUMN {col} {typ}")
    print(f"   + {col} {typ}")

# 2. Delete demo row
n = conn.execute("DELETE FROM hypothesis WHERE created_by='demo'").rowcount
print(f"\n2. Deleted {n} demo row(s)")

# 3. Indexes
conn.execute("CREATE INDEX IF NOT EXISTS idx_hyp_status ON hypothesis(status)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_hyp_evaluate_by ON hypothesis(evaluate_by)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_hyp_scope_node ON hypothesis(scope_node)")
print("\n3. Created indexes: idx_hyp_status, idx_hyp_evaluate_by, idx_hyp_scope_node")

# 4. Overdue view (the anti-diary mechanism)
conn.executescript("""
    CREATE VIEW IF NOT EXISTS hypotheses_overdue AS
        SELECT hypothesis_id, question, evaluate_by, status, scope_node, created_by
        FROM hypothesis
        WHERE status IN ('proposed','pending_measurement')
          AND evaluate_by IS NOT NULL
          AND evaluate_by < date('now');
""")
print("4. Created hypotheses_overdue view")

conn.commit()

# Verification
print("\n=== VERIFICATION ===")
cols = [r[1] for r in conn.execute("PRAGMA table_info(hypothesis)")]
for needed in ["success_criterion","evaluate_by","snapshot_id","analyst_function","args_json"]:
    print(f"   {'OK' if needed in cols else 'MISSING'}  {needed}")
n = conn.execute("SELECT COUNT(*) FROM hypothesis").fetchone()[0]
demo = conn.execute("SELECT COUNT(*) FROM hypothesis WHERE created_by='demo'").fetchone()[0]
print(f"   Rows in table: {n} (demo: {demo})")
views = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='view'")]
print(f"   Views: {views}")
overdue = conn.execute("SELECT COUNT(*) FROM hypotheses_overdue").fetchone()[0]
print(f"   Overdue hypotheses: {overdue}")

conn.close()
print("\nB4 amendment complete.")
