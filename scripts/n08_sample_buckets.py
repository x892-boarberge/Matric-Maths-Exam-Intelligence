"""Sample error paragraphs inside each permanent bucket for N08 naming."""
import pandas as pd
from pathlib import Path

DIAG = Path("data/processed/diagnostics")
df = pd.read_csv(DIAG / "diagnostic_errors_enriched.csv")

PERMANENT = [
    ("TRIG", "procedural"), ("EUCL", "procedural"), ("AGEO", "procedural"),
    ("FUNC", "general"), ("EUCL", "general"), ("AGEO", "general"),
    ("TRIG", "general"), ("FUNC", "procedural"), ("CALC", "general"),
    ("STAT", "general"), ("STAT", "procedural"), ("ALG", "procedural"),
    ("PROB", "general"), ("SEQ", "procedural"), ("CALC", "notation"),
    ("ALG", "notation"), ("CALC", "procedural"), ("SEQ", "general"),
    ("FIN", "procedural"), ("FIN", "general"), ("SEQ", "notation"),
]

out = []
for topic, cls in PERMANENT:
    sub = df[(df["topic"] == topic) & (df["error_class"] == cls)]
    out.append("=" * 70)
    out.append(f"{topic} / {cls}  ({len(sub)} errors)")
    out.append("=" * 70)
    for _, r in sub.head(5).iterrows():
        out.append(f"  [{r['year']} {r['paper']} Q{r['question_number']}]")
        out.append(f"    {str(r['error_text'])[:280]}")
        if pd.notna(r.get("db_e_intervention")):
            out.append(f"    DBE FIX: {str(r['db_e_intervention'])[:150]}")
        out.append("")
    out.append("")

text = "\n".join(out)
(DIAG / "n08_bucket_samples.txt").write_text(text, encoding="utf-8")
print(f"Wrote {len(text)} chars to n08_bucket_samples.txt")
print()
print(text[:4000])