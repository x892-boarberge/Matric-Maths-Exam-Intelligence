import csv
from pathlib import Path
from collections import Counter

path = Path("data/processed/diagnostics/diagnostic_errors_v9.csv")
print(f"File: {path.name}  Size: {path.stat().st_size} bytes\n")

with open(path, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    cols = reader.fieldnames
    rows = list(reader)

print(f"Columns: {cols}\n")
print(f"Total rows: {len(rows)}\n")

# Filter for functions/log mentions across all text columns
def has_log(row):
    text = " ".join(str(v).lower() for v in row.values() if v)
    return "log" in text or "function" in text or "inverse" in text

log_rows = [r for r in rows if has_log(r)]
print(f"Rows mentioning log/function/inverse: {len(log_rows)}\n")

# Show first 10 rows with full detail
if log_rows:
    print("=" * 70)
    print("Sample rows (first 10)")
    print("=" * 70)
    for i, r in enumerate(log_rows[:10], 1):
        print(f"\n--- Row {i} ---")
        for k, v in r.items():
            if v and str(v).strip():
                v_str = str(v).strip()
                if len(v_str) > 300:
                    v_str = v_str[:300] + "..."
                print(f"  {k}: {v_str}")

# Aggregate by year and question
print("\n" + "=" * 70)
print("Years covered")
print("=" * 70)
years = Counter()
for r in log_rows:
    for col in ["year", "Year", "YEAR", "exam_year"]:
        if col in r and r[col]:
            years[r[col]] += 1
            break
if years:
    for y in sorted(years):
        print(f"  {y}: {years[y]} rows")
else:
    print("  (no year column recognized — check column names above)")
