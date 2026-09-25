"""
Layer 4 — Aggregation.
Produce the 4 analysis tables from enriched errors.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(".").resolve()
DIAG = ROOT / "data" / "processed" / "diagnostics"
df = pd.read_csv(DIAG / "diagnostic_errors_enriched.csv")

print(f"Input rows: {len(df)}")
print(f"Years covered: {sorted(df['year'].unique())}")
print()

# Table 1 — topic x year matrix
t1 = df.groupby(["year", "topic"]).agg(
    error_count=("error_text", "count"),
    avg_priority=("avg_performance_pct", "mean"),
).reset_index()
t1_pivot = t1.pivot(index="year", columns="topic", values="error_count").fillna(0).astype(int)
t1_pivot.to_csv(DIAG / "topic_year_matrix.csv", encoding="utf-8")
print("Table 1 — topic_year_matrix.csv")
print(t1_pivot.to_string())
print()

# Table 2 — error_class x year
t2 = df.groupby(["year", "error_class"]).size().unstack(fill_value=0)
t2.to_csv(DIAG / "error_class_year.csv", encoding="utf-8")
print("Table 2 — error_class_year.csv")
print(t2.to_string())
print()

# Table 3 — error_class x topic x year (the peer-reviewed addition)
t3 = df.groupby(["year", "topic", "error_class"]).size().reset_index(name="count")
t3.to_csv(DIAG / "error_class_topic_year.csv", index=False, encoding="utf-8")
print(f"Table 3 — error_class_topic_year.csv ({len(t3)} rows)")
print()

# Table 4 — reading errors yearly
t4 = df[df["error_class"] == "reading"].groupby("year").size().rename("reading_errors")
total = df.groupby("year").size().rename("total_errors")
t4 = pd.concat([t4, total], axis=1).fillna(0).astype(int)
t4["reading_pct"] = (t4["reading_errors"] / t4["total_errors"] * 100).round(1)
t4.to_csv(DIAG / "reading_errors_year.csv", encoding="utf-8")
print("Table 4 — reading_errors_year.csv")
print(t4.to_string())
print()

# Table 5 — diagram assumptions yearly
t5 = df[df["diagram_assumption"] == True].groupby("year").size().rename("diagram_assumption_errors")
t5 = pd.concat([t5, total], axis=1).fillna(0).astype(int)
t5["pct"] = (t5["diagram_assumption_errors"] / t5["total_errors"] * 100).round(1)
t5.to_csv(DIAG / "diagram_assumption_year.csv", encoding="utf-8")
print("Table 5 — diagram_assumption_year.csv")
print(t5.to_string())
print()

# Table 6 — critical errors by topic x year
crit = df[df["priority_band"] == "critical"]
t6 = crit.groupby(["year", "topic"]).size().unstack(fill_value=0)
t6.to_csv(DIAG / "critical_topic_year.csv", encoding="utf-8")
print("Table 6 — critical_topic_year.csv")
print(t6.to_string())
print()

# Table 7 — notation_subtype breakdown
notes = df[df["error_class"] == "notation"]
t7 = notes.groupby(["topic", "notation_subtype"]).size().reset_index(name="count")
t7 = t7.sort_values("count", ascending=False)
t7.to_csv(DIAG / "notation_subtype_breakdown.csv", index=False, encoding="utf-8")
print("Table 7 — notation_subtype_breakdown.csv (top 15)")
print(t7.head(15).to_string())
print()

print("=" * 60)
print("Layer 4 complete. 7 tables written to:", DIAG)
print("=" * 60)