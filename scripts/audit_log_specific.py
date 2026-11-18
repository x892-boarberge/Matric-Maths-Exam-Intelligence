import csv
from pathlib import Path
from collections import Counter

path = Path("data/processed/diagnostics/diagnostic_errors_v9.csv")
with open(path, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# Filter FUNC topic with log/inverse/asymptote in error_text or suggestion_text
targets = []
for r in rows:
    text = ((r.get("error_text") or "") + " " + (r.get("suggestion_text") or "")).lower()
    if "log" in text or "inverse" in text or "asymptote" in text:
        targets.append(r)

print(f"Rows mentioning log/inverse/asymptote: {len(targets)}\n")

# Group by subquestion_ref
by_subq = Counter()
for r in targets:
    sq = r.get("subquestion_ref") or "unknown"
    by_subq[sq] += 1
print("By subquestion_ref:")
for k, v in by_subq.most_common(15):
    print(f"  {k}: {v}")

# Show all rows, dedupe by error_text
print("\n" + "=" * 70)
print("All unique DBE statements about log/inverse/asymptote")
print("=" * 70)

seen = set()
for r in targets:
    year = r.get("year", "?")
    q = r.get("question_number", "?")
    sq = r.get("subquestion_ref", "")
    err = (r.get("error_text") or "").strip()
    sug = (r.get("suggestion_text") or "").strip()
    key = err or sug
    if not key or key in seen:
        continue
    seen.add(key)
    print(f"\n[{year} P1 Q{q}{'.'+sq if sq else ''}]")
    if err:
        print(f"  ERROR: {err}")
    if sug:
        print(f"  SUGGEST: {sug}")

print(f"\n\nTotal unique statements: {len(seen)}")
