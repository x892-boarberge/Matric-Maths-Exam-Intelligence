import os
from pathlib import Path

path = Path("data/processed/diagrams/pages/2025_P1_p05.png")
print(f"Path: {path.resolve()}")
print(f"Exists: {path.exists()}")
print(f"Size: {path.stat().st_size / 1024:.1f} KB")

try:
    os.startfile(str(path.resolve()))
    print("os.startfile: returned without exception")
    print("(If viewer opened: Bug B — message misleading, file opens fine)")
    print("(If nothing happened: Bug A — startfile silent failure)")
except Exception as e:
    print(f"os.startfile: FAILED — {type(e).__name__}: {e}")
    print("(Bug A confirmed — startfile itself throwing)")
