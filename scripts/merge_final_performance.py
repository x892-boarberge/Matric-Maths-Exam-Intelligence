"""Merge all performance data into one CSV."""
from pathlib import Path
import pandas as pd

DIAG = Path("data/processed/diagnostics")
parts = []

manual = DIAG / "performance_2014_2019.csv"
if manual.exists():
    df = pd.read_csv(manual)
    df["source"] = "manual"
    parts.append(df)
    print("Manual 2014-2019: " + str(len(df)) + " rows")

extracted = DIAG / "diagnostic_performance_extended.csv"
if extracted.exists():
    df = pd.read_csv(extracted)
    df = df.drop(columns=["raw_label"], errors="ignore")
    df["source"] = "extracted"
    parts.append(df)
    print("Extracted 2020-2022: " + str(len(df)) + " rows")

v1 = DIAG / "diagnostic_performance_v1.csv"
if v1.exists():
    df = pd.read_csv(v1)
    df = df[df["avg_performance_pct"].notna()].copy()
    keep = ["year", "paper", "question_number", "avg_performance_pct"]
    df = df[[c for c in keep if c in df.columns]]
    df["source"] = "v1_2023_2025"
    parts.append(df)
    print("V1 2023-2025: " + str(len(df)) + " rows")

if parts:
    merged = pd.concat(parts, ignore_index=True, sort=False)
    out = DIAG / "performance_all_years.csv"
    merged.to_csv(out, index=False)
    print()
    print("Wrote: " + str(out))
    print("Total rows: " + str(len(merged)))
    print()
    print("By year:")
    print(merged.groupby("year").size().to_string())
