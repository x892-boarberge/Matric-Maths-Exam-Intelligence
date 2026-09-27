import sqlite3
conn = sqlite3.connect("data/learner_store/learners.db")
print("--- tables ---")
for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(r)
print()
print("--- sittings rows (if table exists) ---")
try:
    for r in conn.execute("SELECT * FROM sittings LIMIT 10"):
        print(r)
except Exception as e:
    print("no sittings table:", e)
