"""
Generate intervention_specification_v1.csv rows for the 69
misconceptions in misconceptions_v2.csv.
Preserves existing rows, adds new ones.
"""
import pandas as pd
from pathlib import Path

TUTOR = Path("data/processed/tutor")
INTERVENTION_DIR = Path("data/processed/intervention")
INTERVENTION_DIR.mkdir(parents=True, exist_ok=True)

NEW = pd.read_csv(TUTOR / "misconceptions_v2.csv")
MASTER_PATH = INTERVENTION_DIR / "intervention_specification_v1.csv"

# Preserve existing rows
if MASTER_PATH.exists():
    existing = pd.read_csv(MASTER_PATH)
    existing_ids = set(existing["misconception_id"].astype(str).str.strip())
    print(f"Existing rows: {len(existing)}")
else:
    existing = pd.DataFrame(columns=["intervention_id", "topic", "misconception_id", "intervention_pattern"])
    existing_ids = set()
    print("No existing file — starting fresh")

# Map error_class -> intervention_pattern
CLASS_TO_PATTERN = {
    "procedural":   "IP_STEP_ISOLATION",
    "conceptual":   "IP_MISCONCEPTION_CONTRAST",
    "notation":     "IP_REPRESENTATION_SHIFT",
    "presentation": "IP_SELF_EXPLANATION",
    "reading":      "IP_SELF_EXPLANATION",
    "arithmetic":   "IP_STEP_ISOLATION",
}

# Topic label mapping (expand short codes to full names)
TOPIC_LABEL = {
    "ALG": "Algebra & Equations",
    "SEQ": "Sequences & Series",
    "FUNC": "Functions & Graphs",
    "FIN": "Finance",
    "CALC": "Calculus",
    "PROB": "Probability",
    "STAT": "Statistics",
    "TRIG": "Trigonometry",
    "AGEO": "Analytical Geometry",
    "EUCL": "Euclidean Geometry",
    "GEN": "General",
}

# Count per topic for sequential IDs
topic_counters = {}

new_rows = []
for _, row in NEW.iterrows():
    mid = str(row["misconception_id"]).strip()
    if mid in existing_ids:
        continue

    topic = str(row["topic"]).strip()
    topic_counters[topic] = topic_counters.get(topic, 0) + 1
    seq = topic_counters[topic]

    # Build a stable intervention_id
    iid = f"N08_{topic}_{seq:03d}"

    pattern = CLASS_TO_PATTERN.get(str(row["error_class"]).strip(), "IP_GENERIC_PROMPT")
    topic_full = TOPIC_LABEL.get(topic, topic)

    new_rows.append({
        "intervention_id": iid,
        "topic": topic_full,
        "misconception_id": mid,
        "intervention_pattern": pattern,
        "status": "active",
    })

if new_rows:
    new_df = pd.DataFrame(new_rows)
    combined = pd.concat([existing, new_df], ignore_index=True)
    combined.to_csv(MASTER_PATH, index=False, encoding="utf-8")
    print(f"Added {len(new_rows)} rows")
    print(f"Total rows now: {len(combined)}")
else:
    print("No new rows to add")

print()
print("Sample new rows:")
for r in new_rows[:5]:
    print(f"  {r['intervention_id']}  {r['misconception_id']:40s}  {r['intervention_pattern']}")
print()
print("Intervention pattern distribution:")
print(pd.DataFrame(new_rows)["intervention_pattern"].value_counts().to_string())