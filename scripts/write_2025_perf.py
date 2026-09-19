import pandas as pd
rows = []
p1 = [(1,67),(2,53),(3,69),(4,58),(5,53),(6,14),(7,39),(8,81),(9,40),(10,25),(11,25)]
for q,p in p1:
    rows.append({"year":2025,"paper":"P1","question_number":q,"avg_performance_pct":p})
p2 = [(1,74),(2,40),(3,70),(4,53),(5,58),(6,33),(7,36),(8,41),(9,70),(10,52),(11,29)]
for q,p in p2:
    rows.append({"year":2025,"paper":"P2","question_number":q,"avg_performance_pct":p})
df = pd.DataFrame(rows)
df.to_csv("data/processed/diagnostics/performance_2025.csv", index=False)
print("Wrote", len(df), "rows")
