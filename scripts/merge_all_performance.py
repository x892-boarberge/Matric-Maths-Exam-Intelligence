"""Merge all per-year performance CSVs (2014-2019) into one."""
from pathlib import Path
import pandas as pd

DIAG = Path("data/processed/diagnostics")
years = [2014, 2015, 2016, 2017, 2018, 2019]

parts = []
for y in years:
    p = DIAG / ("performance_" + str(y) + ".csv")
    if p.exists():
        df = pd.read_csv(p)
        parts.append(df)
        print(str(y) + ": " + str(len(df)) + " rows")
    else:
        print(str(y) + ": MISSING")

if parts:
    merged = pd.concat(parts, ignore_index=True)
    out = DIAG / "performance_2014_2019.csv"
    merged.to_csv(out, index=False)
    print()
    print("Wrote: " + str(out))
    print("Total rows: " + str(len(merged)))
    print()
    print("By year and paper:")
    print(merged.groupby(["year", "paper"]).size().to_string())
else:
    print("No files found")
