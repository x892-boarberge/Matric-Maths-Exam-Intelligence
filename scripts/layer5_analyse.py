"""
Layer 5 — Analysis: persistence, trends, correlation, emergence.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

ROOT = Path(".").resolve()
DIAG = ROOT / "data" / "processed" / "diagnostics"
OUT = DIAG / "layer5_findings.md"

df = pd.read_csv(DIAG / "diagnostic_errors_enriched.csv")

lines = []
lines.append("# Layer 5 — Analysis Findings (2014–2025)\n")
lines.append(f"**Years:** 12 (2014–2025)  ")
lines.append(f"**Error rows:** {len(df)}  ")
lines.append(f"**Joined with priority:** 100%\n")

# 5a Persistence
lines.append("## 5a — Persistence Analysis\n")
persistence = df.groupby(["topic", "error_class"]).agg(
    years_present=("year", "nunique"),
    total_count=("error_text", "count"),
).reset_index()

def band(n):
    if n >= 10: return "permanent"
    if n >= 6: return "recurring"
    if n >= 3: return "occasional"
    return "rare"

persistence["band"] = persistence["years_present"].apply(band)
persistence = persistence.sort_values(["years_present", "total_count"], ascending=False)
persistence.to_csv(DIAG / "persistence_table.csv", index=False, encoding="utf-8")

lines.append("### Permanent (10+ of 12 years)\n")
lines.append("| Topic | Class | Years | Count |")
lines.append("|---|---|---|---|")
for _, r in persistence[persistence["band"] == "permanent"].iterrows():
    lines.append(f"| {r['topic']} | {r['error_class']} | {r['years_present']} | {r['total_count']} |")

lines.append("\n### Recurring (6–9 years)\n")
lines.append("| Topic | Class | Years | Count |")
lines.append("|---|---|---|---|")
for _, r in persistence[persistence["band"] == "recurring"].iterrows():
    lines.append(f"| {r['topic']} | {r['error_class']} | {r['years_present']} | {r['total_count']} |")

# 5b Trends
lines.append("\n## 5b — Trend Detection\n")
topic_yearly = df.groupby(["year", "topic"]).size().unstack(fill_value=0)
trend_rows = []
for topic in topic_yearly.columns:
    y = topic_yearly[topic].values
    x = np.array(topic_yearly.index.values)
    slope, _, r_value, p_value, _ = stats.linregress(x, y)
    direction = "rising" if slope > 0.3 else ("falling" if slope < -0.3 else "stable")
    trend_rows.append({
        "topic": topic, "slope": round(slope, 3),
        "r_squared": round(r_value**2, 3),
        "p_value": round(p_value, 4),
        "direction": direction,
        "mean_per_year": round(y.mean(), 1),
    })
trend_df = pd.DataFrame(trend_rows).sort_values("slope", ascending=False)
trend_df.to_csv(DIAG / "topic_trends.csv", index=False, encoding="utf-8")

lines.append("| Topic | Mean/year | Slope | Direction | R² | p-value |")
lines.append("|---|---|---|---|---|---|")
for _, r in trend_df.iterrows():
    lines.append(f"| {r['topic']} | {r['mean_per_year']} | {r['slope']} | {r['direction']} | {r['r_squared']} | {r['p_value']} |")

class_yearly = df.groupby(["year", "error_class"]).size().unstack(fill_value=0)
class_trends = []
for cls in class_yearly.columns:
    y = class_yearly[cls].values
    x = np.array(class_yearly.index.values)
    if y.sum() > 10:
        slope, _, r_value, p_value, _ = stats.linregress(x, y)
        direction = "rising" if slope > 0.3 else ("falling" if slope < -0.3 else "stable")
        class_trends.append({
            "class": cls, "slope": round(slope, 3),
            "r_squared": round(r_value**2, 3),
            "p_value": round(p_value, 4),
            "direction": direction,
        })

lines.append("\n### Error class trends\n")
lines.append("| Class | Slope | Direction | R² | p-value |")
lines.append("|---|---|---|---|---|")
for t in sorted(class_trends, key=lambda x: -x["slope"]):
    lines.append(f"| {t['class']} | {t['slope']} | {t['direction']} | {t['r_squared']} | {t['p_value']} |")

# 5c Correlation
lines.append("\n## 5c — Correlation: Error count ↔ Average performance\n")
corr_rows = []
for topic in df["topic"].unique():
    sub = df[df["topic"] == topic]
    py = sub.groupby("year").agg(
        error_count=("error_text", "count"),
        avg_perf=("avg_performance_pct", "mean"),
    ).dropna()
    if len(py) >= 5:
        rho, p = stats.spearmanr(py["error_count"], py["avg_perf"])
        corr_rows.append({
            "topic": topic, "n_years": len(py),
            "spearman_rho": round(rho, 3), "p_value": round(p, 4),
        })
corr_df = pd.DataFrame(corr_rows).sort_values("spearman_rho")
corr_df.to_csv(DIAG / "error_performance_correlation.csv", index=False, encoding="utf-8")

lines.append("Spearman correlation — negative ρ means more errors ⇒ lower performance.\n")
lines.append("| Topic | N years | ρ | p-value | Interpretation |")
lines.append("|---|---|---|---|---|")
for _, r in corr_df.iterrows():
    if r["p_value"] < 0.1 and r["spearman_rho"] < -0.4:
        interp = "**strong**"
    elif r["spearman_rho"] < -0.2:
        interp = "weak"
    else:
        interp = "no clear relation"
    lines.append(f"| {r['topic']} | {r['n_years']} | {r['spearman_rho']} | {r['p_value']} | {interp} |")

# 5d Emergence
lines.append("\n## 5d — Emergence and Resolution\n")
emerge = df.groupby(["topic", "error_class"]).agg(
    first_year=("year", "min"),
    last_year=("year", "max"),
    years_present=("year", "nunique"),
).reset_index()
recent = emerge[emerge["first_year"] >= 2022]
resolved = emerge[(emerge["last_year"] <= 2020) & (emerge["years_present"] >= 2)]

lines.append("### Emergent (first seen 2022+)\n")
if len(recent) > 0:
    lines.append("| Topic | Class | First | Years |")
    lines.append("|---|---|---|---|")
    for _, r in recent.sort_values("first_year").iterrows():
        lines.append(f"| {r['topic']} | {r['error_class']} | {r['first_year']} | {r['years_present']} |")
else:
    lines.append("_None._")

lines.append("\n### Resolved (last seen ≤2020, ≥2 years)\n")
if len(resolved) > 0:
    lines.append("| Topic | Class | Last | Years |")
    lines.append("|---|---|---|---|")
    for _, r in resolved.sort_values("last_year", ascending=False).iterrows():
        lines.append(f"| {r['topic']} | {r['error_class']} | {r['last_year']} | {r['years_present']} |")
else:
    lines.append("_None._")

# 5e Diagram trend
lines.append("\n## 5e — Diagram-assumption trend\n")
diag = df[df["diagram_assumption"] == True].groupby("year").size()
total = df.groupby("year").size()
dd = pd.concat([diag.rename("diag"), total.rename("total")], axis=1).fillna(0)
dd["pct"] = (dd["diag"] / dd["total"] * 100).round(1)
if len(dd) >= 5:
    y = dd["pct"].values
    x = np.array(dd.index.values)
    slope, _, r_value, p_value, _ = stats.linregress(x, y)
    direction = "rising" if slope > 0.1 else ("falling" if slope < -0.1 else "stable")
    lines.append(f"**Slope:** {slope:+.2f}% per year | **Direction:** {direction} | R²: {r_value**2:.3f} | p: {p_value:.4f}\n")

lines.append("| Year | Diag errors | Total | % |")
lines.append("|---|---|---|---|")
for year, r in dd.iterrows():
    lines.append(f"| {year} | {int(r['diag'])} | {int(r['total'])} | {r['pct']}% |")

# 5f Notation
lines.append("\n## 5f — Notation subtype breakdown\n")
notes = df[df["error_class"] == "notation"]
if len(notes) > 0:
    sub = notes.groupby(["topic", "notation_subtype"]).size().reset_index(name="count").dropna()
    sub = sub.sort_values("count", ascending=False)
    lines.append("| Topic | Subtype | Count |")
    lines.append("|---|---|---|")
    for _, r in sub.iterrows():
        lines.append(f"| {r['topic']} | {r['notation_subtype']} | {r['count']} |")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
print()
print(f"Wrote: {OUT}")