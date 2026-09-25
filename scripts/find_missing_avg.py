import pandas as pd
from pathlib import Path

DIAG = Path("data/processed/diagnostics")

print("=== All performance* files ===")
for f in sorted(DIAG.glob("performance*")):
    print(f"  {f.name} — {f.stat().st_size} bytes")

print()
print("=== Contents of each per-year file ===")
for f in sorted(DIAG.glob("performance_*.csv")):
    if f.name == "performance_all_years.csv":
        continue
    df = pd.read_csv(f)
    print(f"--- {f.name} ---")
    print(df.to_string())
    print()

print("=== performance_all_years — check for 2020 P1, 2021 P2, 2022 P2 ===")
all_yr = pd.read_csv(DIAG / "performance_all_years.csv")
for yr, paper in [(2020, "P1"), (2021, "P2"), (2022, "P2")]:
    subset = all_yr[(all_yr["year"] == yr) & (all_yr["paper"] == paper)]
    print(f"{yr} {paper}: {len(subset)} rows")
    if len(subset) > 0:
        print(subset.to_string())
    print()

print("=== full 2020, 2021, 2022 from performance_all_years ===")
for yr in [2020, 2021, 2022]:
    subset = all_yr[all_yr["year"] == yr]
    print(f"--- {yr} ({len(subset)} rows) ---")
    print(subset.to_string())
    print()