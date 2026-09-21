"""Insert 2025 P1 Q1.1.1 and 1.1.2 into the mapped corpus."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "mapped" / "2025" / "question_topic_map_2025_v2.csv"

df = pd.read_csv(CSV, encoding="utf-8")
print("Before:", len(df), "rows")

# Drop existing rows for 1.1.1 / 1.1.2 if any (idempotent)
df["_sub"] = df["subquestion"].astype(str).str.strip()
df = df[~df["_sub"].isin(["1.1.1", "1.1.2"])].copy()

# Build two new rows matching the existing schema
def make_row(sub, text, marks):
    row = {c: None for c in df.columns if c != "_sub"}
    row["document_id"] = "2025_nov_p1_exam_maths"
    row["year"] = 2025
    row["paper"] = "P1"
    row["document_type"] = "exam"
    row["question_number"] = 1.0
    row["subquestion"] = sub
    row["marks"] = marks
    row["question_text"] = text
    row["topic_v2"] = "ALG"
    row["mapping_method_v2"] = "manual_backfill"
    row["mapping_confidence_v2"] = "high"
    row["signature_id_v2"] = "MANUAL_BACKFILL"
    row["taxonomy_version"] = "v2_caps"
    return row

new_rows = [
    make_row("1.1.1", "1.1.1 Solve for x: (x+5)(x-2)=0", 2),
    make_row("1.1.2", "1.1.2 Solve for x: 5x^2 + 2 = -9x (correct to TWO decimal places)", 4),
]

df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

# Remove helper column
df = df.drop(columns=["_sub"], errors="ignore")

# Sort by question_number then natural subquestion order
def sort_key(s):
    parts = []
    for p in str(s).split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return parts

df["_sort"] = df["subquestion"].apply(sort_key)
df = df.sort_values(["_sort"], kind="stable").drop(columns=["_sort"]).reset_index(drop=True)

df.to_csv(CSV, index=False, encoding="utf-8")
print("After: ", len(df), "rows")

# Show Q1 rows to confirm
q1 = df[df["question_number"] == 1.0]
print()
print("2025 P1 Question 1 rows:")
print(q1[["subquestion", "topic_v2", "marks", "mapping_method_v2"]].to_string(index=False))
