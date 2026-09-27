import sqlite3
conn = sqlite3.connect("data/learner_store/learners.db")
conn.row_factory = sqlite3.Row

print("--- sessions with attempt counts (tanaka) ---")
rows = conn.execute("""
    SELECT s.session_id, s.started_at, s.skill_id,
           COUNT(a.attempt_id) as attempt_count
    FROM session s
    LEFT JOIN attempt a ON a.session_id = s.session_id
    WHERE s.learner_id = 'tanaka'
    GROUP BY s.session_id
    ORDER BY s.started_at DESC
    LIMIT 15
""").fetchall()
for r in rows:
    print(f"{r['started_at']}  {r['session_id']}  attempts={r['attempt_count']}")

print()
print("--- last 10 attempts for tanaka (with their session) ---")
rows = conn.execute("""
    SELECT attempt_id, session_id, timestamp, error_type, response
    FROM attempt WHERE learner_id='tanaka'
    ORDER BY timestamp DESC LIMIT 10
""").fetchall()
for r in rows:
    resp = (r['response'] or '')[:40]
    print(f"{r['timestamp']}  sess={r['session_id']}  et={r['error_type']!r}  resp={resp!r}")
