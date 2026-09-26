import sqlite3
from pathlib import Path

db = Path("data/learner_store/learners.db")
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

print("=== Sessions for tanaka ===")
for r in conn.execute(
    "SELECT session_id, started_at, ended_at, skill_id FROM session "
    "WHERE learner_id = ? ORDER BY started_at DESC LIMIT 20",
    ("tanaka",)
):
    ended = "yes" if r["ended_at"] else "no"
    print(f'  {r["started_at"][:19]}  {r["skill_id"]:35s}  ended={ended}')

print()
print("=== Attempts for tanaka (last 20) ===")
for r in conn.execute(
    "SELECT session_id, skill_id, timestamp, error_type, diagnosis_rule_id "
    "FROM attempt WHERE learner_id = ? ORDER BY timestamp DESC LIMIT 20",
    ("tanaka",)
):
    print(f'  {r["timestamp"][:19]}  {r["skill_id"]:35s}  err={r["error_type"]:12s}  rule={r["diagnosis_rule_id"]}')

print()
print("=== Mastery for tanaka ===")
for r in conn.execute(
    "SELECT skill_id, mastery_state, sittings_passed, last_sitting_at "
    "FROM mastery WHERE learner_id = ?",
    ("tanaka",)
):
    print(f'  {r["skill_id"]:35s}  {r["mastery_state"]:14s}  sittings={r["sittings_passed"]}')

print()
print("=== Totals ===")
n_sess = conn.execute("SELECT COUNT(*) FROM session WHERE learner_id = ?", ("tanaka",)).fetchone()[0]
n_att = conn.execute("SELECT COUNT(*) FROM attempt WHERE learner_id = ?", ("tanaka",)).fetchone()[0]
print(f"  Sessions: {n_sess}")
print(f"  Attempts: {n_att}")