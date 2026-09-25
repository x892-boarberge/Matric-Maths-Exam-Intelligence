"""Add the 32 missing averages — corrected values from user verification."""
import pandas as pd
from pathlib import Path

DIAG = Path("data/processed/diagnostics")
df = pd.read_csv(DIAG / "performance_all_years.csv")

new_rows = [
    # 2020 P1
    (2020, "P1", 1, 72, "ALG"), (2020, "P1", 2, 66, "SEQ"),
    (2020, "P1", 3, 40, "SEQ"), (2020, "P1", 4, 55, "FUNC"),
    (2020, "P1", 5, 45, "FUNC"), (2020, "P1", 6, 48, "FIN"),
    (2020, "P1", 7, 66, "CALC"), (2020, "P1", 8, 39, "CALC"),
    (2020, "P1", 9, 25, "CALC"), (2020, "P1", 10, 30, "PROB"),
    (2020, "P1", 11, 18, "PROB"),
    # 2021 P2
    (2021, "P2", 1, 75, "STAT"), (2021, "P2", 2, 75, "STAT"),
    (2021, "P2", 3, 57, "AGEO"), (2021, "P2", 4, 43, "AGEO"),
    (2021, "P2", 5, 57, "TRIG"), (2021, "P2", 6, 21, "TRIG"),
    (2021, "P2", 7, 36, "TRIG"), (2021, "P2", 8, 40, "EUCL"),
    (2021, "P2", 9, 56, "EUCL"), (2021, "P2", 10, 24, "EUCL"),
    (2021, "P2", 11, 34, "EUCL"),
    # 2022 P2
    (2022, "P2", 1, 72, "STAT"), (2022, "P2", 2, 49, "STAT"),
    (2022, "P2", 3, 66, "AGEO"), (2022, "P2", 4, 48, "AGEO"),
    (2022, "P2", 5, 40, "TRIG"), (2022, "P2", 6, 29, "TRIG"),
    (2022, "P2", 7, 35, "TRIG"), (2022, "P2", 8, 55, "EUCL"),
    (2022, "P2", 9, 37, "EUCL"), (2022, "P2", 10, 18, "EUCL"),
]

new_df = pd.DataFrame(new_rows, columns=["year", "paper", "question_number", "avg_performance_pct", "topic_v2"])
new_df["source"] = "extracted_graph"
new_df["source_page"] = None

existing_keys = set(zip(df["year"], df["paper"], df["question_number"]))
new_df = new_df[~new_df.apply(lambda r: (r["year"], r["paper"], r["question_number"]) in existing_keys, axis=1)]

combined = pd.concat([df, new_df], ignore_index=True)
combined = combined.sort_values(["year", "paper", "question_number"]).reset_index(drop=True)
combined.to_csv(DIAG / "performance_all_years.csv", index=False, encoding="utf-8")

print(f"Before: {len(df)} rows")
print(f"Added:  {len(new_df)} new rows")
print(f"After:  {len(combined)} rows")
print()
for yr, paper in [(2020, "P1"), (2021, "P2"), (2022, "P2")]:
    subset = combined[(combined["year"] == yr) & (combined["paper"] == paper)]
    print(f"=== {yr} {paper} ({len(subset)} rows) ===")
    print(subset[["question_number", "avg_performance_pct", "topic_v2"]].to_string(index=False))
    print()