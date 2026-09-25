"""
Layer 3 — Enrichment.
Join diagnostic errors with performance averages.
Attach priority band from avg_performance_pct.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(".").resolve()
DIAG = ROOT / "data" / "processed" / "diagnostics"

errors = pd.read_csv(DIAG / "diagnostic_errors_v4.csv")
averages = pd.read_csv(DIAG / "performance_all_years.csv")

# Keep only errors section for enrichment
errs = errors[errors["source_section"] == "errors"].copy()

# Prep averages: ensure year+q+paper keys
averages["question_number"] = averages["question_number"].astype(int)
avg_slim = averages[["year", "paper", "question_number", "avg_performance_pct", "topic_v2"]].copy()
avg_slim = avg_slim.rename(columns={"topic_v2": "avg_topic_v2"})

# Join on year + paper + question
merged = errs.merge(
    avg_slim,
    on=["year", "paper", "question_number"],
    how="left",
)

# Priority band
def band(v):
    if pd.isna(v):
        return "unknown"
    if v < 35:
        return "critical"
    if v < 50:
        return "high"
    if v < 65:
        return "medium"
    return "low"

merged["priority_band"] = merged["avg_performance_pct"].apply(band)

OUT = DIAG / "diagnostic_errors_enriched.csv"
merged.to_csv(OUT, index=False, encoding="utf-8")

print(f"Input errors:  {len(errs)}")
print(f"Enriched rows: {len(merged)}")
print()
print("Join success rate: "
      f"{merged['avg_performance_pct'].notna().sum()} / {len(merged)} "
      f"({100 * merged['avg_performance_pct'].notna().mean():.1f}%)")
print()
print("Priority band distribution:")
print(merged["priority_band"].value_counts().to_string())
print()
print("Critical errors (avg < 35%) by topic:")
crit = merged[merged["priority_band"] == "critical"]
print(crit["topic"].value_counts().to_string())
print()
print("Sample critical error:")
if len(crit) > 0:
    r = crit.iloc[0]
    print(f"  {r['year']} {r['paper']} Q{r['question_number']} [{r['topic']}]")
    print(f"  avg: {r['avg_performance_pct']}%  | class: {r['error_class']}")
    print(f"  {str(r['error_text'])[:250]}")
print()
print(f"Wrote {OUT}")