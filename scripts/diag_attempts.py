import sqlite3
conn = sqlite3.connect("data/learner_store/learners.db")
conn.row_factory = sqlite3.Row

print("--- last 5 sessions for tanaka ---")
sessions = conn.execute(
    "SELECT session_id, started_at, skill_id FROM session "
    "WHERE learner_id='tanaka' ORDER BY started_at DESC LIMIT 5"
).fetchall()
for s in sessions:
    print(dict(s))

print()
print("--- attempts in most recent session ---")
if sessions:
    sid = sessions[0]["session_id"]
    attempts = conn.execute(
        "SELECT attempt_id, timestamp, error_type, response "
        "FROM attempt WHERE session_id=? ORDER BY timestamp", (sid,)
    ).fetchall()
    print(f"session: {sid}")
    print(f"attempt count: {len(attempts)}")
    for a in attempts:
        print(f"  error_type={a['error_type']!r}  response={a['response']!r}")

print()
print("--- distinct error_type values for tanaka ---")
for r in conn.execute(
    "SELECT error_type, COUNT(*) FROM attempt "
    "WHERE learner_id='tanaka' GROUP BY error_type"
):
    print(dict(r))
