import csv
from pathlib import Path

path = Path("data/processed/diagnostics/diagnostic_errors_v9.csv")
with open(path, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    print("Fields:", reader.fieldnames)
    print()
    rows = list(reader)

# Sample the actual values in the columns we need
print("=== Distinct 'year' values ===")
years = sorted(set(r.get("year", "") for r in rows))
print(years[:15])

print("\n=== Distinct 'paper' values ===")
papers = sorted(set(r.get("paper", "") for r in rows))
print(papers)

print("\n=== First 5 subquestion_ref values ===")
refs = [r.get("subquestion_ref", "") for r in rows[:5]]
print(refs)

# Now try the 2024 P1 Q1 filter with whatever the format actually is
print("\n=== 2024 P1 Q1 candidates ===")
p1_2024 = [r for r in rows if r.get("year") == "2024" and "1" in str(r.get("paper", ""))]
print(f"Rows found with year=2024: {len(p1_2024)}")
for r in p1_2024[:10]:
    ref = r.get("subquestion_ref", "")
    txt = r.get("error_text", "")[:120]
    print(f"  [{ref}] {txt}")
