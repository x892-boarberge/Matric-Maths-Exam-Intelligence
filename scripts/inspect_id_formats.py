import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- question_structure.csv ---
qs = ROOT / "data" / "processed" / "questions" / "question_structure.csv"
print(f"--- {qs.name} ---")
if qs.exists():
    with open(qs, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print("Columns:", reader.fieldnames)
        for i, row in enumerate(reader):
            if i < 5:
                print(dict(row))
            else:
                break
else:
    print("NOT FOUND")
    # walk for it
    for p in ROOT.rglob("question_structure.csv"):
        print("  found at:", p)

# --- memo_answers dir ---
ma_dir = ROOT / "data" / "processed" / "memo_answers"
print(f"\n--- {ma_dir.name}/ ---")
if ma_dir.exists():
    for p in sorted(ma_dir.iterdir()):
        print(" ", p.name)

# --- 2023 P1 memo answers ---
ma = ma_dir / "memo_answers_2023_P1.csv"
print(f"\n--- {ma.name} ---")
if ma.exists():
    with open(ma, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print("Columns:", reader.fieldnames)
        for i, row in enumerate(reader):
            if i < 5:
                print(dict(row))
            else:
                break
else:
    print("NOT FOUND")
