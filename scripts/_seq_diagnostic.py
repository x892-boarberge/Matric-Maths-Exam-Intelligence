import json, csv
from pathlib import Path

print("=== SEQUENCES CONTENT DIAGNOSTIC ===\n")

# 1. What's in Q2/Q3 playbooks?
for q in ["Q2", "Q3"]:
    p = Path(f"data/processed/tutor/playbooks/2025_P1_{q}.json")
    if not p.exists():
        print(f"{q}: playbook missing")
        continue
    data = json.loads(p.read_text(encoding="utf-8-sig"))
    subs = data.get("subquestions", {})
    print(f"{q}: {len(subs)} subquestions")
    for sid, sub in subs.items():
        qtext = sub.get("question_text") or sub.get("question") or sub.get("stem") or ""
        print(f"   {sid}: {qtext[:90]}")

# 2. Variant pools for Q2/Q3
print("\nVariant pools for 2.x / 3.x:")
for f in sorted(Path("data/processed/tutor/variant_pools").glob("*_pool.json")):
    name = f.stem.replace("_pool","")
    if name.startswith("2.") or name.startswith("3."):
        data = json.loads(f.read_text(encoding="utf-8-sig"))
        sample = data[0].get("variant_question","")[:80] if data else ""
        print(f"   {name}: {len(data)} variants — {sample}")

# 3. DBE rows for sequences (with year & quote)
print("\nDBE rows for sequences (first 20):")
with open("data/processed/diagnostics/diagnostic_errors_v9.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
seq_rows = [r for r in rows
            if "sequence" in (r.get("topic","")+r.get("error_text","")).lower()
            or "geometric" in r.get("error_text","").lower()
            or "arithmetic" in r.get("error_text","").lower()
            or "series" in r.get("error_text","").lower()]
for r in seq_rows[:20]:
    print(f"   {r.get('year','?')} P{r.get('paper','?')} {r.get('subquestion_ref','?')}: {r.get('error_text','')[:90]}")
print(f"   ... ({len(seq_rows)} total)")
