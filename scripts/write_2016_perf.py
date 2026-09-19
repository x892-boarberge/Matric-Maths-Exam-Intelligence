import pandas as pd
rows = []
p1 = [(1,70,"ALG"),(2,54,"SEQ"),(3,31,"SEQ"),(4,42,"FUNC"),(5,39,"FUNC"),
      (6,27,"FUNC"),(7,50,"FIN"),(8,42,"CALC"),(9,38,"CALC"),
      (10,24,"CALC"),(11,41,"PROB"),(12,69,"PROB")]
for q,p,t in p1:
    rows.append({"year":2016,"paper":"P1","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
p2 = [(1,74,"STAT"),(2,52,"STAT"),(3,59,"AGEO"),(4,69,"AGEO"),
      (5,44,"TRIG"),(6,36,"TRIG"),(7,33,"TRIG"),(8,57,"EUCL"),
      (9,44,"EUCL"),(10,36,"EUCL")]
for q,p,t in p2:
    rows.append({"year":2016,"paper":"P2","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
df = pd.DataFrame(rows)
df.to_csv("data/processed/diagnostics/performance_2016.csv", index=False)
print("Wrote", len(df), "rows")
print(df.to_string(index=False))
