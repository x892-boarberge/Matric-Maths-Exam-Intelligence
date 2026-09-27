import sqlite3
conn = sqlite3.connect("data/learner_store/learners.db")
print("--- session schema ---")
for r in conn.execute("PRAGMA table_info(session)"):
    print(r)
print()
print("--- session rows ---")
for r in conn.execute("SELECT * FROM session"):
    print(r)
print()
print("--- attempt schema ---")
for r in conn.execute("PRAGMA table_info(attempt)"):
    print(r)
print()
print("--- attempt count for tanaka ---")
for r in conn.execute("SELECT COUNT(*) FROM attempt WHERE learner_id='tanaka'"):
    print(r)
