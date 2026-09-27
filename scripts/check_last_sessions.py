import sqlite3
conn = sqlite3.connect("data/learner_store/learners.db")
conn.row_factory = sqlite3.Row
rows = conn.execute(
    "SELECT session_id, started_at, ended_at FROM session "
    "WHERE learner_id='tanaka' ORDER BY started_at DESC LIMIT 3"
).fetchall()
for r in rows:
    print(dict(r))
