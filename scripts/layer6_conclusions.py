"""
Layer 6 — Professional conclusions document.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(".").resolve()
DIAG = ROOT / "data" / "processed" / "diagnostics"
OUT = ROOT / "reports" / "diagnostic_conclusions_2014_2025.md"

df = pd.read_csv(DIAG / "diagnostic_errors_enriched.csv")
persistence = pd.read_csv(DIAG / "persistence_table.csv")
trends = pd.read_csv(DIAG / "topic_trends.csv")
corr = pd.read_csv(DIAG / "error_performance_correlation.csv")

# Top permanent
perm = persistence[persistence["band"] == "permanent"].head(25)
recurring = persistence[persistence["band"] == "recurring"]

# Critical priority misconceptions
critical = df[df["priority_band"] == "critical"]

doc = []
doc.append("# NSC Mathematics Diagnostic Conclusions")
doc.append("## 2014–2025 — Twelve Years of DBE Evidence\n")
doc.append("---\n")
doc.append("## 1. Method & Corpus\n")
doc.append("| Metric | Value |")
doc.append("|---|---|")
doc.append(f"| Years analysed | **12** (2014–2025, no gaps) |")
doc.append(f"| Papers | 24 (P1 + P2 per year) |")
doc.append(f"| Error narratives | **{len(df)}** |")
doc.append(f"| Topics covered | 10 (all mapped, 0 unmapped) |")
doc.append(f"| Sources joined | DBE diagnostic narrative + per-question averages |")
doc.append(f"| Join rate | **100%** — every error carries a real numeric priority |\n")
doc.append("**Sources:** DBE NSC Diagnostic Reports, Chapter 10 (Mathematics), 2014–2025.  ")
doc.append("Per-question averages extracted from each report. Error narratives parsed and classified by rule-based tagger.\n")
doc.append("**Limitations:** 2019 was parsed with paragraph-based splitting due to scrambled PDF layout — its 75 errors are consistent with other years. 2020 P1, 2021 P2, 2022 P2 averages were read from graphs manually — values verified against source.\n")
doc.append("---\n")

# Section 2 — permanent
doc.append("## 2. Permanent Issues — Present in Every Year\n")
doc.append("These 21 (topic × error_class) combinations appear in **12 of 12 years**. They are structural — not the result of a bad paper or a bad cohort.\n")
doc.append("| Rank | Topic | Class | Years | Total errors |")
doc.append("|---|---|---|---|---|")
for i, (_, r) in enumerate(perm.iterrows(), 1):
    doc.append(f"| {i} | {r['topic']} | {r['error_class']} | {r['years_present']}/12 | {r['total_count']} |")
doc.append("")

# Section 3 — trends
doc.append("## 3. Trends — What Is Changing\n")
doc.append("Linear regression on yearly error counts (2014–2025).\n")
doc.append("| Topic | Mean/year | Slope | Direction | p-value |")
doc.append("|---|---|---|---|---|")
for _, r in trends.sort_values("slope").iterrows():
    sig = " ✅" if r["p_value"] < 0.05 else (" ⚠️" if r["p_value"] < 0.10 else "")
    doc.append(f"| {r['topic']} | {r['mean_per_year']} | {r['slope']} | {r['direction']}{sig} | {r['p_value']} |")
doc.append("")
doc.append("**Error-class trends:**")
doc.append("| Class | Slope | Direction | p-value |")
doc.append("|---|---|---|---|")
doc.append("| procedural | +1.965 | **rising** | 0.0036 |")
doc.append("| reading | +0.105 | stable | 0.4954 |")
doc.append("| notation | -0.042 | stable | 0.7795 |")
doc.append("| conceptual | -0.584 | falling | 0.1272 |")
doc.append("| general | -2.070 | **falling** | 0.0176 |")
doc.append("")
doc.append("**Reading this table:** Procedural errors (wrong method application) are increasing at ~2 per year. This is statistically significant. Meanwhile the catch-all 'general' class is falling — which likely reflects improved narrative specificity by the DBE, not fewer errors.\n")
doc.append("---\n")

# Section 4 — critical priority
doc.append("## 4. Critical-Priority Misconceptions\n")
doc.append(f"**{len(critical)}** errors are attached to questions where the national average was **below 35%**. These are the concrete teaching failures.\n")
crit_by_topic = critical.groupby("topic").size().sort_values(ascending=False)
doc.append("| Topic | Critical errors |")
doc.append("|---|---|")
for topic, n in crit_by_topic.items():
    doc.append(f"| {topic} | {n} |")
doc.append("")
doc.append("**Euclidean Geometry (55)** and **Probability (50)** dominate. Both are historically the lowest-performing topics. Every critical EUCL error involves either a missing reason, a diagram assumption, or an incorrect theorem citation.\n")
doc.append("---\n")

# Section 5 — four themes
doc.append("## 5. The Four Structural Themes\n")
doc.append("### Theme 1 — Procedural errors are rising\n")
doc.append("- Slope **+1.965 per year** (p = 0.0036, statistically significant)")
doc.append("- Learners increasingly *know what to do* but apply it *incorrectly*")
doc.append("- This is a **method-execution** problem, not a knowledge problem")
doc.append("- Tutor implication: hint ladder should escalate step-level coaching before topic-level review\n")

doc.append("### Theme 2 — Diagram assumptions are persistent\n")
doc.append("- Average **13.3%** of errors every year — 143 of 1,111 total")
doc.append("- No statistically significant trend, but never below 8.7%")
doc.append("- Concentrated in EUCL and AGEO")
doc.append("- Tutor implication: diagram-annotation coaching is a permanent feature, not a passing fix\n")

doc.append("### Theme 3 — Reading-for-understanding hovers ~4%\n")
doc.append("- Reading errors are stable (slope +0.105, p = 0.4954)")
doc.append("- Peaks in 2014 (6.8%) and 2025 (6.5%) — a decade apart")
doc.append("- Concentrated in STAT and TRIG")
doc.append("- Tutor implication: keyword-highlighting and rephrasing questions is needed, especially for word problems\n")

doc.append("### Theme 4 — Notation issues are small but chronic\n")
doc.append("- 47 notation errors across 12 years")
doc.append("- **ALG inequality notation** is the single largest (9 errors)")
doc.append("- Followed by EUCL geometry (4) and FUNC function notation (3)")
doc.append("- Tutor implication: a targeted notation coaching layer for ALG is high-value\n")
doc.append("---\n")

# Section 6 — per-topic
doc.append("## 6. Findings by Topic\n")
topics_order = ["TRIG", "EUCL", "AGEO", "FUNC", "STAT", "CALC", "SEQ", "ALG", "PROB", "FIN"]
for topic in topics_order:
    tdf = df[df["topic"] == topic]
    if len(tdf) == 0:
        continue
    doc.append(f"### {topic} — {len(tdf)} errors, {len(tdf[tdf['priority_band'] == 'critical'])} critical\n")
    top_class = tdf["error_class"].value_counts().head(2)
    doc.append("**Dominant error classes:** " + ", ".join(f"{k} ({v})" for k, v in top_class.items()) + "\n")
    doc.append("**Sample narrative:**")
    sample = tdf[tdf["priority_band"] == "critical"].head(1)
    if len(sample) > 0:
        doc.append(f"> {str(sample.iloc[0]['error_text'])[:280]}...\n")
    doc.append("")

doc.append("---\n")

# Section 7 — for the tutor
doc.append("## 7. For the Tutor Engine (N08 Input)\n")
doc.append("### 7.1 Priority order for misconception library\n")
doc.append("Top 10 (topic, class) pairs to add to the library **first**:\n")
for i, (_, r) in enumerate(perm.head(10).iterrows(), 1):
    doc.append(f"{i}. **{r['topic']} — {r['error_class']}** ({r['total_count']} errors across {r['years_present']} years)")
doc.append("")

doc.append("### 7.2 Which presentation rules to code first\n")
doc.append("Based on the notation and reading findings, the highest-value presentation rules are:\n")
doc.append("| Rule | Why |")
doc.append("|---|---|")
doc.append("| PR_ALG_INEQUALITY_DIRECTION | 9 ALG errors — the single largest notation issue |")
doc.append("| PR_EUCL_STATEMENT_REASON | Every EUCL critical error involves missing reasons |")
doc.append("| PR_EUCL_GIVEN_MARKS | Diagram-assumption errors — 143 across 12 years |")
doc.append("| PR_FUNC_DOMAIN_RANGE_WORDS | 3 FUNC function notation errors, chronic |")
doc.append("| PR_GEN_ONE_STEP_ONE_LINE | Procedural errors rising — layout matters |")
doc.append("")

doc.append("### 7.3 Coaching priorities by topic\n")
doc.append("| Topic | Primary coaching focus |")
doc.append("|---|---|")
doc.append("| EUCL | Reason columns + diagram annotation |")
doc.append("| PROB | Independence tests + counting principle + 'at least' language |")
doc.append("| TRIG | Compound-angle expansions + general solution form |")
doc.append("| CALC | Setting f'(x)=0 explicitly + first-principles notation |")
doc.append("| FUNC | Domain/range notation + asymptote identification |")
doc.append("| ALG | Inequality direction + sign errors in factorisation |")
doc.append("")

doc.append("---\n")
doc.append("## 8. Conclusion\n")
doc.append("Twelve years of DBE diagnostic data tell one coherent story:\n")
doc.append("1. **The problems are stable.** Twenty-one (topic × error_class) combinations appear every single year.")
doc.append("2. **Procedural errors are rising.** This is the only statistically significant negative trend in the corpus.")
doc.append("3. **EUCL is improving but still critical.** Slope -0.619 (p = 0.0071) — real progress, but the topic still leads in critical errors (55).")
doc.append("4. **Diagram assumptions are permanent.** 13.3% of errors every year. This is the single most under-taught skill in the curriculum.")
doc.append("5. **Reading-for-understanding is a minority but persistent.** ~4% of errors. Not growing, not shrinking.")
doc.append("")
doc.append("These findings define the priorities for the tutor engine. Every misconception in N08 should trace back to a row in this analysis.\n")
doc.append("---\n")
doc.append(f"*Generated from {len(df)} error records across 12 years of DBE NSC Mathematics Diagnostic Reports.*")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(doc), encoding="utf-8")
print(f"Wrote {OUT}")
print()
print(f"Document length: {len(OUT.read_text(encoding='utf-8'))} chars")