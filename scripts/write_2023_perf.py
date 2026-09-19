import pandas as pd
rows = []
p1 = [(1,71,"ALG"),(2,72,"SEQ"),(3,48,"SEQ"),(4,55,"FUNC"),(5,32,"FUNC"),
      (6,48,"FIN"),(7,66,"CALC"),(8,47,"CALC"),(9,26,"CALC"),(10,30,"PROB")]
for q,p,t in p1:
    rows.append({"year":2023,"paper":"P1","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
p2 = [(1,84,"STAT"),(2,50,"STAT"),(3,63,"AGEO"),(4,59,"AGEO"),
      (5,42,"TRIG"),(6,34,"TRIG"),(7,43,"TRIG"),(8,60,"EUCL"),
      (9,44,"EUCL"),(10,18,"EUCL")]
for q,p,t in p2:
    rows.append({"year":2023,"paper":"P2","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
df = pd.DataFrame(rows)
df.to_csv("data/processed/diagnostics/performance_2023.csv", index=False)
print("Wrote", len(df), "rows")
