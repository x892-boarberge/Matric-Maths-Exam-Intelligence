import pandas as pd
rows = []
p1 = [(1,69,"ALG"),(2,56,"SEQ"),(3,40,"SEQ"),(4,60,"FUNC"),(5,42,"FUNC"),
      (6,44,"FUNC"),(7,40,"FIN"),(8,68,"CALC"),(9,34,"CALC"),
      (10,23,"CALC"),(11,40,"PROB"),(12,33,"PROB")]
for q,p,t in p1:
    rows.append({"year":2024,"paper":"P1","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
p2 = [(1,61,"STAT"),(2,41,"STAT"),(3,57,"AGEO"),(4,62,"AGEO"),
      (5,48,"TRIG"),(6,45,"TRIG"),(7,35,"TRIG"),(8,40,"EUCL"),
      (9,51,"EUCL"),(10,32,"EUCL"),(11,33,"EUCL")]
for q,p,t in p2:
    rows.append({"year":2024,"paper":"P2","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
df = pd.DataFrame(rows)
df.to_csv("data/processed/diagnostics/performance_2024.csv", index=False)
print("Wrote", len(df), "rows")
