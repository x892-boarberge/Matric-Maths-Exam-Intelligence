import pandas as pd
rows = []
p1 = [(1,71,"ALG"),(2,70,"SEQ"),(3,48,"SEQ"),(4,59,"FUNC"),(5,55,"FUNC"),
      (6,45,"FUNC"),(7,50,"FIN"),(8,67,"CALC"),(9,38,"CALC"),
      (10,18,"CALC"),(11,34,"PROB"),(12,31,"PROB")]
for q,p,t in p1:
    rows.append({"year":2018,"paper":"P1","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
p2 = [(1,60,"STAT"),(2,48,"STAT"),(3,55,"AGEO"),(4,52,"AGEO"),
      (5,43,"TRIG"),(6,41,"TRIG"),(7,38,"TRIG"),(8,61,"EUCL"),
      (9,49,"EUCL"),(10,31,"EUCL")]
for q,p,t in p2:
    rows.append({"year":2018,"paper":"P2","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
df = pd.DataFrame(rows)
df.to_csv("data/processed/diagnostics/performance_2018.csv", index=False)
print("Wrote", len(df), "rows")
