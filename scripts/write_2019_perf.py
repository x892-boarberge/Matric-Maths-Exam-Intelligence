import pandas as pd
rows = []
p1 = [(1,64,"ALG"),(2,70,"SEQ"),(3,33,"SEQ"),(4,55,"FUNC"),(5,52,"FUNC"),
      (6,57,"FIN"),(7,62,"CALC"),(8,39,"CALC"),(9,42,"CALC"),
      (10,21,"PROB"),(11,26,"PROB")]
for q,p,t in p1:
    rows.append({"year":2019,"paper":"P1","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
p2 = [(1,75,"STAT"),(2,53,"STAT"),(3,69,"AGEO"),(4,47,"AGEO"),
      (5,37,"TRIG"),(6,30,"TRIG"),(7,34,"TRIG"),(8,49,"EUCL"),
      (9,44,"EUCL"),(10,44,"EUCL")]
for q,p,t in p2:
    rows.append({"year":2019,"paper":"P2","question_number":q,
                 "avg_performance_pct":p,"topic_v2":t})
df = pd.DataFrame(rows)
df.to_csv("data/processed/diagnostics/performance_2019.csv", index=False)
print("Wrote", len(df), "rows")
