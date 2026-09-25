import pandas as pd
from pathlib import Path

ROOT = Path(".").resolve()
DIAG = ROOT / "data" / "processed" / "diagnostics"

merged = pd.read_csv(DIAG / "diagnostic_errors_enriched.csv")
averages = pd.read_csv(DIAG / "performance_all_years.csv")

# Which years have nulls?
nulls = merged[merged["avg_performance_pct"].isna()]
print("=== NULL avg_performance_pct by year ===")
print(nulls.groupby("year").size().to_string())
print()
print("=== NULL by year+paper+question ===")
print(nulls.groupby(["year", "paper", "question_number"]).size().to_string())
print()
print("=== Which (year, paper, question_number) keys are missing from averages? ===")
avg_keys = set(zip(averages["year"], averages["paper"], averages["question_number"].astype(int)))
missing_keys = set(zip(nulls["year"], nulls["paper"], nulls["question_number"]))
print(f"Missing keys: {len(missing_keys)}")
for k in sorted(missing_keys)[:30]:
    print(f"  {k}")
print()
print("=== Years present in averages file ===")
print(sorted(averages["year"].unique()))
print()
print("=== 2015 rows in averages ===")
print(averages[averages["year"] == 2015].to_string())
print()
print("=== 2018 rows in averages ===")
print(averages[averages["year"] == 2018].to_string())