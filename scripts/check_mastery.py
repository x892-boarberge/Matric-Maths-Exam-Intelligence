import sqlite3

conn = sqlite3.connect("data/learner_store/learners.db")

print("--- columns in mastery ---")
for row in conn.execute("PRAGMA table_info(mastery)"):
    print(row)

print()
print("--- all learner_ids in mastery ---")
for row in conn.execute("SELECT DISTINCT learner_id FROM mastery"):
    print(row)

print()
print("--- rows for tanaka ---")
for row in conn.execute("SELECT * FROM mastery WHERE learner_id='tanaka'"):
    print(row)
