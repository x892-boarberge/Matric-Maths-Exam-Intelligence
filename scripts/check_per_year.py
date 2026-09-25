import pandas as pd
from pathlib import Path

DIAG = Path("data/processed/diagnostics")

for yr in [2020, 2021, 2022]:
    f = DIAG / f"performance_{yr}.csv"
    if f.exists():
        df = pd.read_csv(f)
        print(f"=== {f.name} ===")
        print(df.to_string())
        print()