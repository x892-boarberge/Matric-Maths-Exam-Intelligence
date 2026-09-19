import pandas as pd
rows = []
p1 = [(1,70,"ALG"),(2,58,"SEQ"),(3,50,"SEQ"),(4,49,"FUNC"),(5,44,"FUNC"),
      (6,37,"FUNC"),(7,52,"FIN"),(8,53,"CALC"),(9,32,"CALC"),
      (10,39,"CALC"),(11,29,"PROB"),(12,29,"PROB")]
for q,p,t in p1:
    rows.append({"year":2014,"paper":"P1","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
p2 = [(1,69,"STAT"),(2,61,"STAT"),(3,57,"AGEO"),(4,57,"AGEO"),
      (5,42,"TRIG"),(6,34,"TRIG"),(7,37,"TRIG"),(8,59,"EUCL"),
      (9,38,"EUCL"),(10,34,"EUCL")]
for q,p,t in p2:
    rows.append({"year":2014,"paper":"P2","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
df = pd.DataFrame(rows)
df.to_csv("data/processed/diagnostics/performance_2014.csv", index=False)
print("Wrote", len(df), "rows")
