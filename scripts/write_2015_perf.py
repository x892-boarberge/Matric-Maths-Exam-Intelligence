import pandas as pd
rows = []
p1 = [(1,60,"ALG"),(2,60,"SEQ"),(3,60,"SEQ"),(4,56,"FUNC"),(5,47,"FUNC"),
      (6,26,"FUNC"),(7,43,"FIN"),(8,52,"CALC"),(9,29,"CALC"),
      (10,22,"CALC"),(11,28,"PROB")]
for q,p,t in p1:
    rows.append({"year":2015,"paper":"P1","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
p2 = [(1,72,"STAT"),(2,33,"STAT"),(3,51,"AGEO"),(4,64,"AGEO"),
      (5,49,"TRIG"),(6,42,"TRIG"),(7,39,"TRIG"),(8,56,"EUCL"),
      (9,28,"EUCL"),(10,38,"EUCL"),(11,29,"EUCL")]
for q,p,t in p2:
    rows.append({"year":2015,"paper":"P2","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
df = pd.DataFrame(rows)
df.to_csv("data/processed/diagnostics/performance_2015.csv", index=False)
print("Wrote", len(df), "rows")
print(df.to_string(index=False))
