import sqlite3
from pathlib import Path

conn = sqlite3.connect("data/learner_store/learners.db")

print("=== MISCONCEPTION FREQUENCY IN REAL ATTEMPTS ===\n")
print(f"{'Misconception':40} {'Count':>6}")
print("-" * 48)

rows = conn.execute("""
    SELECT misconception_id, COUNT(*) as n
    FROM attempt
    WHERE misconception_id IS NOT NULL
    GROUP BY misconception_id
    ORDER BY n DESC
""").fetchall()

for mid, n in rows:
    print(f"{mid:40} {n:>6}")

print(f"\nTotal distinct misconceptions fired: {len(rows)}")

# Cross-reference with TEACHINGS coverage
from src.tutor.diagnosis import TEACHINGS
covered = set(TEACHINGS.keys())
print("\n=== TOP MISCONCEPTIONS WITHOUT TEACHINGS ===\n")
uncovered_hits = [(m, n) for m, n in rows if m not in covered]
for mid, n in uncovered_hits:
    print(f"{mid:40} {n:>6}  ← no teaching")

conn.close()
