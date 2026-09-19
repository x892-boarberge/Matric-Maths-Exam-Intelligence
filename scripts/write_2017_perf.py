import pandas as pd
rows = []
p1 = [(1,60,"ALG"),(2,63,"SEQ"),(3,18,"SEQ"),(4,51,"FUNC"),(5,49,"FUNC"),
      (6,45,"FIN"),(7,65,"CALC"),(8,40,"CALC"),(9,41,"CALC"),
      (10,9,"PROB"),(11,25,"PROB")]
for q,p,t in p1:
    rows.append({"year":2017,"paper":"P1","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
p2 = [(1,66,"STAT"),(2,64,"STAT"),(3,49,"AGEO"),(4,43,"AGEO"),
      (5,57,"TRIG"),(6,35,"TRIG"),(7,50,"TRIG"),(8,46,"EUCL"),
      (9,34,"EUCL"),(10,34,"EUCL"),(11,41,"EUCL")]
for q,p,t in p2:
    rows.append({"year":2017,"paper":"P2","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
df = pd.DataFrame(rows)
df.to_csv("data/processed/diagnostics/performance_2017.csv", index=False)
print("Wrote", len(df), "rows")
