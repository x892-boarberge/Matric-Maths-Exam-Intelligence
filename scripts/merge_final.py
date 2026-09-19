from pathlib import Path
import pandas as pd

DIAG = Path("data/processed/diagnostics")
parts = []

manual = DIAG / "performance_2014_2019.csv"
if manual.exists():
    df = pd.read_csv(manual)
    df["source"] = "manual"
    parts.append(df)
    print("Manual 2014-2019: " + str(len(df)))

extracted = DIAG / "diagnostic_performance_extended.csv"
if extracted.exists():
    df = pd.read_csv(extracted)
    df = df.drop(columns=["raw_label"], errors="ignore")
    df["source"] = "extracted"
    parts.append(df)
    print("Extracted 2020-2022: " + str(len(df)))

for year in [2023, 2024, 2025]:
    p = DIAG / ("performance_" + str(year) + ".csv")
    if p.exists():
        df = pd.read_csv(p)
        df["source"] = "manual"
        parts.append(df)
        print(str(year) + ": " + str(len(df)))

if parts:
    merged = pd.concat(parts, ignore_index=True, sort=False)
    out = DIAG / "performance_all_years.csv"
    merged.to_csv(out, index=False)
    print()
    print("Wrote: " + str(out))
    print("Total: " + str(len(merged)))
    print()
    print("By year:")
    print(merged.groupby("year").size().to_string())
