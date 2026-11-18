"""
Inspect recent attempts for a learner-skill.
Shows raw evidence, interpretation, diagnosis, and decision as stored.
"""
import json
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "learner_store" / "learners.db"

learner_id = sys.argv[1] if len(sys.argv) > 1 else "tanaka"
skill_id   = sys.argv[2] if len(sys.argv) > 2 else "algebra.quadratic.solve"
limit      = int(sys.argv[3]) if len(sys.argv) > 3 else 10

conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT attempt_id, timestamp, response, diagnosis_rule_id, "
    "       misconception_id, error_type, evidence_json "
    "FROM attempt "
    "WHERE learner_id = ? AND skill_id = ? "
    "ORDER BY timestamp DESC LIMIT ?",
    (learner_id, skill_id, limit),
).fetchall()

print(f"Showing {len(rows)} attempts for {learner_id} / {skill_id}")
print()

for r in rows:
    print("=" * 72)
    print(f"{r['timestamp']}  {r['attempt_id']}")
    print(f"  top-level:  response={r['response']!r}")
    print(f"              rule={r['diagnosis_rule_id']!r} "
          f"error_type={r['error_type']!r} "
          f"misconception={r['misconception_id']!r}")

    if not r["evidence_json"]:
        print("  <<no evidence_json — Claim 1 FAILS for this attempt>>")
        continue

    ev = json.loads(r["evidence_json"])
    raw    = ev.get("raw") or {}
    interp = ev.get("interpretation")
    diag   = ev.get("diagnosis")
    dec    = ev.get("decision")

    print(f"  RAW        qid={raw.get('question_id')!r} "
          f"skill={raw.get('skill_id')!r}")
    print(f"             lines={raw.get('learner_lines')}")
    print(f"             final={raw.get('final_answer')!r} "
          f"count={raw.get('line_count')}")

    if interp:
        print(f"  INTERP     kind={interp.get('match_kind')!r} "
              f"matcher={interp.get('matcher')!r} "
              f"conf={interp.get('confidence')}")
        print(f"             expected={interp.get('expected_answer')!r}")
    else:
        print("  INTERP     <<MISSING>>")

    if diag:
        print(f"  DIAGNOSIS  mid={diag.get('misconception_id')!r} "
              f"rule={diag.get('rule_id')!r} "
              f"kind={diag.get('kind')!r}")
    elif diag is None:
        print("  DIAGNOSIS  (none)")
    else:
        print(f"  DIAGNOSIS  {diag}")

    if dec:
        print(f"  DECISION   action={dec.get('action')!r} "
              f"reason={dec.get('reason')!r}")
    else:
        print("  DECISION   <<MISSING>>")

conn.close()
